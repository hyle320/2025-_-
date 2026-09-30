"""주산지 효과 검증 — 한국청과(가락) 백다다기 경매 원자료(data/hkck_raw/*.csv).

질문
  A. 같은 날·같은 규격·같은 등급 안에서, 주산지 물건이 비주산지보다 비싸게 낙찰되는가? (주산지 프리미엄)
  B. 그날 주산지 반입 비중이 높을수록 비주산지의 상대가격이 더 떨어지는가? (주산지 물량 압박)
  C. 경남(진주 등) 물건은 계절별로 어떤 상대가격을 받는가?

상대가격 rel = log(개별 경락가 / 같은 날·규격·등급 셀의 수량가중평균). 0이면 셀 평균, +0.05 ≈ +5%.

    python analysis/origin_effect.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "hkck_raw"
OUT = ROOT / "output" / "analysis"
MAIN_CUM = 0.5  # 계절 누적 물량 50%를 채우는 상위 산지를 주산지로 정의


def season_of(d: pd.Timestamp) -> str:
    if d.month in (7, 8):
        return f"{d.year} 여름"
    y = d.year if d.month == 12 else d.year - 1
    return f"{y}/{str(y + 1)[2:]} 겨울"


def load() -> pd.DataFrame:
    frames = []
    for f in sorted(RAW.glob("*.csv")):
        df = pd.read_csv(f, dtype={"과수크기": str})
        if df.empty:
            continue
        df["날짜"] = pd.to_datetime(f.stem)
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df = df[(df["경락가"] > 0) & (df["수량"] > 0)].copy()
    df["시즌"] = df["날짜"].map(season_of)
    df["계절"] = np.where(df["날짜"].dt.month.isin([7, 8]), "여름", "겨울")
    df["도"] = df["지역"].str.split().str[0]
    df["셀"] = df["날짜"].dt.strftime("%Y%m%d") + "|" + df["규격"] + "|" + df["등급"]
    g = df.groupby("셀")
    cell_wavg = g.apply(lambda x: np.average(x["경락가"], weights=x["수량"]), include_groups=False)
    df["셀평균"] = df["셀"].map(cell_wavg)
    df["셀산지수"] = df["셀"].map(g["지역"].nunique())
    df["rel"] = np.log(df["경락가"] / df["셀평균"])
    return df


def mark_main(df: pd.DataFrame) -> pd.DataFrame:
    """시즌별 물량 순위로 주산지 지정."""
    share = (df.groupby(["시즌", "지역"])["수량"].sum()
               .groupby(level=0, group_keys=False).apply(lambda s: s.sort_values(ascending=False) / s.sum()))
    cum = share.groupby(level=0).cumsum()
    main = cum[(cum - share) < MAIN_CUM].index  # 누적 50%에 도달하는 산지까지 포함
    df["주산지"] = df.set_index(["시즌", "지역"]).index.isin(main).astype(int)
    df["시즌점유율"] = df.set_index(["시즌", "지역"]).index.map(share)
    return df


def origin_table(df: pd.DataFrame, season: str, top: int = 12) -> pd.DataFrame:
    d = df[df["시즌"] == season]
    t = d.groupby("지역").apply(lambda x: pd.Series({
        "물량점유율%": 100 * x["수량"].sum() / d["수량"].sum(),
        "반입일수": x["날짜"].nunique(),
        "거래건수": len(x),
        "상대가격%": 100 * (np.exp(np.average(x["rel"], weights=x["수량"])) - 1),
        "주산지": "●" if x["주산지"].iat[0] else "",
    }), include_groups=False).sort_values("물량점유율%", ascending=False)
    return t.head(top).round(1)


def test_premium(df: pd.DataFrame) -> pd.DataFrame:
    """A. 셀 내 주산지 프리미엄 (산지 2곳 이상 경합한 셀만). 수량 가중 WLS, 날짜 클러스터 SE."""
    rows = []
    d0 = df[df["셀산지수"] >= 2]
    for key, d in [("전체", d0)] + list(d0.groupby("시즌")):
        m = smf.wls("rel ~ 주산지", data=d, weights=d["수량"]).fit(
            cov_type="cluster", cov_kwds={"groups": d["날짜"].dt.strftime("%Y%m%d").astype("category").cat.codes})
        b, (lo, hi) = m.params["주산지"], m.conf_int().loc["주산지"]
        rows.append({"시즌": key, "주산지 프리미엄%": 100 * (np.exp(b) - 1),
                     "95%CI": f"{100*(np.exp(lo)-1):+.1f} ~ {100*(np.exp(hi)-1):+.1f}",
                     "p값": m.pvalues["주산지"], "거래건수": len(d), "일수": d["날짜"].nunique()})
    return pd.DataFrame(rows).round(3)


def test_pressure(df: pd.DataFrame) -> pd.DataFrame:
    """B. 일별: 주산지 반입비중↑ → 비주산지 상대가격↓ ?"""
    daily = df.groupby(["시즌", "날짜"]).apply(lambda x: pd.Series({
        "주산지비중": x.loc[x["주산지"] == 1, "수량"].sum() / x["수량"].sum(),
        "총반입": x["수량"].sum(),
        "비주산지rel": np.average(x.loc[x["주산지"] == 0, "rel"], weights=x.loc[x["주산지"] == 0, "수량"])
                       if (x["주산지"] == 0).any() else np.nan,
    }), include_groups=False).dropna().reset_index()
    rows = []
    for key, d in [("전체", daily)] + list(daily.groupby("시즌")):
        f = "비주산지rel ~ 주산지비중" + (" + C(시즌)" if key == "전체" else "")
        m = smf.ols(f, data=d).fit(cov_type="HC1")
        rows.append({"시즌": key, "주산지비중 +10%p당 비주산지 상대가격%": 100 * (np.exp(m.params["주산지비중"] * 0.1) - 1),
                     "p값": m.pvalues["주산지비중"], "일수": len(d)})
    return pd.DataFrame(rows).round(3)


def test_share_rank(df: pd.DataFrame, min_trades: int = 30) -> pd.DataFrame:
    """A2. 산지 단위: 시즌 물량점유율이 클수록 상대가격이 높은가? (스피어만 순위상관)"""
    from scipy.stats import spearmanr
    rows = []
    for s, d in df.groupby("시즌"):
        t = d.groupby("지역").apply(lambda x: pd.Series({
            "share": x["수량"].sum() / d["수량"].sum(), "n": len(x),
            "rel": np.average(x["rel"], weights=x["수량"])}), include_groups=False)
        t = t[t["n"] >= min_trades]
        rho, p = spearmanr(t["share"], t["rel"])
        rows.append({"시즌": s, "산지수": len(t), "순위상관 rho": rho, "p값": p})
    return pd.DataFrame(rows).round(3)


def region_table(df: pd.DataFrame, pattern: str = "경남") -> pd.DataFrame:
    d = df[df["지역"].str.contains(pattern)]
    if d.empty:
        return pd.DataFrame({"안내": [f"{pattern} 산지 거래 없음"]})
    return d.groupby(["시즌", "지역"]).apply(lambda x: pd.Series({
        "거래건수": len(x), "총수량": x["수량"].sum(), "반입일수": x["날짜"].nunique(),
        "상대가격%": 100 * (np.exp(np.average(x["rel"], weights=x["수량"])) - 1),
        "10kg특 가중평균": np.average(x.loc[x["셀"].str.contains("10kg.*\\|특$"), "경락가"],
                                   weights=x.loc[x["셀"].str.contains("10kg.*\\|특$"), "수량"])
                          if x["셀"].str.contains("10kg.*\\|특$").any() else np.nan,
    }), include_groups=False).round(1)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = mark_main(load())
    df.to_csv(OUT / "hkck_rows_with_rel.csv", index=False, encoding="utf-8-sig")
    md = lambda t, **k: t.to_markdown(**k, floatfmt=",.3g")  # noqa: E731
    print(f"표본: {df['날짜'].nunique()}일, {len(df):,}건, 시즌 {sorted(df['시즌'].unique())}\n")
    print("규격×계절 거래건수\n" + md(pd.crosstab(df["규격"], df["계절"])) + "\n")
    for s in sorted(df["시즌"].unique()):
        t = origin_table(df, s)
        t.to_csv(OUT / f"origin_{s.replace('/', '-').replace(' ', '_')}.csv", encoding="utf-8-sig")
        print(f"### {s} 산지별 (주산지=누적물량 {int(MAIN_CUM*100)}%)\n" + md(t) + "\n")
    a, a2, b, c = test_premium(df), test_share_rank(df), test_pressure(df), region_table(df)
    for name, t in [("A_premium", a), ("A2_share_rank", a2), ("B_pressure", b), ("C_gyeongnam", c)]:
        t.to_csv(OUT / f"{name}.csv", encoding="utf-8-sig")
    print("### A. 주산지 프리미엄 (같은 날·규격·등급 내)\n" + md(a, index=False) + "\n")
    print("### A2. 산지 물량점유율 vs 상대가격 순위상관 (거래 30건 이상 산지)\n" + md(a2, index=False) + "\n")
    print("### B. 주산지 물량 압박 (일별)\n" + md(b, index=False) + "\n")
    print("### C. 경남 산지\n" + md(c) + "\n")


if __name__ == "__main__":
    main()
