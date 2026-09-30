# 수도권·강원 (가락 한국청과 제외) — 오이 백다다기 수집 현황

수집일 2026-09-30. 대상 날짜: `_dates.txt`의 61일 (여름 36일 / 겨울 25일). S/W = 데이터가 있는 여름/겨울 날짜 수.

| 시장 | 법인 | 홈페이지 | 상태 | 단위 | 수집 날짜 수 | 행 수 | 파일 |
|---|---|---|---|---|---|---|---|
| 서울가락 | 서울청과 | http://www.sfvc.co.kr | 차단: 503 upstream 연결 시간초과 (2회 재시도) | – | 0 | 0 | – |
| 서울가락 | 중앙청과 | https://www.ejoongang.co.kr | 수집 완료 | grade_agg (중량별 최저/최고/평균, 등급 없음) | 58 (S35 W23) | 180 | garak__jungang.csv |
| 서울가락 | 동화청과 | http://www.donghwafp.com | 수집 완료 (최근 8일만 제공) | trade (산지·수량 없음) | 5 (2026-09-23~30, 대상 날짜 밖) | 920 | garak__donghwa.csv |
| 서울가락 | 대아청과 | http://www.dagreen.co.kr | 데이터 없음: 무·배추·파·양배추·옥수수만 취급 (2025-08-05, 2026-01-15 전체 페이지 확인) | – | 0 | 0 | – |
| 서울가락 | 농협가락공판장 | https://newgp.nonghyup.com | 차단: SPA, CSRF에서 파생한 AES 암호화 API 페이로드 | – | 0 | 0 | – |
| 서울가락 | (공사 garak.co.kr 법인별 BI) | https://www.garak.co.kr/youtong | 차단: 데이터 iframe db.garak.co.kr:9443 연결 리셋 (해외 IP) | – | – | – | – |
| 서울강서 | 서부청과 | http://www.sbbot.com | 수집 완료 | grade_agg | 58 (S35 W23) | 650 | gangseo__seobu.csv |
| 서울강서 | 강서청과 | http://www.ksfresh.kr | 차단: http 연결 리셋, https 인증서 오류 | – | 0 | 0 | – |
| 서울강서 | 농협강서공판장 | https://newgp.nonghyup.com | 차단: AES 암호화 API | – | 0 | 0 | – |
| 구리 | 구리청과 | http://www.kurifnv.com (시세 페이지 없음) → 구리농수산물공사 gamaco.co.kr 실시간 경락 | 수집 완료 | trade + 산지 + 수량 | 50 (S35 W15) | 4124 | guri__guricheonggwa.csv |
| 구리 | 인터넷청과 | https://corp.gamaco.co.kr/introduce/internetChungHome/main → gamaco.co.kr | 수집 완료 | trade + 산지 + 수량 | 54 (S35 W19) | 6816 | guri__internet.csv |
| 구리 | 농협구리공판장 | gamaco.co.kr | 수집 완료 | trade + 산지 + 수량 | 44 (S35 W9) | 1599 | guri__nh.csv |
| 인천 남촌 (구 구월) | 인천농산물 | http://www.innong.co.kr | 수집 완료 | grade_agg + 수량 | 58 (S35 W23) | 111 | incheon_namchon__innong.csv |
| 인천 남촌 | 덕풍청과 | http://www.deokpung.co.kr | 수집 완료 | trade (산지·수량 없음) | 38 (S35 W3) | 662 | incheon_namchon__deokpung.csv |
| 인천 남촌 | 대인농산 | http://www.daeinnongsan.co.kr | 데이터 없음: 시세 게시판이 2024-07-16에 멈춤, 비밀글 | – | 0 | 0 | – |
| 인천 남촌 | 인천원예농협 남촌공판장 | newgp.nonghyup.com | 차단: AES 암호화 API | – | 0 | 0 | – |
| 인천 삼산 | 경인농산 | http://www.kyoung-in.co.kr | 차단: "자동등록방지" 봇 검사 | – | 0 | 0 | – |
| 인천 삼산 | 부평농산 | http://www.bpnongsan.co.kr | 차단: "자동등록방지" 봇 검사 | – | 0 | 0 | – |
| 인천 삼산 | 인천원협 삼산공판장 | newgp.nonghyup.com | 차단: AES 암호화 API | – | 0 | 0 | – |
| 수원 | 경기청과 | http://www.kyunggi.me (/s03/2.asp) | 데이터 없음: 시세 조회가 어떤 품목·날짜에도 빈 결과, 엑셀은 HTTP 500 | – | 0 | 0 | – |
| 수원 | 수원청과물 | http://www.sucheong.co.kr | 차단: 403 Forbidden | – | 0 | 0 | – |
| 수원 | 수원원예농협(공) | http://suwonwonye.nonghyup.com → newgp | 차단: AES 암호화 API | – | 0 | 0 | – |
| 안양 | 안양농산물 | 찾지 못함 (시청 market.anyang.go.kr 연결 리셋) | 찾지 못함 | – | 0 | 0 | – |
| 안양 | 안양원예농협 공판장 | https://aywy.nonghyup.com:8100 → newgp | 차단: AES 암호화 API | – | 0 | 0 | – |
| 안산 | 안산농산물 | http://www.ansanfnv.co.kr | 수집 완료 | grade_agg | 35 (S30 W5) | 139 | ansan__ansannongsan.csv |
| 안산 | 농협안산공판장 | newgp.nonghyup.com | 차단: AES 암호화 API | – | 0 | 0 | – |
| 원주 | 합동청과 | http://www.xn--vb0b43k2pxr5h.com (합동청과.com) | 수집 완료 | trade + 수량 (산지 없음) | 58 (S35 W23) | 761 | wonju__hapdong.csv |
| 원주 | 원주원예농협 | https://wjhanaro.nonghyup.com → newgp | 차단: AES 암호화 API | – | 0 | 0 | – |
| 춘천 | 춘천중앙청과 | http://cjungang.co.kr | 수집 완료 | grade_agg | 57 (S35 W22) | 67 | chuncheon__chuncheon_jungang.csv |
| 강릉 | (주)강릉농산물도매시장 | http://www.gnns.co.kr | 수집 완료 (품종명 "백오이") | grade_agg | 47 (S35 W12) | 241 | gangneung__gangneung_nongsan.csv |

특이사항
- 시청·공사 사이트 다수(incheon.go.kr/sm, suwon.go.kr, anyang.go.kr, ansan.go.kr, db.garak.co.kr)가 해외 IP 연결을 리셋함. aT 통합홈페이지 at.agromarket.kr은 WAF가 406을 반환함. 농협 공판장은 모두 newgp.nonghyup.com 한 곳을 거치며, 이 사이트의 요청은 암호화되어 있어 우회하지 않음.
- 구리 사이트 gamaco.co.kr의 `/realTime/realTimeAuction/realTimeAuctionAjax`(POST searchDate)는 과거 날짜의 3개 법인 건별 경락 전체를 산지 포함해 JSON으로 반환함. 이 지역에서 가장 좋은 데이터 소스임.
- 동화청과는 AuctionDate가 조회 가능 범위(최근 8일)를 벗어나면 조용히 오늘 날짜로 대체함. 날짜가 적용된 것처럼 보이지만 아님. 그래서 최근 며칠만 수집했음.
- 춘천중앙청과 "10Kg-P" 가격(겨울 평균 5만~9.5만 원)은 다른 시장 10kg 가격의 2~3배임. "-P"는 표준 10kg 상자와 다른 포장 단위일 가능성이 있으니 확인 필요. 이 사이트 결과표 첫 행은 고정된 "사과 후지" 샘플 행이어서 제외함.
- 강릉은 백다다기를 "백오이"로 표기함(원래 표기 그대로 유지).
- 덕풍청과는 겨울 날짜 대부분에 다다기 거래가 없음(W3). 안산(W5), 구리 농협(W9)도 겨울 물량이 적음.
- 대상 날짜 중 2026-01-01, 2026-02-17(설), 2025-12-25(일부 시장)는 휴장이라 데이터 없음.
