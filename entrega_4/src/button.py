import tkinter as tk
from typing import Callable


class Button:
    __canvas: tk.Canvas
    __center_pos: tuple[int, int]
    __size: tuple[int, int]
    __message: str

    __on_click: Callable[["Button"], None] | None

    __rect_id: int | None
    __text_id: int | None
    __hitbox_id: int | None

    def __init__(
        self,
        canvas: tk.Canvas,
        center_pos: tuple[int, int],
        size: tuple[int, int],
        message:str,
        on_click: Callable[["Button"], None] | None=None
    ):
        self.__canvas = canvas
        self.__center_pos = center_pos
        self.__size = size
        self.__message = message
        self.__on_click = on_click

        self.__rect_id = None
        self.__text_id = None
        self.__hitbox_id = None

        self.mount()
    
    def mount(self):
        button_w, button_h = self.__size
        x, y = self.__center_pos

        self.__rect_id = self.__canvas.create_rectangle(
            x - button_w/2,
            y - button_h/2,
            x + button_w/2,
            y + button_h/2,
            fill="#7d91a1",
            outline=""
        )
        self.__text_id = self.__canvas.create_text(
            x,
            y,
            justify="center",
            text=self.__message,
            fill="white",
            font="LuckiestGuy 25 bold",
        )
        self.__hitbox_id = self.__canvas.create_rectangle(
            x - button_w/2,
            y - button_h/2,
            x + button_w/2,
            y + button_h/2,
            fill="",
            outline=""
        )
        self.__canvas.tag_bind(self.__hitbox_id, "<Enter>", lambda _: self.__canvas.itemconfig(self.__rect_id, fill="#e38539"))
        self.__canvas.tag_bind(self.__hitbox_id, "<Leave>", lambda _: self.__canvas.itemconfig(self.__rect_id, fill="#7d91a1"))
        self.__canvas.tag_bind(self.__hitbox_id, "<Button-1>", self.click)

    def click(self, event: tk.Event):
        if self.__on_click:
            self.__on_click(self)
