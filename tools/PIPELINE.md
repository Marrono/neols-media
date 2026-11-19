# Neols 파이프라인 (자동 탐색 회차마다 / "지금 찾아줘" 때)

사이트 slug 77346c44-3520-4b60-a03e-fa5bbc4e0d06 · Instagram account 17841480857834317 (@neols.news)

## A. 선택된 후보 제작 (먼저)
1. candidates 중 status:"selected" 각각 → 소재 1개짜리 JSON(items 1개, handle "@neols.news", slogan 포함).
   항목: category, title(\n 줄바꿈), points 3개, then_label, then, link, source. 사실 확인된 것만.
   이미지(필수로 시도):
   - visual: 직접 만든 그래픽. {"type":"bars","title","data":[[라벨,값]...],"fmt":"{}만","source"} /
     {"type":"timeline","title","data":[[연도,설명]...],"source"} / {"type":"big","title","value","label","sub","source"}.
     숫자는 기사·공식 자료로 확인한 것만, source에 자료 출처.
   - photo: 위키미디어 공용 사진 {"path","credit":"작가 / Wikimedia Commons / 라이선스"}.
     CC0·퍼블릭 도메인·CC BY만 사용(CC BY-SA·NC·ND 제외). 실존 인물이 알아볼 수 있게 나온 사진은 쓰지 않음.
     commons API로 검색 → 파일 페이지의 라이선스·작가 확인 → 1600px 썸네일 다운로드. 접속이 막혀 있으면 photo 생략.
2. 카드: `python3 render.py <json> <out>` → 표지(사진 있으면 상단 사진+하단 출처) / BY THE NUMBERS 그래픽(visual 있을 때) / NOW+THEN / 홍보.
3. 릴스: `python3 reel.py <json> <out>` (무음 1080x1920).
4. /home/claude/neols-media/<날짜-id>/ 에 card_XX.jpg(quality 92), reel.mp4, reel_cover.jpg → commit(attribution) → `git -c push.negotiate=true push`.
   공개 주소: https://raw.githubusercontent.com/Marrono/neols-media/main/<폴더>/<파일>
5. upload_asset로 미리보기 PNG/MP4 → drafts/<id>-card, drafts/<id>-reel set (status:"pending",
   images/video, publicImages 또는 publicVideo+publicCover, caption, hashtags 최대 5개: #Neols #오늘의뉴스 + 주제 3개).
6. 해당 candidate → status:"made", draftIds.

## B. 새 후보 5개
1. meta/request 가 status:"requested" 면 working으로 바꾸고 hint 주제 우선 → 끝나면 done(doneAt, result).
2. 국내 뉴스 검색 → 기존 candidates와 겹치지 않는 5개, 각각 검증된 THEN 포함.
3. candidates/c<YYYYMMDD-HHMM>-<n> set: batchId, batchLabel("11/20 07:00"), createdAt, status:"new",
   category, title, summary(2~3줄 배열), then_label, then, link, sources.
4. 민감한 정치 뉴스는 사실 확인된 경우만 중립적으로.

## C. 마무리
- meta/status lastRun·nextRun 갱신(ifVersion).
- 다음 회차 send_later: 07:00~23:00(KST) 30분 뒤, 23:00 이후 다음날 07:00.
- 새 후보/초안이 생기면 SendUserMessage 한 줄 알림.
