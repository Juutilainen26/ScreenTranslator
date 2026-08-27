"""
화면 영역 드래그 선택 + 캡쳐 모듈.
parent를 넘기면 그 창의 자식(Toplevel)으로 뜨고, 없으면 독립 창(Tk)으로 뜬다.
"""
import tkinter as tk
from mss import mss
from PIL import Image


class RegionSelector:
    """
    화면 전체(멀티 모니터 포함)를 반투명하게 덮고, 마우스 드래그로 캡쳐 영역을 선택받는 창.

    tkinter의 -fullscreen 속성은 모니터 1개 기준으로만 전체화면이 되기 때문에
    (두 번째 모니터는 덮이지 않아 그쪽에서는 드래그 자체가 안 됨), 대신 mss로
    연결된 모든 모니터를 합친 가상 화면 전체 크기를 구해서 그 크기에 맞게
    테두리 없는 창을 직접 배치하는 방식을 쓴다.
    """

    def __init__(self, parent=None):
        self.parent = parent
        self._start = (0, 0)
        self._end = (0, 0)
        self._cancelled = False
        self._origin = (0, 0)  # 가상 화면 좌상단의 절대 좌표 (보조 모니터가 왼쪽/위에 있으면 음수일 수 있음)

    def select(self):
        """
        드래그로 캡쳐 영역을 선택.
        반환: (left, top, right, bottom) 절대 좌표, 또는 취소(Esc) 시 None
        """
        with mss() as sct:
            virtual_screen = sct.monitors[0]  # index 0 = 연결된 모든 모니터를 합친 영역

        origin_x = virtual_screen["left"]
        origin_y = virtual_screen["top"]
        width = virtual_screen["width"]
        height = virtual_screen["height"]
        self._origin = (origin_x, origin_y)

        win = tk.Tk() if self.parent is None else tk.Toplevel(self.parent)
        win.overrideredirect(True)  # 제목표시줄 없는 창 - 모니터 경계에 상관없이 정확한 위치/크기 지정용
        win.geometry(f"{width}x{height}+{origin_x}+{origin_y}")
        win.attributes("-alpha", 0.25)   # 반투명하게 화면을 덮음
        win.attributes("-topmost", True)
        win.config(cursor="cross")
        win.grab_set()  # 선택 끝날 때까지 다른 조작 막기

        canvas = tk.Canvas(win, bg="gray", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        rect_id = {"id": None}

        def on_press(event):
            self._start = (event.x, event.y)
            rect_id["id"] = canvas.create_rectangle(
                event.x, event.y, event.x, event.y, outline="red", width=2
            )

        def on_drag(event):
            self._end = (event.x, event.y)
            if rect_id["id"] is not None:
                canvas.coords(rect_id["id"], *self._start, *self._end)

        def finish():
            win.grab_release()
            win.destroy()

        def on_release(event):
            self._end = (event.x, event.y)
            finish()

        def on_escape(event):
            self._cancelled = True
            finish()

        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        win.bind("<Escape>", on_escape)

        win.wait_window()  # 중첩 mainloop 없이, 이 창이 닫힐 때까지만 대기

        if self._cancelled:
            return None

        left, right = sorted([self._start[0], self._end[0]])
        top, bottom = sorted([self._start[1], self._end[1]])

        if right - left < 5 or bottom - top < 5:
            return None  # 너무 작게 선택하면 무효 처리

        # 창(캔버스) 내부 좌표 -> 실제 데스크톱 절대 좌표로 변환
        origin_x, origin_y = self._origin
        return (
            origin_x + left,
            origin_y + top,
            origin_x + right,
            origin_y + bottom,
        )


def capture_region(region):
    """
    region: (left, top, right, bottom) - 절대 좌표
    반환: PIL.Image (RGB)
    """
    left, top, right, bottom = region
    monitor = {"left": left, "top": top, "width": right - left, "height": bottom - top}
    with mss() as sct:
        shot = sct.grab(monitor)
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
    return img
