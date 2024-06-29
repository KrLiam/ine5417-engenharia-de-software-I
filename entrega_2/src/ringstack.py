
import tkinter as tk
from dataclasses import dataclass, field
from typing import Callable, ClassVar

from constants import Constants as c
from game import RingType

@dataclass
class RingStack:
    canvas: tk.Canvas
    pos: tuple[int, int]
    ring_type: RingType
    amount: int = 16
    on_click: Callable[["RingStack"], None] | None = None

    ring_id: int = field(init=False)
    text_id: int = field(init=False)

    asset_names: ClassVar[dict[RingType, str]] = {
        RingType.RED: "red_ring",
        RingType.BLUE: "blue_ring",
        RingType.GREEN: "green_ring",
    }

    def __post_init__(self):
        self.mount()
    
    def mount(self):
        x,y = self.pos

        asset_name = self.asset_names[self.ring_type]
        asset = c.assets[asset_name]

        self.ring_id = self.canvas.create_image(
            x, y, image=asset
        )
        self.text_id = self.canvas.create_text(
            x + 85,
            y + 65,
            justify="center",
            fill="black",
            font="LuckiestGuy 20 bold",
            text=self.count
        )

        self.canvas.tag_bind(self.ring_id, "<Button-1>", self.click)
    
    def click(self, event: tk.Event):
        if self.on_click:

            self.on_click(self)
    
    def get_count(self):
        return self.count
    
    def set_count(self, amount: int):
        self.count = amount
        self.canvas.itemconfig(self.text_id, text=self.count)
