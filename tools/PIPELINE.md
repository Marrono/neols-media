# Neols 파이프라인 (자동 탐색 회차마다 / "지금 찾아줘" 때)

사이트 slug 77346c44-3520-4b60-a03e-fa5bbc4e0d06 · Instagram account 17841480857834317 (@neols.news)

## 카드뉴스 6~8장 · 릴스 25초 구성 (2026-11-20 사용자 결정, 최우선)
- 카드뉴스는 **최소 6장, 최대 8장** (예전 4~8장 규칙 대체). render.py → tpl.card_pages6 가 자동 구성:
  1 표지(사진+훅) → 2 사진+핵심 숫자 → 3 THEN 사진+연도  ← 이미지 중심, 글 최소, 한눈에 이목 집중
  4 쉽게 보기(NOW 풀이) → 5 여담 → (그래픽 · THEN 자세히) → 마지막 홍보
- JSON에 꼭 채울 것: explain {title:"질문형 제목", lines:[쉬운 말 3줄]}, asides [{kicker:"여담", title, lines:[2~3줄]}] (사실 확인된 흥미로운 뒷이야기·배경지식).
  reel.stat(숫자 장면), reel.hook, then_head/then_sub 도 필수.
- 8장 넘으면 여담 2번째 → 그래픽 2번째 → THEN 자세히 → 그래픽 순으로 뺌.
- 릴스는 **25초**(15초 흐름 + '쉽게 말하면' 5.5초 + '여담' 4.5초 장면 삽입). cine.make_reel → tpl.reel_html25.

## 템플릿 3종 — 소재마다 어울리는 걸 골라 씀 (2026-11-20 사용자 결정)
- JSON items[0].template 에 "cine" | "split" | "collage" 지정 → render.py·reel.py가 tpl.py로 자동 적용(카드·릴스 같은 템플릿).
- 고르는 기준:
  · cine(시네마): 사진 한 장의 힘이 큰 소재 — 사건·장소·인물·기념일·속보, 무게감 있는 소재. 애매하면 기본값.
  · split(스플릿): NOW와 THEN을 숫자로 맞비교할 수 있는 소재 — 물가·금리·집값·기록·통계(위 컬러 NOW ↔ 아래 흑백 THEN).
    표지·릴스 첫 장면은 **C안 고정**(2026-11-21 사용자 결정): 위 칸 아래쪽 'YYYY년 M월, 오늘' + 훅 2줄(흰 글씨), 아래 흑백 칸 위쪽 'then_label, 그때는' + reel.then_head, 경계 가운데 '그때는 어땠을까?' 파란 알약. 흰 상자 문구 쓰지 않음.
  · collage(콜라주): 생활·문화·소비·화제성 등 가벼운 소재, 사진이 여러 장일 때(밝은 종이·폴라로이드·THEN 도장).
  · 같은 템플릿이 3번 연속 나오지 않게(최근 초안 2개의 template 확인). drafts 문서에 template 기록.
## 시네마 템플릿 세부 (첫 선택안)
- 소재 1개 카드뉴스·릴스는 cine.py '시네마' 템플릿으로 만든다(render.py·reel.py가 자동 사용, JSON "theme":"classic"이면 예전 디자인).
- 카드: 사진 전면 + 어두운 그라데이션 + 흰 글씨, 상단 진행 막대·로고·NOW/THEN 태그, THEN 페이지는 흑백·필름 질감 + 큰 연도, 마지막은 밝은 홍보 페이지.
- 릴스(15초): 0초부터 훅 문장(밑줄 강조) → 큰 숫자+칩 → THEN 도장·연도 카운트(흑백) → 연결 문장 단어별 → 엔딩. 무음(음악은 사용자가 인스타에서).
- 사진은 최대한 많이: JSON photos 배열(0번 표지·NOW, 1번 숫자 장면). 소재마다 2장 이상 구하는 걸 목표로(관련 기관·장소·사물).
- JSON reel 항목을 꼭 채운다: hook("1줄\n2줄", 궁금증 생기는 짧은 문장), stat{label,value}, chips[["down"|"up","텍스트"]], then_head, then_sub.
- 릴스 표지: reel_cover.jpg = 훅이 다 나온 1.4초 장면(reel.py가 자동 저장).

## A. 제작 대기 후보 제작 (매 회차 확인)
- 제작 대상: status:"selected" 이고 **decidedAt(제작 대기로 넘어간 시각)에서 70분 이상 지난 것**.
  70분이 안 된 것은 그대로 둠. 사용자가 대화에서 "만들어줘"(지금 만들기)라고 하면 시간과 상관없이 즉시 제작.
1. candidates 중 status:"selected" 각각 → 소재 1개짜리 JSON(items 1개, handle "@neols.news", slogan 포함).
   항목: category, title(\n 줄바꿈), points 3개, then_label, then, link, source. 사실 확인된 것만.
   **표지 사진 찾는 순서** (위에서 안 되면 다음 단계로):
     ① 위키미디어 공용 — `python3 wiki_photo.py --list "<검색어 또는 Category:분류>"` → `--pick`
        (API가 429면 1분 쉬고 1번 재시도. 제목을 알면 `--direct`로 API 없이 받기)
     ② 다른 대안 — Openverse(api.openverse.org, 허용 목록에 있을 때) 등 CC0·퍼블릭 도메인·CC BY 사진 검색
     ③ 사진 보관함에서 비슷한 사진 — `python3 wiki_photo.py --lib "<키워드>"` (neols-media/photos, 이전에 받은 사진·출처 재사용)
     ④ 그래도 없으면 **표지 사진 없이 초안 생성** → drafts에 photoPending:true → 사이트에 '⚠️ 표지 사진 없음' 경고.
        이후 매 회차마다 photoPending 초안의 사진을 ①부터 다시 시도해, 구하면 다시 렌더·푸시·업로드하고 photoPending 삭제.
     공통 원칙: 인물 소재는 인물 대신 관련 장소·사물 사진. 얼굴을 알아볼 수 있는 사람이 나온 사진 제외.
       ①②에서 받은 사진은 자동으로 보관함에 저장. CC BY는 credit 끝에 "· 잘라서 사용".
   이미지(그래픽):
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
2. 카드: `python3 render.py <json> <out>` — **전체 최소 6장, 최대 8장(위 6~8장 구성 참고)** (render.py가 자동으로 맞춤)
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
4. 새 급상승 이슈가 있으면 candidates 등록(batchLabel "11/20 08:00 급상승"), meta/seen 갱신.
   **없으면 그 시점에 가장 많이 보는 국내 소재 1개**(meta/seen에 없는 것)를 후보로 등록(batchLabel "11/20 08:00 지금 인기"), 한 줄 알림.
   (자살·개인 신상 위주 등 다루기 부적절한 소재는 건너뛰고 다음 순위)
5. 민감한 정치·사건사고(사망, 범죄 피해자 등)는 사실 확인된 경우만 중립적으로, 개인 신상 위주 소재는 제외.

## C. 마무리
- **중복 예약 방지**: 다음 회차를 예약하기 전에 meta/status.nextRun을 확인해서, 이미 지금보다 미래 시각이면(다른 회차가 예약해 둔 것) 새로 예약하지 않음. 예약할 때는 nextRun을 먼저 갱신.
- meta/status lastRun·nextRun 갱신(ifVersion).
- 다음 회차 send_later: **24시간 쉬지 않고** 15분 뒤(:00/:15/:30/:45). 밤에도 동일.
- :15/:30/:45 회차는 A(70분 지난 제작 대기)·photoPending·meta/request만 보고, 할 일이 없으면 바로 끝냄(조용히).
- 새 급상승 후보나 새 초안이 생겼을 때만 SendUserMessage 한 줄 알림(무엇이 왜 떴는지).
- **알림 조건(활동 기반):** 알림 전 meta/siteSeen.at(사이트 열람·터치 시 자동 기록)과 meta/chatSeen.at(사용자가 이 대화에 메시지를 보낼 때마다 Claude가 기록) 중 최근 값을 확인. **30분 이내면 알림, 30분 넘게 반응 없으면 알림 생략**(작업·사이트 반영은 그대로 계속). 사용자가 다시 반응하는 순간부터 알림 재개.
- 사용자가 채팅에 메시지를 보내면 그 턴에서 meta/chatSeen {at: 메시지 시각}을 set으로 갱신.

## 문구 원칙 (2026-11-20 밤)
- 템플릿 고정 문구는 tpl.polish()가 마지막에 한국어로 다듬음: 오른쪽 위 알약 '11월 20일 뉴스'/'다시 보는 2020.03', '옆으로 넘겨보세요 →', '숫자로 보기', '그때와 지금 →', 사진 출처 '작가 (라이선스, 위키미디어 공용)'(작가 미상·Me는 '위키미디어 공용 (퍼블릭 도메인)').
- JSON 문구도 말하듯 자연스럽게: '~뭐예요?', '~했어요' 체, 명사로 뚝 끊는 표현·'개미' 같은 속어 대신 '개인'. 훅은 짧게, 캡션 첫 줄은 완전한 문장.
