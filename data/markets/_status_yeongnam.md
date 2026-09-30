# 영남권 오이(백다다기) 경락 데이터 수집 현황

Target: 61 dates (Tue/Thu; Jul–Aug 2025, Dec 2025–Feb 2026, Jul–Aug 2026). Date counts are S25 / W / S26. Sites with full coverage have 58 dates, because 12/25, 1/1 and one other date were market holidays.

| 시장 | 법인 | 홈페이지 / 수집 소스 | 상태 | granularity | 날짜 (S25/W/S26) | rows | 파일 |
|---|---|---|---|---|---|---|---|
| 대구북부 | 효성청과 | http://www.hyosungcg.com (community/today.htm) | collected | grade_agg | 58 (18/23/17) | 376 | daegu_bukbu__hyosung.csv |
| 대구북부 | 대양청과 | http://dyvaf.co.kr (_new/sub4/sub4-1.php) | collected | grade_agg | 58 (18/23/17) | 467 | daegu_bukbu__daeyang.csv |
| 대구북부 | 대구중앙청과 | http://www.tgjungang.co.kr | blocked: JS cookie challenge (not bypassed) | - | - | 0 | - |
| 대구북부 | 대구농산 | (site behind JS cookie challenge) | blocked: JS cookie challenge (not bypassed) | - | - | 0 | - |
| 대구북부 | 농협북대구공판장 / 대구경북원예농협공판장 | newgp.nonghyup.com (NH platform); dafco.or.kr ClipReport | not collected: the NH site is a JS platform; DAFCO's report is a ClipReport viewer and resets connections | - | - | 0 | - |
| 부산엄궁 | 부산청과(주) | http://www.busanfruit.co.kr/page/market_price.php (GET) | collected | trade (with 출하지 and 수량; no 등급) | 53 (18/18/17) | 820 | busan_eomgung__busan_cg.csv |
| 부산엄궁 | 항도청과(주) | http://www.hangdoi.co.kr/s04_/sub3.asp | collected (only rows labeled 다다기오이) | grade_agg (lot level) | 28 (18/0/10) | 109 | busan_eomgung__hangdo_cg.csv |
| 부산엄궁 | 농협부산공판장 | busan.go.kr/market/mktdistributioninfo020101 | no-data: the city portal keeps only the last few days | - | - | 0 | - |
| 부산반여 | 동부청과(주) | http://www.dongbufnv.com/customer_/customer03.asp | collected | grade_agg (lot level) | 58 (18/23/17) | 338 | busan_banyeo__dongbu.csv |
| 부산반여 | 부산중앙청과(주) | http://bjfnv.com | blocked: HTTP 500 server error on every page | - | - | 0 | - |
| 부산반여 | 농협반여공판장 | busan.go.kr/market/mktdistributioninfo020102 | no-data: the city portal keeps only the last few days | - | - | 0 | - |
| 울산 | 울산원예농협 공판장 | ulsan.go.kr/s/market/func/ea/list.ulsan?mId=001005001000000000 | collected | trade (수량) | 45 (16/12/17) | 382 | ulsan__ulsan_wonye_nh.csv |
| 울산 | 울산중앙청과시장(주) | http://www.ulsanjungang.co.kr (data from the city portal) | collected | trade (수량) | 38 (17/5/16) | 224 | ulsan__ulsan_jungang.csv |
| 창원팔용 | (주)창원청과시장 | http://www.changwonfvc.co.kr; changwon.go.kr/market/00011/00033/00034.web | collected | grade_agg | 46 (16/18/12) | 104 | changwon_palyong__changwon_cg.csv |
| 창원팔용 | 농협창원공판장 | changwon.go.kr (same page) | collected | grade_agg | 44 (10/18/16) | 57 | changwon_palyong__nh_changwon.csv |
| 창원내서 | 마산청과시장(주) | changwon.go.kr (marketType=ns) | collected (thin) | grade_agg | 7 (0/0/7) | 16 | changwon_naeseo__masan_cg.csv |
| 창원내서 | 창원원협 | changwon.go.kr (marketType=ns) | no-data: the portal has no records for any item | - | - | 0 | (empty csv) |
| 진주 | 진주원예농협 공판장 ("농협공판장") | market.jinju.go.kr/sub4/sub1.asp | collected | trade (수량) | 47 (17/13/17) | 467 | jinju__nh_gongpanjang.csv |
| 진주 | 진주중앙청과(주) | market.jinju.go.kr (same) | collected (thin) | trade | 10 (3/0/7) | 21 | jinju__jungang_cg.csv |
| 포항 | 포항농협 | market.pohang.go.kr/bbs/board.php?bo_table=menu03_01 | collected | trade (수량) | 29 (17/2/10) | 132 | pohang__pohang_nh.csv |
| 포항 | 포항청과(주) / 대경사과원예농협 | same | no-data: no 백다다기 rows on any target date | - | - | 0 | - |
| 안동 | 안동청과(합자) / 안동농협(공) / (주)경북청과 | andongff.com, adnacf.co.kr (daily 시세표 posts, fruit only); andong.go.kr/market price01.do | collected at market level only (the city portal has no 법인 split; the realtime page keeps about 1 day) | grade_agg | 6 (1/0/5) | 17 | andong__market_all.csv |
| 구미 | 구미농협공판장 | gumi.go.kr/market/auction/auction.asp | collected | trade (수량) | 39 (18/4/17) | 294 | gumi__nh_gongpanjang.csv |
| 구미 | 구미중앙청과(주) | same | collected | trade (수량) | 36 (16/15/5) | 130 | gumi__gumi_jungang_cg.csv |

## Notes
- **Variety names:** the labels differ by site but all mean 백다다기. 대양 uses 다다기; 항도 uses 다다기오이, and its plain "오이" label appears to be 취청 because a 취청 search returns those rows, so it was excluded. 구미 and 포항 use 오이(백다다기); the others use 백다다기.
- **Unit strings:** each site formats the unit differently: 10.000kg상자 (효성), 10KG상자 (대양), 10.0kg (창원), 10.0kg 상자 (안동), 10kg (the rest). Some rows are 11, 12, 15, 18 or 20 kg boxes; 농협창원 mostly uses 11kg.
- **동부 and 항도 rows:** these show several rows per grade per day (lot or shipper level min/max/avg). They are labelled grade_agg.
- **부산청과:** qty is the box count; the site also shows 거래량 in kg. 산지 is filled on every row.
- **Duplicates in trade files:** identical rows (same price and qty) are real separate trades and were kept.
- **Winter gaps:** many 영남 sites trade little 백다다기 in winter, for example 항도 (0 winter dates), 포항 and 구미NH. Keep this in mind when comparing seasons.
- **Proxy resets:** busan.go.kr, ulsan.go.kr, changwon.go.kr, andong.go.kr and dafco.or.kr often reset connections from the proxy IP. Retries with backoff got through, except the DAFCO report viewer.
