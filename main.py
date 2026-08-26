"""
콘솔 버전 실행 파일. GUI 없이 콘솔창에서만 돌리고 싶을 때 사용.
(exe로 배포할 때는 app.py를 씁니다 — README.md 참고)

F9: 새 영역을 드래그로 선택해서 캡쳐
F10: 마지막으로 선택했던 영역을 그대로 재캡쳐 (드래그 없이 바로)

실행: python main.py
종료: 콘솔 창에서 Ctrl+C
"""
import keyboard

import config
from pipeline import run_pipeline


def _console_log(message):
    print(f"[번역기] {message}")


def main():
    print(f"[번역기] 설정 파일 위치: {config.settings_file_path()}")
    print(
        f"[번역기] 준비 완료! "
        f"{config.HOTKEY_CAPTURE.upper()}=새 영역 캡쳐, "
        f"{config.HOTKEY_RECAPTURE.upper()}=마지막 영역 재캡쳐"
    )
    print("[번역기] 종료하려면 이 창에서 Ctrl+C를 누르세요.")
    keyboard.add_hotkey(config.HOTKEY_CAPTURE, lambda: run_pipeline(log=_console_log))
    keyboard.add_hotkey(config.HOTKEY_RECAPTURE, lambda: run_pipeline(log=_console_log, reuse_region=True))
    keyboard.wait()


if __name__ == "__main__":
    main()
