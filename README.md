<p align="center"><a href="https://jinawinwin.github.io/SEC_Apple/"><img src="assets/apple-dashboard-icon.png" width="90" alt="Apple 대시보드 바로가기 아이콘"></a><br><a href="https://jinawinwin.github.io/SEC_Apple/"><strong>🔗 대시보드 바로가기</strong></a></p>

# Apple Inc. SEC 재무 분석

Apple의 SEC 공시를 이용해 재무 성과를 확인하는 대시보드입니다.

- 상단: 매출·순이익 추이, 현금흐름 차트와 주요 KPI
- 하단: Annual, Half-year, Quarterly 수치 테이블
- 우측 플로팅 메뉴: 대시보드 PDF 저장, 기간별 Excel 다운로드
- 분석: 전년 대비 매출·순이익 성장률, 매출총이익률·영업이익률·순이익률, 잉여현금흐름률, 현금전환율, 자본적지출률, 부채/자산 및 현금/부채 비율
- 국내 Peer Firms: 삼성전자, LG전자

## 자동 업데이트

GitHub Actions가 매월 1일 00:00 UTC에 SEC Company Facts API에서 데이터를 다시 가져옵니다. 공시가 새로 제출된 뒤 수치가 반영됩니다. 첫 수집 전 저장소 Settings → Secrets and variables → Actions에 `SEC_CONTACT_EMAIL` secret(모니터링 가능한 연락 이메일)을 추가해야 합니다. 이메일은 저장소 코드에 공개되지 않습니다. GitHub Actions 화면에서 수동 실행도 할 수 있습니다.

**현재 상태:** `data/financials.json`의 연간·반기·분기 배열이 비어 있어 실제 분석값은 아직 표시되지 않습니다. `SEC_CONTACT_EMAIL` 설정 후 수집 작업이 성공하면 대시보드가 저장된 데이터로 자동 계산합니다.

출처는 [SEC Company Facts API](https://www.sec.gov/edgar/sec-api-documentation), Apple CIK 0000320193입니다. 금액은 USD millions, EPS는 USD이며 SEC XBRL GAAP 태그를 사용합니다. 반기는 6개월 누적 공시, 분기는 SEC 분기 공시 기준입니다.

## 국내 Peer Firms

| 기업 | 종목 코드 | 비교 근거 |
|---|---|---|
| 삼성전자 | 005930.KS | 스마트폰·태블릿·PC·반도체를 아우르며 Apple의 하드웨어 시장과 가장 넓게 겹칩니다. |
| LG전자 | 066570.KS | 가전·TV·IT 기기 중심의 글로벌 소비자 전자제품 기업으로 프리미엄 기기 및 브랜드 시장에서 비교할 수 있습니다. |

Peer는 사업·제품 유사성을 기준으로 한 참고 비교이며, 공급망 부품 업체는 제외했습니다. 이 자료는 투자 조언이 아닙니다.
