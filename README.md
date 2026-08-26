# 화면 캡쳐 번역기

F9를 누르면 화면 영역을 드래그로 선택 → 캡쳐 이미지를 그대로 Claude/Gemini에 보내서 **자연스러운 문장으로 번역+해설**을 받아 팝업으로 보여주는 프로그램. 단순 직역이 아니라 "어떤 화면인지, 뭐라고 적혀있는지"까지 사람이 옆에서 설명해주듯 풀어줘요.
`app.py`가 GUI(시작/정지 버튼) 버전이고, exe로 배포할 때도 이 파일을 기준으로 빌드합니다.

## 동작 방식

캡쳐한 이미지를 **통째로** 멀티모달 LLM(Claude 또는 Gemini)에 보내서, 화면 내용을 설명 겸 번역해주는 자연어 문장을 받아와요 (`vision.py`). 원문 위치에 맞춰 이미지에 글자를 합성하는 방식이 아니라(정확한 위치 계산이 필요 없어서 더 빠르고 로컬 리소스도 거의 안 씀), 캡쳐 이미지 원본과 해설 텍스트를 나란히 보여주는 방식이에요.

예시: 게임 가챠 화면을 캡쳐하면 →
> "어떤 게임의 가챠 화면이신 것 같아요! 110회 이후에는 SSR이 확정으로 뜬다고 적혀 있어요."

## 1. 개발 환경에서 실행해보기

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

```powershell
python app.py
```

- **▶ 시작** 버튼 → 상태가 `🟢 실행중`으로 바뀌고, 이제부터 아무 화면에서나 F9로 캡쳐 가능
- **⏹ 정지** 버튼 → 단축키 해제
- **🔁 마지막 영역 재캡쳐** 버튼 (또는 F10) → 방금 드래그했던 영역을 그대로 다시 캡쳐/해설. 게임 대사창처럼 같은 위치에 텍스트가 계속 나오는 경우, 매번 드래그할 필요 없이 F10만 눌러도 됨
- 창 안 "최근 기록"에 캡쳐/처리 진행 상황이 그대로 로그로 남음

콘솔 버전만 필요하면 `python main.py`도 그대로 사용 가능해요 (동작은 동일, GUI만 없음).

> ⚠️ `keyboard` 라이브러리는 전역 단축키를 잡기 위해 **관리자 권한 실행**이 필요할 수 있어요.

## 2. 번역 엔진 준비 (`config.py`의 `TRANSLATE_BACKEND`)

| 값 | 방식 |
|---|---|
| `"claude"` (기본) | Anthropic Claude API (비전) |
| `"gemini"` | Google Gemini API (비전) |

둘 다 호출당 소액이 과금돼요. 사용량이 걱정되면 Anthropic/Google 콘솔에서 확인해보세요.

### Claude API 사용 시 (기본값)
1. https://console.anthropic.com 에서 API 키 발급
2. `config.py`의 `ANTHROPIC_API_KEY`에 붙여넣기

### Gemini API 사용 시
1. https://aistudio.google.com/apikey 에서 API 키 발급
2. `config.py`의 `GEMINI_API_KEY`에 붙여넣기, `TRANSLATE_BACKEND = "gemini"`로 변경
3. `GEMINI_MODEL` 값이 만료/변경됐다면 https://ai.google.dev/gemini-api/docs/models 에서 현재 모델명으로 교체

**연결 테스트 (텍스트 기준 빠른 확인용):**
```powershell
python test_translate.py
```
"✅ 정상 동작합니다"가 뜨면 API 키/연결 자체는 정상. 실제 이미지 해설은 `python app.py`로 F9 캡쳐해서 확인하는 게 정확해요.

## 3. exe로 만들기 (더블클릭 실행)

**반드시 사용자님의 Windows PC에서 직접 빌드해야 해요** — 리눅스 환경(제가 코드를 작성하는 곳)에서는 Windows용 exe를 만들 수 없어서, 빌드 스크립트만 준비해드렸어요.

`build.bat`을 그냥 **탐색기에서 더블클릭**하면 됩니다. 가상환경이 없으면 알아서 만들고, 필요한 패키지도 알아서 설치한 다음 빌드까지 진행해요.

빌드가 끝나면 `dist\ScreenTranslator` **폴더**가 생기고, 그 안의 `ScreenTranslator.exe`를 더블클릭하면 실행돼요.

> ⚠️ **폴더째로 옮겨야 해요.** exe 파일 하나만 따로 복사해서 옮기면 실행이 안 됩니다. 다른 곳에 옮기고 싶으면 `dist\ScreenTranslator` 폴더 전체를 복사/압축해서 옮기면 돼요. `config.py`에 API 키를 미리 입력해둔 상태여야 exe 안에도 그대로 반영되고(exe 안에 키가 그대로 포함되니 다른 사람과 공유하지 않도록 주의), 인터넷 연결이 있어야 동작해요.

### 빌드가 실패하거나 exe 실행이 안 될 때

- 빌드 중 콘솔에 뜨는 에러 메시지 (빨간 글씨 부분)를 알려주시면 같이 잡아볼게요
- exe 실행했는데 아무 반응이 없다면: `build.bat`에서 `--windowed`를 잠깐 지우고 다시 빌드 → 콘솔창이 뜨면서 에러가 보일 거예요
- 앱 내 "최근 기록" 로그에는 오류 발생 시 전체 오류 내역(traceback)까지 찍히니, 그 내용을 보내주시면 원인 파악이 훨씬 빨라요

## 4. GitHub에 올려두고 필요할 때 받아쓰기

`config.py`에는 API 키가 그대로 들어있어서, **절대 커밋하면 안 돼요.** 이미 `.gitignore`에 `config.py`가 등록되어 있어서, 아래대로 하면 실수로 올라갈 일은 없어요.

**처음 올릴 때:**
```powershell
git init
git add .
git commit -m "화면 번역기 초기 버전"
```
그 다음 GitHub에서 **Private** 저장소를 새로 만들고:
```powershell
git remote add origin <저장소 URL>
git branch -M main
git push -u origin main
```

**커밋하기 전에 꼭 확인:** `git status`를 쳤을 때 `config.py`가 목록에 안 보여야 정상이에요. 혹시 보인다면 `.gitignore`가 제대로 적용 안 된 거니, 커밋하지 말고 먼저 말씀해주세요.

**다른 PC(또는 나중에)에서 받아서 쓸 때:**
```powershell
git clone <저장소 URL>
cd screen_translator
copy config.example.py config.py
```
그 다음 새로 생긴 `config.py`를 열어서 `ANTHROPIC_API_KEY`(또는 `GEMINI_API_KEY`)에 실제 키만 다시 입력하면 끝. 나머지는 그대로 `pip install -r requirements.txt` → `python app.py`.

## 5. 설정 바꾸기 (`config.py`)

- `HOTKEY_CAPTURE` — 새 영역 캡쳐 단축키 (기본 F9)
- `HOTKEY_RECAPTURE` — 마지막 영역 재캡쳐 단축키 (기본 F10)
- `TARGET_LANG` — 번역/해설에 사용할 언어 (기본 `ko`=한국어). 원문 언어는 이미지에서 자동으로 감지되므로 따로 지정할 필요 없음
- `TRANSLATE_BACKEND` — 번역 엔진 선택 (`claude` / `gemini`, 2번 항목 참고)

## 파일 구성

```
app.py             ← GUI 진입점 (exe 빌드 대상)
main.py            ← 콘솔 버전 (선택 사항)
pipeline.py        ← 캡쳐 -> vision.py 호출 -> 표시 전체 흐름 조율
capture.py         ← 드래그 영역 선택 + 캡쳐
vision.py          ← 이미지를 통째로 Claude/Gemini에 보내 자연어 해설/번역 받기
translate.py       ← 텍스트 전용 번역 헬퍼 (연결 테스트용)
popup.py           ← 캡쳐 이미지 + 해설 텍스트를 보여주는 결과 창
config.py          ← 단축키, 언어, 번역 엔진/API 키 설정 (git에는 안 올라감)
config.example.py ← config.py의 템플릿 (API 키 자리는 비워둔 채로 커밋됨)
.gitignore         ← config.py 등 커밋하면 안 되는 파일 목록
test_translate.py  ← 번역 엔진(텍스트) 연결 테스트용 스크립트
build.bat          ← exe 빌드 스크립트
requirements.txt
```

## 알려진 제약사항 (MVP라서 아직 없는 기능)

- 원문 위치에 맞춘 이미지 합성은 하지 않아요 (의도적으로 뺀 부분 — 자연어 해설 방식이 더 빠르고 자연스러워서). 대신 캡쳐 이미지 원본 + 해설 텍스트를 같이 보여줘요
- 해설이 상황에 따라 길이/스타일이 조금씩 달라질 수 있어요 (LLM이 그때그때 자연스럽게 요약하는 방식이라 완전히 고정된 포맷은 아님)
- 번역 대상 언어를 실행 중에 바로 전환하는 기능 없음 (지금은 `config.py`에서 수동으로 바꿔야 함)
- OCR/해설 처리 중에는 GUI가 잠깐 멈춘 것처럼 보일 수 있음 (백그라운드 스레드 대신 안정성을 위해 메인 스레드에서 처리)
- 인터넷 연결이 끊기면 동작 안 함 (API 기반이라 오프라인 사용 불가)

## 다음 단계 (선택)

- 캡쳐 영역 고정 + 화면 변화 감지 기반 지속 오버레이 모드
- 단축키로 번역 대상 언어 순환 전환
- exe 트레이 아이콘화 (작업표시줄 최소화)

진행 상황은 `PROGRESS.md`에 체크포인트로 정리되어 있어요.
