"""
캡쳐 이미지와 자연어 해설을 보여주는 팝업 창.
(이미지 자체는 그대로 보여주고, 그 아래에 해설/번역 텍스트를 표시함)
"""
import tkinter as tk
from PIL import ImageTk

_MAX_DISPLAY_SIZE = (600, 480)  # 너무 큰 캡쳐 이미지는 이 크기 안으로 축소해서 보여줌


def show_result(image, explanation, parent=None):
    if not explanation or not explanation.strip():
        explanation = "(해설 없음)"

    win = tk.Tk() if parent is None else tk.Toplevel(parent)
    win.title("화면 번역기 - 해설")
    win.attributes("-topmost", True)

    if image is not None:
        display_img = image.copy()
        display_img.thumbnail(_MAX_DISPLAY_SIZE)
        photo = ImageTk.PhotoImage(display_img, master=win)
        img_label = tk.Label(win, image=photo)
        img_label.image = photo  # 참조를 안 들고 있으면 가비지컬렉트되어 이미지가 사라짐
        img_label.pack(padx=10, pady=(10, 5))

    tk.Label(win, text="해설", font=("맑은 고딕", 10, "bold")).pack(anchor="w", padx=10)
    text_box = tk.Text(win, height=6, wrap="word", font=("맑은 고딕", 11))
    text_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    text_box.insert("1.0", explanation)
    text_box.config(state="disabled")

    tk.Button(win, text="닫기 (Esc)", command=win.destroy).pack(pady=(0, 10))
    win.bind("<Escape>", lambda e: win.destroy())

    win.wait_window()
