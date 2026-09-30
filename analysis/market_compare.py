"""전국 경매장 비교 — 백다다기 10kg 특, 여름(7~8월) vs 겨울(12~2월).

입력: data/markets/<market>__<corp>.csv (공통 스키마)
  market,corp,date,item,variety,unit,grade,origin,qty,price,price_min,price_max,price_avg,granularity

지표 (법인 × 계절)
  일평균가      : 날짜별 대표가(거래단위는 수량가중평균, 집계형은 평균가)의 평균
  한국청과대비% : 같은 날 가락 한국청과 10kg 특 가중평균 대비 (날짜 효과 제거)
  변동성%      : 한국청과 대비 비율의 일별 표준편차 (클수록 들쭉날쭉)
  일평균반입    : 10kg 특 일평균 상자수 (거래단위 자료만)
  1위산지점유% : 주산지 집중도 (거래단위 자료만)
  경남산상대%  : 같은 날·규격·등급 셀 평균 대비 경남산 가격 (거래단위 자료만)
  추정순수취    : 일평균가 × (1-상장수수료) - 하차비 - 운송비(진주 기준 거리 추정)

    python analysis/market_compare.py
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "markets"
OUT = ROOT / "output" / "market_compare"

UNIT_PAT = re.compile(r"(?:^|[^0-9.])10(?:\.0+)?\s*(?:kg|키로)", re.I)
BENCH = ("서울가락", "한국청과")

# ── 비용 가정 (컨설팅 현장값으로 바꿔 쓰기) ──
COMMISSION = 0.07        # 상장수수료 (법정 상한 7%)
UNLOAD = 150             # 하차·하역비 원/상자
FREIGHT_BASE, FREIGHT_PER_KM = 200, 1.5   # 운송비 원/상자 ≈ 200 + 1.5×km (5톤 차 기준 대략치)
# 진주 → 시장 도로거리(km, 대략치)
DIST = {"가락": 335, "강서": 360, "구리": 350, "인천": 380, "구월": 380, "삼산": 385, "수원": 320,
        "안양": 330, "안산": 340, "원주": 330, "춘천": 400, "강릉": 420, "대구": 130, "엄궁": 95,
        "반여": 110, "부산": 100, "울산": 150, "팔용": 70, "창원": 70, "내서": 60, "마산": 60, "진주": 5,
        "포항": 200, "안동": 230, "구미": 170, "광주": 170, "각화": 170, "순천": 100, "전주": 190,
        "익산": 210, "정읍": 210, "대전": 200, "오정": 200, "노은": 200, "청주": 240, "천안": 270, "충주": 280}


def dist_of(market: str) -> float:
    for k, v in DIST.items():
        if k in market:
            return v
    return np.nan


def season(d: pd.Timestamp) -> str | None:
    return "여름" if d.month in (7, 8) else "겨울" if d.month in (12, 1, 2) else None


def load() -> pd.DataFrame:
    frames = [pd.read_csv(f, dtype=str) for f in sorted(SRC.glob("*__*.csv")) if f.stat().st_size > 200]
    df = pd.concat(frames, ignore_index=True)
    for c in ("qty", "price", "price_min", "price_max", "price_avg"):
        df[c] = pd.to_numeric(df[c].str.replace(",", ""), errors="coerce")
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce")
    df["계절"] = df["date"].map(season)
    unit = df["unit"].fillna("")
    kg = pd.to_numeric(unit.str.extract(r"(\d+(?:\.\d+)?)\s*(?:kg|키로)", flags=re.I)[0], errors="coerce")
    ok_unit = (kg == 10) & ~unit.str.contains(r"-P\b|비닐|망", case=False)   # 춘천 '10Kg-P' 등 이형 포장 제외
    grade = df["grade"].fillna("").str.strip()
    df["등급구분"] = np.where(grade.eq("") | grade.isin(["-", "nan"]), "미구분", "특")
    ok_grade = grade.str.match(r"^특(\(|$|1|등)") | (df["등급구분"] == "미구분")
    df = df[ok_unit & ok_grade & df["계절"].notna()].copy()
    df["p"] = df["price"].where(df["granularity"] == "trade", df["price_avg"])
    return df[df["p"] > 0]


def daily(df: pd.DataFrame) -> pd.DataFrame:
    def rep(x):
        if (x["granularity"] == "trade").all() and x["qty"].notna().all():
            return pd.Series({"p": np.average(x["p"], weights=x["qty"]), "qty": x["qty"].sum()})
        return pd.Series({"p": x["p"].mean(), "qty": np.nan})
    return df.groupby(["market", "corp", "등급구분", "계절", "date"]).apply(rep, include_groups=False).reset_index()


def origin_stats(df: pd.DataFrame) -> pd.DataFrame:
    t = df[(df["granularity"] == "trade") & df["origin"].notna() & df["qty"].notna()].copy()
    if t.empty:
        return pd.DataFrame()
    t["cell"] = t["date"].astype(str) + t["unit"] + t["grade"]
    t["cellavg"] = t.groupby(["market", "corp", "cell"])["p"].transform(
        lambda s: np.average(s, weights=t.loc[s.index, "qty"]))
    t["rel"] = np.log(t["p"] / t["cellavg"])
    rows = []
    for (m, c, s), x in t.groupby(["market", "corp", "계절"]):
        sh = x.groupby("origin")["qty"].sum().sort_values(ascending=False) / x["qty"].sum()
        g = x[x["origin"].str.contains("경남|경상남")]
        rows.append({"market": m, "corp": c, "계절": s, "1위산지": sh.index[0], "1위산지점유%": 100 * sh.iloc[0],
                     "경남산점유%": 100 * g["qty"].sum() / x["qty"].sum(),
                     "경남산상대%": 100 * (np.exp(np.average(g["rel"], weights=g["qty"])) - 1) if len(g) else np.nan})
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = load()
    d = daily(df)
    bench = d[(d["market"] == BENCH[0]) & (d["corp"] == BENCH[1])].set_index("date")["p"]
    d["ratio"] = np.log(d["p"] / d["date"].map(bench))
    s = d.groupby(["market", "corp", "등급구분", "계절"]).agg(
        일수=("date", "nunique"), 일평균가=("p", "mean"), 중앙값=("p", "median"),
        한국청과대비=("ratio", "mean"), 변동성=("ratio", "std"), 일평균반입=("qty", "mean")).reset_index()
    s["한국청과대비%"] = 100 * (np.exp(s.pop("한국청과대비")) - 1)
    s["변동성%"] = 100 * s.pop("변동성")
    s["신뢰"] = np.where(s["일수"] >= 8, "", "표본적음")
    s["거리km"] = s["market"].map(dist_of)
    s["추정순수취"] = s["일평균가"] * (1 - COMMISSION) - UNLOAD - (FREIGHT_BASE + FREIGHT_PER_KM * s["거리km"])
    o = origin_stats(df)
    if not o.empty:
        s = s.merge(o, on=["market", "corp", "계절"], how="left")
    s = s.sort_values(["계절", "추정순수취"], ascending=[False, False])
    s.to_csv(OUT / "market_compare.csv", index=False, encoding="utf-8-sig")
    for k, g in s.groupby("계절", sort=False):
        print(f"### {k} — 백다다기 10kg 특 (추정순수취 순)\n")
        print(g.drop(columns="계절").to_markdown(index=False, floatfmt=",.0f") + "\n")
    print(f"비용가정: 수수료 {COMMISSION:.0%}, 하차 {UNLOAD}원, 운송 {FREIGHT_BASE}+{FREIGHT_PER_KM}×km 원/상자")


if __name__ == "__main__":
    main()
