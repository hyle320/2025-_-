#!/usr/bin/env python3
"""한국청과(가락시장) 당일경매현황(지역별) — 백다다기 오이 산지별 통계.

사용법:
    python hkck_price.py                 # 오늘 (데이터 없으면 어제로 자동 폴백)
    python hkck_price.py 20260929        # 특정 날짜
    python hkck_price.py --source api    # aT OpenAPI(data.go.kr 15141808) 사용
    python hkck_price.py --no-fallback   # 어제 폴백 끄기
    python hkck_price.py --corp tgjungang          # 대구 중앙청과 (API 전용)
    python hkck_price.py --corp tgjungang --corp-cd 22000101   # 코드 직접 지정

실제 페이지 구조 (2026-09 확인):
    - 품목/품종/산지 드롭다운은 없음. 대신
      cmbSearchType(SRH1=품목명, SRH2=품종명, SRH3=산지명) + tbxSearchword(검색어)
      + tbxFromDate(YYYYMMDD) + btnSearch(submit) 방식의 텍스트 검색.
    - AutoPostBack 없음 → 검색은 1회 POST.
    - 결과 GridView(id=..._WebGrid1_wgGV1)는 10행씩 페이징,
      __doPostBack('ctl00$ContentPlaceHolder1$WebGrid1$wgGV1', 'Page$N')으로 넘김.
    - 컬럼: 지역, 품목, 품종, 규격, 등급, 과수크기, 반입량(수량), 경락가(원)
"""
import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry

URL = "https://www.hkck.co.kr/price/today_area.aspx"
P = "ctl00$ContentPlaceHolder1$"
GRID_ID = "ctl00_ContentPlaceHolder1_WebGrid1_wgGV1"
GRID_TARGET = P + "WebGrid1$wgGV1"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

ITEM, VARIETY = "오이", "백다다기"
UNIT_PAT = r"10\s*kg|10\s*키로"
GRADE = "특"
OUT_DIR = Path("./output")


# ─────────────────────────── 한국청과 웹 스크래핑 ───────────────────────────
def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Referer": URL})
    retry = Retry(total=5, backoff_factor=2, allowed_methods=None,
                  status_forcelist=[500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s


def hidden_fields(soup: BeautifulSoup) -> dict:
    """__VIEWSTATE, __VIEWSTATEGENERATOR, __EVENTVALIDATION 등 hidden input 전부."""
    return {i["name"]: i.get("value", "") for i in soup.select("input[type=hidden][name]")}


def parse_grid(soup: BeautifulSoup) -> list[list[str]]:
    table = soup.find(id=GRID_ID)
    if table is None:
        return []
    rows = []
    for tr in table.find_all("tr", recursive=False) or table.find_all("tr"):
        if tr.find("table"):          # 페이저 행(내부에 table) 제외
            continue
        cells = [c.get_text(strip=True) for c in tr.find_all("td")]
        if len(cells) == 8:
            rows.append(cells)
    return rows


def page_numbers(soup: BeautifulSoup) -> set[int]:
    nums = set()
    for a in soup.select(f"#{GRID_ID} a[href*='Page$']"):
        m = re.search(r"Page\$(\d+)", a.get("href", ""))
        if m:
            nums.add(int(m.group(1)))
    return nums


def fetch_hkck(date: str, verbose: bool = True) -> pd.DataFrame:
    s = make_session()
    r = s.get(URL, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    if verbose:
        hf = hidden_fields(soup)
        print("[구조] hidden:", ", ".join(k for k in hf if k.startswith("__")))
        sel = soup.find("select", attrs={"name": P + "cmbSearchType"})
        opts = [(o.get("value"), o.text) for o in sel.find_all("option")] if sel else []
        print("[구조] 검색유형:", opts, "| 조회버튼:", P + "btnSearch")

    search = {P + "cmbSearchType": "SRH2",      # 품종명으로 검색
              P + "tbxSearchword": VARIETY,
              P + "tbxFromDate": date}
    data = {**hidden_fields(soup), **search, P + "btnSearch": "검색"}
    r = s.post(URL, data=data, timeout=60)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    header = ["지역", "품목", "품종", "규격", "등급", "과수크기", "수량", "경락가"]
    rows = parse_grid(soup)
    page = 1
    while (page + 1) in page_numbers(soup):
        page += 1
        data = {**hidden_fields(soup), **search,
                "__EVENTTARGET": GRID_TARGET, "__EVENTARGUMENT": f"Page${page}"}
        r = s.post(URL, data=data, timeout=60)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        rows += parse_grid(soup)
    if verbose:
        print(f"[수집] {date}: {page}페이지, {len(rows)}행")

    df = pd.DataFrame(rows, columns=header)
    for c in ("수량", "경락가"):
        df[c] = pd.to_numeric(df[c].str.replace(",", ""), errors="coerce")
    return df[(df["품목"] == ITEM) & (df["품종"] == VARIETY)].reset_index(drop=True)


# ─────────────────────── 대안: aT 실시간 경매정보 OpenAPI ───────────────────────
API_URL = "https://apis.data.go.kr/B552845/katRealTime2/trades2"
# aT 도매시장/법인 코드. 표준코드 API(data.go.kr 15141818)로 재확인 권장 → 틀리면 --market-cd/--corp-cd로 덮어쓰기.
# 코드가 틀려도 결과가 0건이 되지 않도록, 법인코드 없이 시장 단위로 받은 뒤 법인명(corp_nm)으로도 거른다.
CORPS = {
    "hkck":      {"name": "한국청과",     "market_cd": "110001", "corp_cd": "11000105", "file": "hkck"},       # 서울 가락
    "tgjungang": {"name": "대구중앙청과", "market_cd": "220001", "corp_cd": "22000101", "file": "tgjungang"},  # 대구 북부
}


def fetch_api(date: str, verbose: bool = True, corp: dict = CORPS["hkck"]) -> pd.DataFrame:
    key = os.environ.get("DATA_GO_KR_KEY")
    if not key:
        sys.exit("환경변수 DATA_GO_KR_KEY가 없습니다 (data.go.kr 15141808 활용신청 후 발급).")
    ymd = f"{date[:4]}-{date[4:6]}-{date[6:]}"
    params = {"serviceKey": key, "returnType": "json", "numOfRows": 1000,
              "cond[trd_clcln_ymd::EQ]": ymd,
              "cond[whsl_mrkt_cd::EQ]": corp["market_cd"]}
    s = make_session()
    items, page = [], 1
    while True:
        params["pageNo"] = page
        r = s.get(API_URL, params=params, timeout=60)
        r.raise_for_status()
        body = r.json()["response"]["body"]
        got = body.get("items", {}).get("item", []) or []
        items += got if isinstance(got, list) else [got]
        if page * params["numOfRows"] >= int(body.get("totalCount", 0)) or not got:
            break
        page += 1
    if verbose:
        print(f"[API] {ymd} 시장 {corp['market_cd']} 전체 {len(items)}건")
    raw = pd.DataFrame(items)
    if not raw.empty:
        nm = raw.get("corp_nm", pd.Series("", index=raw.index)).astype(str).str.replace(" ", "")
        raw = raw[(raw.get("corp_cd", "").astype(str) == corp["corp_cd"])
                  | nm.str.contains(corp["name"].replace(" ", ""))]
        if verbose:
            print(f"[API] {corp['name']} {len(raw)}건")
    if raw.empty:
        return pd.DataFrame(columns=["지역", "품목", "품종", "규격", "등급", "수량", "경락가"])
    # 품목코드는 소분류명/법인품종명으로 필터 (코드 체계 변경에 안전)
    vrty = raw.get("corp_gds_vrty_nm", "").astype(str) + raw.get("gds_sclsf_nm", "").astype(str)
    raw = raw[vrty.str.contains(VARIETY)]
    unit = (raw["unit_qty"].astype(str).str.replace(r"\.0+$", "", regex=True)
            + raw["unit_nm"].astype(str) + " " + raw.get("pkg_nm", "").astype(str))
    return pd.DataFrame({
        "지역": raw["plor_nm"], "품목": ITEM, "품종": VARIETY, "규격": unit,
        # API 명세에 등급 필드가 없어 전부 '특'으로 볼 수 없음 → 등급 필터 불가 표시
        "등급": raw.get("grd_nm", pd.Series("미제공", index=raw.index)),
        "수량": pd.to_numeric(raw["qty"], errors="coerce"),
        "경락가": pd.to_numeric(raw["scsbd_prc"], errors="coerce"),
    }).reset_index(drop=True)


# ─────────────────────────────── 통계 ───────────────────────────────
def summarize(df: pd.DataFrame) -> pd.DataFrame:
    def agg(g: pd.DataFrame) -> pd.Series:
        return pd.Series({
            "거래건수": len(g),
            "총수량": g["수량"].sum(),
            "단순평균": g["경락가"].mean(),
            "가중평균": (g["경락가"] * g["수량"]).sum() / g["수량"].sum(),
            "중앙값": g["경락가"].median(),
            "최고가": g["경락가"].max(),
            "최저가": g["경락가"].min(),
        })
    out = (df.groupby("지역").apply(agg, include_groups=False)
             .sort_values("가중평균", ascending=False))
    out.loc["전체"] = agg(df)
    out = out.round(0).astype(int)
    out.index.name = "산지"
    return out.reset_index()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("date", nargs="?", default=datetime.now().strftime("%Y%m%d"), help="YYYYMMDD (기본: 오늘)")
    ap.add_argument("--source", choices=["web", "api"], default="web")
    ap.add_argument("--corp", choices=list(CORPS), default="hkck", help="hkck=가락 한국청과, tgjungang=대구 중앙청과")
    ap.add_argument("--market-cd", help="aT 도매시장코드 덮어쓰기")
    ap.add_argument("--corp-cd", help="aT 법인코드 덮어쓰기")
    ap.add_argument("--no-fallback", action="store_true", help="데이터 없을 때 전날로 넘어가지 않음")
    args = ap.parse_args()

    corp = dict(CORPS[args.corp])
    if args.market_cd:
        corp["market_cd"] = args.market_cd
    if args.corp_cd:
        corp["corp_cd"] = args.corp_cd
    if args.corp != "hkck" and args.source == "web":
        # 대구중앙청과 홈페이지는 자동접속방지(JS 쿠키 챌린지)가 있어 스크래핑하지 않고 API로 조회
        print(f"[안내] {corp['name']}는 웹 스크래핑 미지원 → aT OpenAPI로 조회")
        args.source = "api"
    fetch = fetch_hkck if args.source == "web" else (lambda d: fetch_api(d, corp=corp))
    date = args.date
    try:
        df = fetch(date)
        if df.empty and not args.no_fallback:
            date = (datetime.strptime(date, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
            print(f"[폴백] {args.date} 데이터 없음 → {date}로 재조회")
            df = fetch(date)
    except (requests.RequestException, ValueError, KeyError) as e:
        if args.source == "web":
            sys.exit(f"[실패] {corp['name']} 사이트 접속/파싱 실패: {e}\n"
                     "  대안: DATA_GO_KR_KEY 설정 후  python hkck_price.py --source api")
        raise
    if df.empty:
        sys.exit(f"[결과] {date} {VARIETY} 거래 없음")

    zero = df["경락가"].fillna(0) <= 0      # 경락가 0 = 미낙찰/가격 미확정 → 통계 제외
    if zero.any():
        print(f"[제외] 경락가 0원 {zero.sum()}건")
        df = df[~zero]
    mask = df["규격"].str.contains(UNIT_PAT, case=False, regex=True)
    label = "10kg_특"
    if (df["등급"] == "미제공").all():
        print("[주의] API 응답에 등급 정보가 없어 '특' 필터를 적용하지 않음 (10kg 전체 등급 통계)")
        label = "10kg_전등급"
    else:
        mask &= df["등급"] == GRADE
    sel = df[mask]
    print(f"[필터] {date} 백다다기 {len(df)}건 → {label} {len(sel)}건")
    if sel.empty:
        print("\n단위×등급 분포:")
        print(df.value_counts(["규격", "등급"]).to_string())
        sys.exit(0)

    result = summarize(sel)
    print(f"\n### {corp['name']} 백다다기 {label.replace('_', ' ')} — {date} ({args.source})\n")
    print(result.to_markdown(index=False, floatfmt=",.0f", intfmt=","))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{corp['file']}_백다다기_{label}_{date}.csv"
    result.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"\n저장: {path}")


if __name__ == "__main__":
    main()
