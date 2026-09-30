"""한국청과 백다다기 경매 원자료를 날짜별로 수집해 data/hkck_raw/YYYYMMDD.csv로 캐시.

    python analysis/collect_hkck.py            # 기본 표본(여름·겨울 화/목)
    python analysis/collect_hkck.py 20260105 20260106
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import hkck_price as h  # noqa: E402

RAW = Path(__file__).resolve().parent.parent / "data" / "hkck_raw"
SEASONS = [(date(2025, 7, 1), date(2025, 8, 31)),
           (date(2025, 12, 1), date(2026, 2, 28)),
           (date(2026, 7, 1), date(2026, 8, 31))]


def sample_dates():
    for a, b in SEASONS:
        d = a
        while d <= b:
            if d.weekday() in (1, 3):  # 화, 목
                yield d.strftime("%Y%m%d")
            d += timedelta(days=1)


def one(d: str) -> str:
    out = RAW / f"{d}.csv"
    if out.exists():
        return f"{d} cached"
    df = h.fetch_hkck(d, verbose=False)
    df.to_csv(out, index=False, encoding="utf-8-sig")  # 0건도 빈 파일로 캐시
    return f"{d} {len(df)}"


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    dates = sys.argv[1:] or list(sample_dates())
    print(len(dates), "dates", flush=True)
    with ThreadPoolExecutor(4) as ex:
        futs = {ex.submit(one, d): d for d in dates}
        for f in as_completed(futs):
            try:
                print(f.result(), flush=True)
            except Exception as e:
                print(futs[f], "ERR", e, flush=True)
