"""
텍스트 전용 번역 헬퍼. 캡쳐-번역 메인 흐름은 vision.py가 담당하지만,
연결 테스트(test_translate.py)처럼 이미지 없이 텍스트만 빠르게 확인할 때 사용한다.
config.TRANSLATE_BACKEND ("claude" | "gemini")에 맞는 API를 호출한다.
"""
import re
import requests

import config

_LANG_NAMES = {
    "ja": "일본어",
    "ko": "한국어",
    "en": "영어",
}


def _build_lines_prompt(texts, source, target):
    src_name = _LANG_NAMES.get(source, source)
    tgt_name = _LANG_NAMES.get(target, target)
    numbered_input = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(texts))
    return (
        f"다음은 화면에서 인식된 {src_name} 텍스트 줄 목록이야. 전체 맥락을 참고해서 "
        f"자연스러운 {tgt_name}로 번역해줘.\n"
        f"반드시 입력과 같은 줄 수를 유지하고, 각 줄 앞에 원래 번호를 그대로 붙여서 "
        f"'번호. 번역문' 형식으로만 출력해. 다른 설명은 하지 마.\n\n"
        f"{numbered_input}"
    )


def _build_single_prompt(text, source, target):
    src_name = _LANG_NAMES.get(source, source)
    tgt_name = _LANG_NAMES.get(target, target)
    return (
        f"다음 {src_name} 텍스트를 자연스러운 {tgt_name}로 번역해줘. "
        f"부가 설명 없이 번역 결과만 출력해.\n\n{text}"
    )


def _parse_numbered_response(raw, expected_count):
    parsed = {}
    for line in raw.splitlines():
        m = re.match(r"\s*(\d+)[.\)]\s*(.*)", line)
        if m:
            parsed[int(m.group(1))] = m.group(2).strip()
    if len(parsed) == expected_count and all((i + 1) in parsed for i in range(expected_count)):
        return [parsed[i + 1] for i in range(expected_count)]
    return None


def _call_claude(prompt):
    if not config.ANTHROPIC_API_KEY or "여기에" in config.ANTHROPIC_API_KEY:
        raise RuntimeError("config.py에 ANTHROPIC_API_KEY를 입력해주세요.")

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": config.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": config.CLAUDE_MODEL,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Claude API 오류 ({resp.status_code}): {resp.text}")

    data = resp.json()
    return "".join(
        block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
    ).strip()


def _call_gemini(prompt):
    if not config.GEMINI_API_KEY or "여기에" in config.GEMINI_API_KEY:
        raise RuntimeError("config.py에 GEMINI_API_KEY를 입력해주세요.")

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{config.GEMINI_MODEL}:generateContent?key={config.GEMINI_API_KEY}"
    )
    resp = requests.post(
        url,
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini API 오류 ({resp.status_code}): {resp.text}")

    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise RuntimeError(f"Gemini 응답 형식을 해석할 수 없어요: {data}")


_BACKENDS = {
    "claude": _call_claude,
    "gemini": _call_gemini,
}


def _call_backend(prompt):
    backend = config.TRANSLATE_BACKEND
    func = _BACKENDS.get(backend)
    if func is None:
        raise RuntimeError(
            f"알 수 없는 TRANSLATE_BACKEND: '{backend}' (claude / gemini 중 하나여야 함)"
        )
    return func(prompt)


def translate_text(text, source="ja", target="ko"):
    """단일 텍스트 번역."""
    if not text.strip():
        return ""
    return _call_backend(_build_single_prompt(text, source, target))


def translate_lines(texts, source="ja", target="ko"):
    """
    texts: 번역할 원문 줄들의 리스트
    반환: texts와 개수가 같은 번역문 리스트 (맥락 유지를 위해 한 번에 번역 요청)
    """
    if not any(t.strip() for t in texts):
        return ["" for _ in texts]

    raw = _call_backend(_build_lines_prompt(texts, source, target))
    parsed = _parse_numbered_response(raw, len(texts))
    if parsed is not None:
        return parsed

    return [translate_text(t, source, target) for t in texts]
