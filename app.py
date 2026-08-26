"""
GUI 버전 실행 파일.
시작/정지 버튼으로 전역 단축키(F9/F10) 리스너를 켜고 끌 수 있고,
캡쳐/번역 기록을 창 안에서 확인할 수 있다.

F9: 새 영역을 드래그로 선택해서 캡쳐
F10: 마지막으로 선택했던 영역을 그대로 재캡쳐 (드래그 없이 바로)

exe로 빌드할 때 이 파일이 진입점이 된다 (build.bat 참고).
"""
import tkinter as tk
from datetime import datetime

import keyboard

import config
from pipeline import run_pipeline


class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("화면 번역기")
        self.root.geometry("420x440")
        self.root.resizable(False, False)

        self.running = False

        # 상태 표시
        self.status_var = tk.StringVar(value="🔴 정지됨")
        tk.Label(root, textvariable=self.status_var, font=("맑은 고딕", 13, "bold")).pack(pady=(15, 5))

        tk.Label(
            root,
            text=(
                f"{config.HOTKEY_CAPTURE.upper()}=새 영역 캡쳐   "
                f"{config.HOTKEY_RECAPTURE.upper()}=마지막 영역 재캡쳐   "
                f"|   번역 대상: {config.TARGET_LANG}"
            ),
            font=("맑은 고딕", 9), fg="#666",
        ).pack()

        # 시작/정지 토글 버튼
        self.toggle_btn = tk.Button(
            root, text="▶  시작", font=("맑은 고딕", 12, "bold"),
            width=16, height=1, bg="#1a73e8", fg="white",
            activebackground="#1558b0", activeforeground="white",
            relief="flat", command=self.toggle,
        )
        self.toggle_btn.pack(pady=(15, 8))

        # 마지막 영역 재캡쳐 버튼 (단축키 없이 마우스로도 가능하도록)
        self.recapture_btn = tk.Button(
            root, text="🔁  마지막 영역 재캡쳐", font=("맑은 고딕", 10),
            width=22, relief="flat", bg="#eee",
            command=self._trigger_recapture,
        )
        self.recapture_btn.pack(pady=(0, 12))

        # 최근 기록 로그
        tk.Label(root, text="최근 기록", font=("맑은 고딕", 9, "bold")).pack(anchor="w", padx=15)
        self.log_box = tk.Text(root, height=13, width=48, font=("맑은 고딕", 9), state="disabled")
        self.log_box.pack(padx=15, pady=(0, 15))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"[{timestamp}] {message}\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")
        self.log_box.update_idletasks()  # OCR/번역으로 잠깐 멈추기 전에 로그가 바로 보이도록

    def toggle(self):
        self.stop() if self.running else self.start()

    def start(self):
        keyboard.add_hotkey(config.HOTKEY_CAPTURE, self._on_hotkey_new)
        keyboard.add_hotkey(config.HOTKEY_RECAPTURE, self._on_hotkey_recapture)
        self.running = True
        self.status_var.set(f"🟢 실행중 ({config.HOTKEY_CAPTURE.upper()}로 캡쳐)")
        self.toggle_btn.config(text="⏹  정지", bg="#d93025", activebackground="#a52714")
        self.log("시작됨 — 아무 화면에서나 단축키를 눌러보세요.")

    def stop(self):
        keyboard.remove_hotkey(config.HOTKEY_CAPTURE)
        keyboard.remove_hotkey(config.HOTKEY_RECAPTURE)
        self.running = False
        self.status_var.set("🔴 정지됨")
        self.toggle_btn.config(text="▶  시작", bg="#1a73e8", activebackground="#1558b0")
        self.log("정지됨.")

    def _on_hotkey_new(self):
        # keyboard 라이브러리의 콜백은 별도 스레드에서 호출되므로,
        # Tkinter 작업은 반드시 after()로 메인 스레드에 넘겨서 실행해야 안전하다.
        self.root.after(0, self._run_pipeline_new)

    def _on_hotkey_recapture(self):
        self.root.after(0, self._run_pipeline_recapture)

    def _trigger_recapture(self):
        # 버튼 클릭은 이미 메인 스레드에서 호출되지만, 다른 경로와 통일해서 after()로 처리
        self.root.after(0, self._run_pipeline_recapture)

    def _run_pipeline_new(self):
        run_pipeline(log=self.log, parent=self.root)

    def _run_pipeline_recapture(self):
        run_pipeline(log=self.log, parent=self.root, reuse_region=True)

    def on_close(self):
        if self.running:
            keyboard.remove_hotkey(config.HOTKEY_CAPTURE)
            keyboard.remove_hotkey(config.HOTKEY_RECAPTURE)
        self.root.destroy()


def main():
    root = tk.Tk()
    TranslatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
