"""
설정 파일.
"""

# 캡쳐를 시작할 전역 단축키
HOTKEY_CAPTURE = "f9"

# 마지막으로 선택했던 영역을 그대로 재캡쳐하는 단축키 (드래그 없이 바로 재실행)
HOTKEY_RECAPTURE = "f10"

# 번역 대상 언어 ("ko" | "en" | "ja" 등) — 원문 언어는 이미지에서 자동으로 감지됨
TARGET_LANG = "ko"

# ===== 번역 엔진 설정 =====
# "claude" | "gemini" 중 하나 (이미지를 직접 이해하는 멀티모달 API 사용)
TRANSLATE_BACKEND = "claude"

# --- claude 사용 시 (https://console.anthropic.com 에서 API 키 발급) ---
ANTHROPIC_API_KEY = "여기에_API_키_입력"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # 번역처럼 가벼운 작업엔 Haiku가 빠르고 저렴함

# --- gemini 사용 시 (https://aistudio.google.com/apikey 에서 API 키 발급) ---
GEMINI_API_KEY = "여기에_API_키_입력"
GEMINI_MODEL = "gemini-2.5-flash"  # 모델명이 바뀌었으면 https://ai.google.dev/gemini-api/docs/models 확인
