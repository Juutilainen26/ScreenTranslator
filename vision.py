"""
캡쳐 이미지를 멀티모달 LLM(Claude/Gemini)에 보내서, 화면 내용을 자연스러운
문장으로 설명 겸 번역해주는 모듈. 원문 위치에 맞춰 이미지에 합성하는 대신,
사람이 옆에서 설명해주듯 풀어서 알려준다.
"""
import base64
import io

import requests

import config

_LANG_NAMES = {
    "ja": "일본어",
    "ko": "한국어",
    "en": "영어",
}


def _image_to_base64(image):
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _build_prompt(target):
    tgt_name = _LANG_NAMES.get(target, target)
    return (
        f"이 화면 캡쳐 이미지를 보고 사용자에게 자연스럽게 설명해줘.\n"
        f"화면에 외국어 텍스트가 있으면 {tgt_name}로 번역해서 알려주고, "
        f"어떤 상황/맥락인지도 함께 짧게 설명해줘 "
        f"(예: 게임 화면이면 무슨 기능/이벤트인지, 설정 화면이면 뭘 하는 화면인지 등). "
        f"이미 {tgt_name}로 된 텍스트뿐이면 번역은 생략하고 내용만 설명해줘.\n"
        f"번역투 말고 친구한테 옆에서 설명해주듯 자연스러운 {tgt_name} 문장으로, "
        f"2~4문장 정도로 간결하게 답변해줘."
    )


def _call_claude_vision(image, prompt):
    if not config.ANTHROPIC_API_KEY or "여기에" in config.ANTHROPIC_API_KEY:
        raise RuntimeError("config.py에 ANTHROPIC_API_KEY를 입력해주세요.")

    b64 = _image_to_base64(image)
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": config.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": config.CLAUDE_MODEL,
            "max_tokens": 600,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}},
                    {"type": "text", "text": prompt},
                ],
            }],
        },
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Claude API 오류 ({resp.status_code}): {resp.text}")

    data = resp.json()
    return "".join(
        b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"
    ).strip()


def _call_gemini_vision(image, prompt):
    if not config.GEMINI_API_KEY or "여기에" in config.GEMINI_API_KEY:
        raise RuntimeError("config.py에 GEMINI_API_KEY를 입력해주세요.")

    b64 = _image_to_base64(image)
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{config.GEMINI_MODEL}:generateContent?key={config.GEMINI_API_KEY}"
    )
    resp = requests.post(
        url,
        json={
            "contents": [{
                "parts": [
                    {"inline_data": {"mime_type": "image/png", "data": b64}},
                    {"text": prompt},
                ],
            }],
        },
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini API 오류 ({resp.status_code}): {resp.text}")

    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise RuntimeError(f"Gemini 응답 형식을 해석할 수 없어요: {data}")


def explain_image(image, target="ko"):
    """
    image: PIL.Image (캡쳐 원본)
    target: 설명/번역에 사용할 언어
    반환: 자연스러운 설명 문장 (문자열)
    """
    prompt = _build_prompt(target)

    backend = config.TRANSLATE_BACKEND
    if backend == "claude":
        return _call_claude_vision(image, prompt)
    elif backend == "gemini":
        return _call_gemini_vision(image, prompt)
    else:
        raise RuntimeError(f"vision 모드는 claude/gemini 백엔드에서만 지원해요 (현재: {backend})")
