# Neols 파이프라인 (자동 탐색 회차마다 / "지금 찾아줘" 때)

사이트 slug 77346c44-3520-4b60-a03e-fa5bbc4e0d06 · Instagram account 17841480857834317 (@neols.news)

## A. 선택된 후보 제작 (먼저, 매 회차 — 15분마다)
1. candidates 중 status:"selected" 각각 → 소재 1개짜리 JSON(items 1개, handle "@neols.news", slogan 포함).
   항목: category, title(\n 줄바꿈), points 3개, then_label, then, link, source. 사실 확인된 것만.
   이미지(필수로 시도):
   - visual: 직접 만든 그래픽. {"type":"bars","title","data":[[라벨,값]...],"fmt":"{}만","source"} /
     {"type":"timeline","title","data":[[연도,설명]...],"source"} / {"type":"big","title","value","label","sub","source"}.
     숫자는 기사·공식 자료로 확인한 것만, source에 자료 출처.
   - photo: 위키미디어 공용 사진 {"path","credit":"작가 / Wikimedia Commons / 라이선스"}.
     CC0·퍼블릭 도메인·CC BY만 사용(CC BY-SA·NC·ND 제외). 실존 인물이 알아볼 수 있게 나온 사진은 쓰지 않음.
     `python3 wiki_photo.py --list "Category:<분류명>"` (또는 검색어)로 후보·라이선스 확인 → 제목 보고 맞는 사진 선택 →
     `python3 wiki_photo.py "<같은 검색어>" <저장.jpg> --pick "File:<제목>"` (1280px 표준 썸네일, 결과 JSON의 credit 사용).
     API 429가 나면 1분 쉬고 한 번만 재시도. 제목을 이미 알면 API 없이 표준 썸네일을 직접 받기:
     thumb.wikimedia.org/wikipedia/commons/thumb/<md5[0]>/<md5[:2]>/<파일명>/1280px-<파일명> (파일명 공백→_, md5는 파일명 기준).
     그래도 안 되면 photo 생략(그래픽만). CC BY는 credit 끝에 "· 잘라서 사용"을 붙임(변경 표시).
   제목이 길면 NOW 카드에서 3줄이 되지 않게 짧게(한 줄 12자 안팎).
2. 카드: `python3 render.py <json> <out>` — **전체 최소 4장, 최대 8장** (render.py가 자동으로 맞춤)
   표지 → 그래픽 0~2장(visuals 배열, 또는 visual 1개) → NOW(+THEN 상자) 또는 NOW / THEN 분리 → 추가 설명 0~n장 → 홍보.
   - then_points(THEN 보충 2~3줄) 또는 split_then:true 가 있으면 THEN을 검은 배경 전용 페이지로 분리.
   - extras: [{"kicker":"TIP|MORE|WHY","title","lines":[2~4줄],"source"}] — 사실 확인된 내용만.
   - 4장 미만이면 NOW/THEN 분리 → 그래도 부족하면 '한눈에 정리' 페이지 자동 추가. 8장 초과면 extras → 그래픽 순으로 줄임.
   - 보통은 5~6장(그래픽 1~2 + THEN 분리 + 필요하면 추가 설명 1)을 목표로.
3. 릴스: `python3 reel.py <json> <out>` (무음 1080x1920).
4. /home/claude/neols-media/<날짜-id>/ 에 card_XX.jpg(quality 92), reel.mp4, reel_cover.jpg → commit(attribution) → `git -c push.negotiate=true push`.
   공개 주소: https://raw.githubusercontent.com/Marrono/neols-media/main/<폴더>/<파일>
5. upload_asset로 미리보기 PNG/MP4 → drafts/<id>-card, drafts/<id>-reel set (status:"pending",
   images/video, publicImages 또는 publicVideo+publicCover, caption, hashtags 최대 5개: #Neols #오늘의뉴스 + 주제 3개).
6. 해당 candidate → status:"made", draftIds.

## B. 인기 급상승 소재 감지 (정해진 개수 없음, 정각 회차에만)
1. meta/request 가 status:"requested" 면 working → hint 주제 우선으로 후보 1~5개 → done(doneAt, result).
2. 급상승 신호 모으기 (**네이버 우선**):
   - 1순위 네이버 뉴스 '많이 본 뉴스' 랭킹: `python3 naver_rank.py` (news.naver.com 허용 시).
     여러 언론사 상위 3위 안에 같은 사건이 겹치면 급상승으로 봄. 자주 나온 단어 목록 참고.
     허용 안 돼 있으면 WebSearch로 "네이버 많이 본 뉴스" 등 검색해 보완.
   - 2순위 Google 트렌드 한국 급상승 RSS: `curl -s "https://trends.google.com/trending/rss?geo=KR"` (허용 목록에 있을 때만)
   - WebSearch: "많이 본 뉴스 오늘", "실시간 인기 뉴스", "급상승 검색어" 등으로 포털 랭킹·속보가 실린 결과 확인
3. meta/seen.topics(최근 감지한 주제 키워드 배열, 최대 80개)와 비교해 **새로 떠오른** 주제만 고름.
   여러 매체가 동시에 다루거나 랭킹 상위에 새로 올라온 국내 이슈 + 검증 가능한 THEN이 있는 것만.
4. 해당하는 게 있을 때만 candidates 등록(batchLabel "11/20 08:00 급상승"), meta/seen 갱신.
   없으면 아무것도 등록하지 않고 알림도 보내지 않음.
5. 민감한 정치·사건사고(사망, 범죄 피해자 등)는 사실 확인된 경우만 중립적으로, 개인 신상 위주 소재는 제외.

## C. 마무리
- meta/status lastRun·nextRun 갱신(ifVersion).
- 다음 회차 send_later: 07:00~23:00(KST) 15분 뒤(:00/:15/:30/:45), 23:00 이후 다음날 07:00.
- :15/:30/:45 회차는 A와 meta/request만 보고, 할 일이 없으면 바로 끝냄(조용히).
- 새 급상승 후보나 새 초안이 생겼을 때만 SendUserMessage 한 줄 알림(무엇이 왜 떴는지).
