import tkinter as tk
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Button:
    canvas: tk.Canvas
    center_pos: tuple[int, int]
    size: tuple[int, int]
    message: str

    on_click: Callable[["Button"], None] | None = None

    rect_id: int | None = field(default=None, init=False)
    text_id: int | None = field(default=None, init=False)
    hitbox_id: int | None = field(default=None, init=False)

    def __post_init__(self):
        self.mount()
    
    def mount(self):
        button_w, button_h = self.size
        x, y = self.center_pos

        self.rect_id = self.canvas.create_rectangle(
            x - button_w/2,
            y - button_h/2,
            x + button_w/2,
            y + button_h/2,
            fill="#7d91a1",
            outline=""
        )
        self.text_id = self.canvas.create_text(
            x,
            y,
            justify="center",
            text=self.message,
            fill="white",
            font="LuckiestGuy 25 bold",
        )
        self.hitbox_id = self.canvas.create_rectangle(
            x - button_w/2,
            y - button_h/2,
            x + button_w/2,
            y + button_h/2,
            fill="",
            outline=""
        )
        self.canvas.tag_bind(self.hitbox_id, "<Enter>", lambda _: self.canvas.itemconfig(self.rect_id, fill="#e38539"))
        self.canvas.tag_bind(self.hitbox_id, "<Leave>", lambda _: self.canvas.itemconfig(self.rect_id, fill="#7d91a1"))
        self.canvas.tag_bind(self.hitbox_id, "<Button-1>", self.click)

    def click(self, event: tk.Event):
        if self.on_click:
            self.on_click(self)
