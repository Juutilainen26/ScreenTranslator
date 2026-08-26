"""
설정 로더.
실제 설정 값은 이 파일이 아니라, PC의 %APPDATA%\\ScreenTranslator\\settings.py 에 있다.
exe로 빌드해도 이 외부 파일만 고치면 재빌드 없이 바로 설정이 반영된다
(그리고 exe 결과물 안에는 API 키가 전혀 안 들어가게 되어 더 안전함).

처음 실행하면 settings.py가 자동으로 만들어지니, 그 파일을 열어서 값을 채우면 된다.
"""
import importlib.util
import os

_TEMPLATE = '''"""
화면 번역기 설정 파일.
이 파일을 수정한 뒤 프로그램(exe 포함)을 다시 실행하면 바로 반영됩니다.
"""

# 캡쳐를 시작할 전역 단축키
HOTKEY_CAPTURE = "f9"

# 마지막으로 선택했던 영역을 그대로 재캡쳐하는 단축키 (드래그 없이 바로 재실행)
HOTKEY_RECAPTURE = "f10"

# 번역 대상 언어 ("ko" | "en" | "ja" 등) - 원문 언어는 이미지에서 자동으로 감지됨
TARGET_LANG = "ko"

# ===== 번역 엔진 설정 =====
# "claude" | "gemini" 중 하나 (이미지를 직접 이해하는 멀티모달 API 사용)
TRANSLATE_BACKEND = "claude"

# --- claude 사용 시 (https://console.anthropic.com 에서 API 키 발급) ---
ANTHROPIC_API_KEY = "여기에_API_키_입력"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# --- gemini 사용 시 (https://aistudio.google.com/apikey 에서 API 키 발급) ---
GEMINI_API_KEY = "여기에_API_키_입력"
GEMINI_MODEL = "gemini-2.5-flash"
'''

_DEFAULTS = {
    "HOTKEY_CAPTURE": "f9",
    "HOTKEY_RECAPTURE": "f10",
    "TARGET_LANG": "ko",
    "TRANSLATE_BACKEND": "claude",
    "ANTHROPIC_API_KEY": "여기에_API_키_입력",
    "CLAUDE_MODEL": "claude-haiku-4-5-20251001",
    "GEMINI_API_KEY": "여기에_API_키_입력",
    "GEMINI_MODEL": "gemini-2.5-flash",
}


def _settings_dir():
    appdata = os.getenv("APPDATA")
    if appdata:
        return os.path.join(appdata, "ScreenTranslator")
    # APPDATA가 없는 환경(윈도우가 아닌 경우) 대비용
    return os.path.join(os.path.expanduser("~"), ".screen_translator")


def _settings_path():
    return os.path.join(_settings_dir(), "settings.py")


def settings_file_path():
    """설정 파일이 실제로 어디 있는지 알려주는 헬퍼 (안내 메시지 등에 사용)."""
    return _settings_path()


def _ensure_exists():
    path = _settings_path()
    if not os.path.exists(path):
        os.makedirs(_settings_dir(), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(_TEMPLATE)
    return path


def _load():
    path = _ensure_exists()
    try:
        spec = importlib.util.spec_from_file_location("screen_translator_user_settings", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:
        # settings.py 문법 오류 등으로 로드에 실패하면 기본값으로 동작 (앱이 죽지 않도록)
        class _Empty:
            pass
        return _Empty()


_settings = _load()

HOTKEY_CAPTURE = getattr(_settings, "HOTKEY_CAPTURE", _DEFAULTS["HOTKEY_CAPTURE"])
HOTKEY_RECAPTURE = getattr(_settings, "HOTKEY_RECAPTURE", _DEFAULTS["HOTKEY_RECAPTURE"])
TARGET_LANG = getattr(_settings, "TARGET_LANG", _DEFAULTS["TARGET_LANG"])
TRANSLATE_BACKEND = getattr(_settings, "TRANSLATE_BACKEND", _DEFAULTS["TRANSLATE_BACKEND"])
ANTHROPIC_API_KEY = getattr(_settings, "ANTHROPIC_API_KEY", _DEFAULTS["ANTHROPIC_API_KEY"])
CLAUDE_MODEL = getattr(_settings, "CLAUDE_MODEL", _DEFAULTS["CLAUDE_MODEL"])
GEMINI_API_KEY = getattr(_settings, "GEMINI_API_KEY", _DEFAULTS["GEMINI_API_KEY"])
GEMINI_MODEL = getattr(_settings, "GEMINI_MODEL", _DEFAULTS["GEMINI_MODEL"])
