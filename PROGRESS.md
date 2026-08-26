# 프로젝트 진행 상황 체크포인트

## 최초 계획
캡쳐 → OCR → 번역 → 표시 파이프라인. "단축키 캡쳐 → 팝업" 방식을 1단계로 구현 → GUI(시작/정지 버튼) + exe 단일 실행파일화를 2차로 진행.

## 완료된 것

### 1~5단계 — MVP (콘솔 기반)
1. ✅ `capture.py` — 드래그 영역 선택 UI + mss 캡쳐
2. ✅ `ocr.py` — PaddleOCR 연동 (PaddleOCR 3.x API 대응 완료, oneDNN 버그 우회 처리)
3. ✅ `translate.py` — 번역 모듈
4. ✅ `popup.py` — 원문/번역 나란히 보여주는 결과창
5. ✅ `main.py` — F9 단축키로 전체 파이프라인 연결 (콘솔 MVP 완성)

### 6단계 — GUI + exe 패키징
6. ✅ `pipeline.py` — 파이프라인 로직 분리 (GUI/콘솔 공통 사용)
7. ✅ `capture.py`, `popup.py` — parent 파라미터 지원 (Toplevel 방식)
8. ✅ `app.py` — 시작/정지 토글 버튼 + 상태표시(🟢/🔴) + 실시간 로그창 GUI
9. ✅ `build.bat` — PyInstaller 기반 exe 빌드 스크립트

### 7단계 — 번역 백엔드 교체 (Papago → 로컬 Ollama)
- Papago(NCP)로 시도했으나 실사용 결론: **무료 티어 없음, 사용하는 순간 월 최소 약 2만원 청구**되는 과금 구조로 확인됨 (요금은 1,000,000자 단위로 올림 청구)
- 사용자가 로컬 LLM(Ollama) 방식으로 전환 결정 — 완전 무료, 가입/카드 불필요, 기존에 쓰던 qwen2.5 모델 재사용
- ✅ `translate.py` — Papago API 코드 제거, Ollama(`http://localhost:11434/api/generate`) 호출로 교체
- ✅ `config.py` — Papago 키 설정 제거, `OLLAMA_MODEL = "qwen2.5"` 추가
- ✅ `pipeline.py` — 번역 호출부를 client_id/secret 방식에서 model 파라미터 방식으로 수정
- ✅ `test_ollama.py` — 기존 `test_papago.py` 대체, Ollama 연결/번역 진단용
- ✅ README.md — Papago 관련 섹션 전부 제거, "Ollama 준비" 섹션으로 교체

### 8단계 — 마지막 영역 재캡쳐 기능
- ✅ `pipeline.py` — 마지막 캡쳐 영역을 저장해두고, `reuse_region=True`면 드래그 없이 재사용하도록 개선
- ✅ `config.py` — `HOTKEY_RECAPTURE = "f10"` 추가
- ✅ `main.py`, `app.py` — F10 단축키 등록 + GUI에 "🔁 마지막 영역 재캡쳐" 버튼 추가

### 9단계 — 캡쳐 이미지에 번역문 오버레이
- 사용자 요청: 원문/번역 텍스트만 따로 보여주면 "어느 위치의 글자를 번역한 건지" 알기 어려움 → 캡쳐 이미지 위에 번역문을 원문 자리 그대로 그려서 보여주는 방식으로 변경 (망가/게임 번역기 방식)
- ✅ `ocr.py` — `extract_text()` → `extract_lines()`로 변경, 텍스트뿐 아니라 각 줄의 좌표(`rec_boxes`)도 같이 반환
- ✅ `translate.py` — 변경 없음, 줄 단위로 여러 번 호출하는 방식으로 사용
- ✅ `overlay.py` (신규) — 원문 자리를 배경색으로 덮고 그 위에 번역문을 그려 넣는 모듈. 폰트는 맑은 고딕(`C:/Windows/Fonts/malgun.ttf`) 사용, 박스 크기에 맞춰 폰트 크기 자동 축소
- ✅ `popup.py` — 오버레이된 이미지를 보여주고, 그 아래에 원문/번역 텍스트(복사용)도 같이 표시하도록 변경
- ✅ `pipeline.py` — 줄 단위 OCR → 줄 단위 번역 → 오버레이 합성 → 표시 순서로 재작성
- 리눅스 샌드박스에서 합성 로직 자체는 자체 테스트로 정상 동작 확인 (폰트가 없어 한글은 깨져 보였지만, 실제 사용자 Windows 환경에는 맑은 고딕이 있어 정상 렌더링 예상 — 사용자 PC에서 실제 확인 필요)

### 10단계 — 번역 품질 저하 수정 (줄별 개별 번역 → 문맥 유지 일괄 번역)
- 문제: 9단계에서 오버레이 위치 매칭을 위해 줄마다 따로 번역기를 호출하게 만들었더니, 문맥이 끊겨서 번역 품질이 눈에 띄게 떨어짐 (예: 후리가나 줄과 본문 줄이 서로 다른 OCR 줄로 인식되는 경우 등)
- ✅ `translate.py` — `translate_lines()` 함수 추가: 모든 줄을 번호 매겨 **한 번에** 모델에 보내 맥락을 유지한 채 번역시키고, 응답을 번호 기준으로 다시 줄별로 분리. 모델이 형식을 안 지켜 파싱 실패 시에만 안전하게 줄별 개별 번역(`translate_text`)으로 대체
- ✅ `pipeline.py` — 줄마다 반복 호출하던 부분을 `translate_lines()` 단일 호출로 교체

### 11단계 — exe 빌드 문제 해결 (onefile → onedir, paddlex 누락 수정)
- 문제 흐름: `.bat` 파일 줄바꿈(LF→CRLF) 문제 → `keyboard` 모듈 미포함(venv 미활성화 상태로 더블클릭 실행) → `paddlex` 패키지 데이터 미포함으로 "OCR pipeline 없음" 오류, 순서로 계속 다른 이슈가 발생
- PaddleOCR 3.x는 실제 파이프라인 설정을 `paddlex` 패키지 안에 두는데, `--collect-all`에 `paddlex`가 빠져있어서 발생한 문제였음
- 사용자가 `--onefile` 대신 `--onedir`(폴더 배포) 방식으로 전환 결정 — PaddleOCR처럼 리소스가 많은 패키지는 onefile보다 onedir이 더 안정적
- ✅ `build.bat` — `--onedir`로 변경, `--collect-all paddlex` 추가, 빌드 전 자체적으로 venv 활성화(없으면 생성) + `requirements.txt` 설치까지 하도록 개선 (탐색기 더블클릭 실행 대비)
- ✅ README.md — exe가 `dist\ScreenTranslator` 폴더 형태로 나오고, 폴더 전체를 옮겨야 한다는 점 안내 추가

### 12단계 — "dependency error" 해결 시도 + 에러 로그 개선
- 원인 추정: PaddleX가 내부적으로 OCR 파이프라인 생성 시 opencv/pyclipper/shapely 등의 설치 여부를 **패키지 메타데이터(dist-info)** 기준으로 확인하는데, `--collect-all`은 코드/데이터는 챙겨도 메타데이터까지는 안 챙겨서 "의존성 없음"으로 오판하는 알려진 PyInstaller+PaddleX 조합 이슈
- ✅ `build.bat` — `--copy-metadata opencv-python/opencv-contrib-python/pyclipper/shapely` 추가
- ✅ `pipeline.py` — 예외 발생 시 `traceback.format_exc()`로 전체 스택트레이스까지 로그에 남기도록 개선 (앞으로 비슷한 애매한 에러가 나도 바로 원인 파악 가능)

### 13단계 — 번역 엔진을 Claude/Gemini API 선택 가능하게 확장
- 이유: 로컬 Ollama가 PC 하드웨어 리소스(GPU/CPU)를 잡아먹는 게 부담스럽고, 사용자가 이미 Gemini API와 Claude API를 결제해서 쓰고 있어서 그걸 재사용하고 싶어함
- ✅ `translate.py` — `config.TRANSLATE_BACKEND` 값(`"claude"`/`"gemini"`/`"ollama"`)에 따라 세 가지 백엔드 중 선택해서 호출하는 구조로 재작성. `translate_lines()`/`translate_text()` 공개 인터페이스는 그대로 유지(내부에서 백엔드 분기)
- ✅ `config.py` — `TRANSLATE_BACKEND`(기본값 `"claude"`), `ANTHROPIC_API_KEY`, `CLAUDE_MODEL`(`claude-haiku-4-5-20251001`), `GEMINI_API_KEY`, `GEMINI_MODEL`(`gemini-2.5-flash`) 추가
- ✅ `pipeline.py` — 번역 호출부에서 `model=` 인자 제거 (translate.py 내부에서 config로 처리)
- ✅ `test_ollama.py` → `test_translate.py`로 교체 (백엔드 무관하게 연결 테스트 가능)
- ✅ README.md — 번역 엔진 3가지 선택지와 각각의 API 키 발급 방법 안내로 갱신
- 참고: Claude/Gemini는 호출당 소액 과금되고 인터넷 연결이 필요함 (Ollama는 무료/오프라인이지만 로컬 리소스 사용) — 트레이드오프를 README에 명시함

### 14단계 — 멀티모달 비전 활용으로 아키텍처 단순화 (PaddleOCR 제거, claude/gemini 기준)
- 사용자 인사이트: "이 대형 LLM들 이미지 던져줘도 알아서 다 해석하지 않아?" — 맞음. Claude/Gemini는 이미지를 직접 이해할 수 있어서, 캡쳐 이미지를 통째로 보내면 텍스트 인식+번역+위치를 한 번에 받을 수 있음
- 이러면 claude/gemini 백엔드에서는 **PaddleOCR이 완전히 필요 없어짐** → 지금까지 계속 발목 잡던 exe 빌드 문제(oneDNN, keyboard 미포함, paddlex 누락, opencv 메타데이터 등)가 전부 원천 해결됨
- ✅ `vision.py` (신규) — 이미지를 base64로 인코딩해 Claude/Gemini 비전 API에 전송, "원문+번역+bounding box" JSON 배열로 응답받아 파싱
- ✅ `pipeline.py` — `config.TRANSLATE_BACKEND`에 따라 분기: claude/gemini는 `vision.py` 경로(OCR 없음), ollama는 기존 `ocr.py`+`translate.py` 경로. 각 경로의 import를 지연 로딩으로 변경(사용하지 않는 백엔드의 무거운 의존성을 아예 안 불러오도록)
- ✅ `requirements.txt` — `paddlepaddle`/`paddleocr`를 ollama 전용 선택사항으로 주석 처리 (기본 경로에서 불필요)
- ✅ `build.bat` — PaddleOCR 관련 `--collect-all`/`--copy-metadata` 플래그 전부 제거 (claude/gemini 기준으로는 더 이상 필요 없음). ollama로 전환 시 필요한 플래그는 README에 별도 기록해둠
- ✅ README.md — 아키텍처 변경사항(claude/gemini는 vision 경로, ollama는 기존 경로) 및 각 경로별 준비방법 정리

### 15단계 — Ollama 완전 제거, API 전용으로 전환
- 사용자 결정: "올라마를 제발 버려! 이제 api로만 간다구!" — 로컬 리소스 부담, PaddleOCR 패키징 골치 등을 이유로 ollama/PaddleOCR 경로를 완전히 드랍하고 claude/gemini API만 사용하기로 확정
- ✅ `ocr.py` 삭제 (PaddleOCR 더 이상 사용 안 함)
- ✅ `pipeline.py` — ollama 분기 제거, vision.py(이미지 통째 전송) 경로로 단일화
- ✅ `translate.py` — `_call_ollama` 및 관련 백엔드 항목 제거, claude/gemini만 남김 (텍스트 전용 연결 테스트용으로 계속 사용)
- ✅ `config.py` — `OLLAMA_MODEL` 등 ollama 관련 설정 제거
- ✅ `requirements.txt` — paddleocr/paddlepaddle 관련 주석 전부 제거 (mss/pillow/requests/keyboard 4개만 남음)
- ✅ README.md — ollama 관련 섹션/표/트러블슈팅 전부 제거, API 전용 문서로 정리

### 16단계 — 원문 언어 자동 감지로 전환 (고정 언어 필터 버그 수정)
- 버그 발견: 영어 텍스트(NCP 콘솔의 "Storage/Database" 등)를 캡쳐했는데 "텍스트를 인식하지 못했습니다"로 나옴 → 원인은 `config.DEFAULT_OCR_LANG`이 `"ja"`로 고정되어 있어서, vision 프롬프트가 "일본어 텍스트만 찾아줘"로 되어 있었던 것. Gemini가 정확하게 "일본어 없음"이라고 판단해 빈 결과를 준 것이었음 (코드 버그는 아니고 설계 자체의 한계)
- 해결: 비전 모델은 언어 자동 감지가 가능하므로, 원문 언어를 사전 지정하지 않고 "번역 대상 언어(한국어)가 아닌 텍스트를 전부 찾아줘" 방식으로 프롬프트를 일반화함 — 어떤 언어든 상관없이 인식되도록 개선
- ✅ `vision.py` — `_build_prompt()`/`extract_and_translate()`에서 `source` 파라미터 제거, 언어 무관 자동 감지 프롬프트로 변경
- ✅ `config.py` — `DEFAULT_OCR_LANG`/`TRANSLATE_TARGET` 제거, 단일 `TARGET_LANG = "ko"`로 단순화
- ✅ `pipeline.py`, `app.py` — 위 변경사항에 맞춰 참조 수정
- ✅ README.md — 설정 항목 설명 갱신

### 17단계 — 이미지 오버레이 제거, 자연어 해설 방식으로 전환
- 사용자 피드백: 이미지 합성(오버레이)이 로컬에서 처리되다 보니 체감 성능이 딸림 → 정확한 위치 계산 없이, LLM이 화면을 보고 자연스러운 문장으로 번역+맥락 설명을 해주는 방식(예: "가챠 화면이신 것 같아요! 110회 이후 SSR 확정이라고 적혀 있어요")으로 변경 제안 → 채택
- ✅ `overlay.py` 삭제 (더 이상 이미지에 텍스트를 합성하지 않음)
- ✅ `vision.py` — JSON+bounding box 파싱 방식(`extract_and_translate`) 제거, 자유 텍스트로 자연스러운 해설을 받는 `explain_image()`로 교체
- ✅ `pipeline.py` — 오버레이 합성 단계 제거, `explain_image()` 결과를 그대로 표시하도록 단순화
- ✅ `popup.py` — 원문/번역 텍스트 박스 대신, 캡쳐 이미지 원본(그대로) + "해설" 텍스트 박스 하나로 UI 단순화
- ✅ README.md — 새 방식 설명 및 예시 추가, 오버레이 관련 제약사항 문구 제거

### 18단계 — GitHub 업로드 준비 (private repo)
- 사용자가 완성된 프로젝트를 GitHub(프라이빗)에 올려두고 필요할 때 clone해서 쓰고 싶어함
- 핵심 문제: `config.py`에 실제 API 키가 그대로 들어있어서 절대 커밋하면 안 됨 (private repo라도 안전을 위해 원천 차단)
- ✅ `.gitignore` (신규) — `config.py`, `venv/`, `__pycache__/`, `build/`, `dist/`, `*.spec` 등록
- ✅ `config.example.py` (신규) — `config.py`와 동일 구조지만 API 키 자리가 플레이스홀더인 템플릿, 이건 커밋 가능
- ✅ README.md — "GitHub에 올려두고 필요할 때 받아쓰기" 섹션 추가: 최초 push 방법, 커밋 전 `git status`로 config.py 안 보이는지 확인하라는 안내, 새 PC에서 clone 후 `config.example.py` → `config.py` 복사해서 키 재입력하는 방법까지 정리
- 주의: 사용자 로컬의 실제 `config.py`(진짜 API 키 포함)는 이번 작업에서 건드리지 않음 — 압축 파일에 포함하지 않고 새 파일들만 별도 안내

## 현재 상태: MVP + exe 배포 + GitHub 업로드 준비까지 완료
더블클릭 실행되는 화면 번역기(캡쳐 → Claude/Gemini 비전으로 인식+번역+맥락 해설 → 팝업 표시)가 목표한 형태로 완성됨.
번역 백엔드는 API 전용(claude/gemini)이며 Ollama/PaddleOCR은 완전히 제거됨.

## 다음에 이어서 할 것 (선택사항)
- [ ] 사용자가 실제로 `git init` ~ `git push`까지 진행 후 GitHub에 private repo로 잘 올라갔는지, `config.py`가 빠져있는지 확인 필요
- [ ] 캡쳐 영역 고정 + 화면 변화 감지 기반 지속 오버레이 모드
- [ ] 단축키로 번역 대상 언어 순환 전환
- [ ] 멀티 모니터 환경 좌표 보정 확인
- [ ] exe 트레이 아이콘화 (작업표시줄 최소화)

## 재개 시 참고
- 개발 중 테스트: `python app.py`
- 번역 엔진(텍스트) 연결만 확인: `python test_translate.py`
- exe 빌드: `build.bat` 더블클릭 (사용자 PC, Windows 환경에서만 가능) — 완료된 상태
- GitHub: `config.py`는 `.gitignore`에 등록되어 있음. 새 환경에서는 `config.example.py`를 `config.py`로 복사 후 API 키만 입력하면 됨
- 새 세션에서 이어간다면: 이 파일 + README.md만 보고 "다음에 이어서 할 것" 항목부터 진행하면 됨
