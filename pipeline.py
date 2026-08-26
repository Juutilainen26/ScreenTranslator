"""
캡쳐 -> 이미지를 멀티모달 LLM에 보내 자연어 해설/번역 받기 -> 표시.
GUI(app.py)와 콘솔 버전(main.py)에서 공통으로 사용한다.
"""
import traceback

import config
from capture import RegionSelector, capture_region
from popup import show_result
from vision import explain_image

_busy = False  # 처리 중에 또 실행되지 않도록 막는 플래그
_last_region = None  # 마지막으로 사용한 캡쳐 영역 (재캡쳐 기능용)


def run_pipeline(log=print, parent=None, reuse_region=False):
    """
    log: 진행 상황을 전달받을 콜백 함수 (기본은 print)
    parent: GUI에서 호출할 때 메인 창(tk 객체)을 넘기면 그 자식 창으로 뜬다.
            콘솔에서 호출할 때는 None으로 두면 독립 창으로 뜬다.
    reuse_region: True면 드래그 없이 마지막으로 썼던 영역을 그대로 재캡쳐한다.
                  아직 저장된 영역이 없으면 안내만 하고 종료한다.
    """
    global _busy, _last_region
    if _busy:
        log("이미 처리 중입니다. 잠시 후 다시 시도해주세요.")
        return

    _busy = True
    try:
        if reuse_region:
            if _last_region is None:
                log("아직 저장된 영역이 없어요. 먼저 새 영역 캡쳐(F9)를 한 번 해주세요.")
                return
            region = _last_region
            log(f"마지막 캡쳐 영역 재사용: {region}")
        else:
            log("영역을 드래그해서 선택하세요 (Esc: 취소)")
            region = RegionSelector(parent=parent).select()
            if region is None:
                log("선택이 취소되었습니다.")
                return
            _last_region = region
            log(f"캡쳐 영역: {region}")

        image = capture_region(region)

        log(f"이미지를 {config.TRANSLATE_BACKEND}로 전송해서 해설 받는 중...")
        explanation = explain_image(image, target=config.TARGET_LANG)

        log(f"해설:\n{explanation}")

        show_result(image, explanation, parent=parent)

    except Exception as e:
        log(f"오류 발생: {e}")
        log("상세 정보:\n" + traceback.format_exc())

    finally:
        _busy = False
