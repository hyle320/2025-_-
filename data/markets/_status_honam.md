# 호남·충청권 status (오이 백다다기) — collected 2026-09-30

| Market | 법인 | Homepage | Status | Granularity | Dates (of 61) | Rows |
|---|---|---|---|---|---|---|
| 광주각화 | 광주청과 | http://www.kjcg.co.kr (시세: http://59.0.116.141/KJCG_Web/Service/Danga_List02.aspx) | collected | grade_agg (규격×등급 min/max/avg, no qty) | 58 | 197 |
| 광주각화 | 광주중앙청과 | https://www.ejoongang.co.kr (SuccessfulBid.aspx / MarketPrice.aspx) | collected | trade (낙찰가 only; no 산지/qty/grade) + grade_agg per weight | 58 | 7919 (7739 trade + 180 agg) |
| 광주각화 | 광주원예농협 공판장 | https://wonhyup.nonghyup.com → newgp.nonghyup.com | blocked: old JSP pages redirect; new platform is an SPA with client-side encrypted query params (not reverse-engineered) | – | 0 | 0 |
| 광주서부 | 호남청과 | http://khonam.co.kr (/distri/?p_url=distri_3) | collected | grade_agg (per weight only, no grade) | 54 | 65 |
| 광주서부 | (market site) | https://seobu-market.gwangju.go.kr | blocked: connection reset (geo-IP) | – | – | – |
| 전주 | 전주청과 / 전주원예농협 공판장 | market.jeonju.go.kr; jeonjuwon.nonghyup.com | blocked: market site DNS/proxy connect failure; 원협 → newgp (see above) | – | 0 | 0 |
| 익산 | 익산원예농협 공판장 / (자)이리청과 | https://market.iksan.go.kr | blocked: HTTP 502 via proxy; no corp homepages found; 원협 → newgp | – | 0 | 0 |
| 정읍 | 정일청과 / 정읍원예농협 공판장 | www.jeongeup.go.kr (no corp sites found) | not-found (corp sites); city site reset/503 | – | 0 | 0 |
| 순천 | 순천남도청과 | https://market.sc.go.kr/sub4/sub1.aspx (market site, per corp) | collected | trade (경락가, qty, grade; no 산지) | 10 | 23 |
| 순천 | 순천원예농협 | same | collected | trade | 51 | 336 |
| 순천 | 남일청과 | same | no-data (no 오이 rows on any date) | – | 0 | 0 |
| 대전오정 | 대전청과 | https://www.djcg.co.kr (/new_api/api/prices) | collected (history only from ~2026-05/06) | grade_agg per weight (+qty) | 17 (Jul–Aug 2026 only) | 42 |
| 대전오정 | 농협대전공판장 | newgp.nonghyup.com | blocked (newgp, see above) | – | 0 | 0 |
| 대전노은 | 대전중앙청과 | https://tjc.co.kr (/prg/real.prg) | collected | grade_agg per weight (+qty) | 58 | 177 |
| 대전노은 | 대전원예농협 노은공판장 | https://tjwy.nonghyup.com → newgp | blocked (newgp) | – | 0 | 0 |
| 대전 (both) | city 경락정보 (all corps, per-trade+산지) | daejeon.go.kr/noe, /ohj NoeFrmprdPriceList.do | no-data: today only, date params ignored | trade | 0 | 0 |
| 청주 | 청주청과시장 | http://www.cjcg.co.kr (/notice/vege_list.html) | collected | trade WITH 산지 + qty + grade | 49 | 1217 |
| 청주 | 충북원예농협 공판장 | cheongju.go.kr/market (reset); newgp | blocked | – | 0 | 0 |
| 천안 | 천안청과 | http://www.cack.co.kr (/s04_/sub3.asp) | no-data: shows only today (date params ignored); labels 오이(다다기) | grade_agg | 0 | 0 |
| 천안 | 천안농협 공판장 | newgp; cheonan.go.kr/market | blocked (newgp; city site intermittent reset) | – | 0 | 0 |
| 충주 | 충주중원청과 / 충북원협 충주 | chungju.go.kr/market (no corp homepage found; blog only) | no-data: realtime-only page, its market_api.jsp returns 500 | – | 0 | 0 |

Notes
- at.agromarket.kr returns 406 (WAF) -> not used. nongnet.or.kr is reachable (national aggregates by market) — possible fallback, not used.
- 광주청과 site carries forward the last trading day's table on holidays: 20260101, 20260217, 20260219 were dropped as stale.
- 청주청과 has a raw 과수 column (e.g. "50", "50-2", "오이지") kept inside unit as "(과수:x)"; grade values include 특/상/대/중/특상/왕특 etc.
- 순천 trades almost all 취청 (전남 local variety); 백다다기 is thin. 10 exact-duplicate rows (paging overlap) removed.
- 광주중앙청과 trade rows have no grade/qty; units mix 10/18/21kg 박스, 팰릿, 8kg 비닐봉지 — filter unit for 10kg 박스.
- Missing dates are mostly holidays (20260101, 설 20260217/19) or days with no 백다다기 trades (청주/순천 winter).
