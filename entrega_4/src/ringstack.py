
import tkinter as tk
from dataclasses import dataclass, field
from typing import Callable, ClassVar

from constants import Constants as c
from game import RingType

class RingStack:
    __canvas: tk.Canvas
    __pos: tuple[int, int]
    __ring_type: RingType
    __count: int = 16
    __on_click: Callable[["RingStack"], None] | None = None

    __ring_id: int = field(init=False)
    __text_id: int = field(init=False)

    __asset_names: ClassVar[dict[RingType, str]] = {
        RingType.RED: "red_ring",
        RingType.BLUE: "blue_ring",
        RingType.GREEN: "green_ring",
    }

    def __init__(
        self,
        canvas: tk.Canvas,
        pos: tuple[int, int],
        ring_type: RingType,
        count: int = 16,
        on_click: Callable[["RingStack"], None] | None = None,
    ):
        self.__canvas = canvas
        self.__pos = pos
        self.__ring_type = ring_type
        self.__count = count
        self.__on_click = on_click

        self.__ring_id = None
        self.__text_id = None

        self.mount()
    
    def mount(self):
        x,y = self.__pos

        asset_name = self.__asset_names[self.__ring_type]
        asset = c.assets[asset_name]

        self.__ring_id = self.__canvas.create_image(
            x, y, image=asset
        )
        self.__text_id = self.__canvas.create_text(
            x + 85,
            y + 65,
            justify="center",
            fill="black",
            font="LuckiestGuy 20 bold",
            text=self.__count
        )

        self.__canvas.tag_bind(self.__ring_id, "<Button-1>", self.click)
    
    def click(self, event: tk.Event):
        if self.__on_click:

            self.__on_click(self)
    
    def get_count(self):
        return self.__count

    def get_ring_type(self):
        return self.__ring_type
    
    def set_count(self, amount: int):
        self.__count = amount
        self.__canvas.itemconfig(self.__text_id, text=self.__count)
