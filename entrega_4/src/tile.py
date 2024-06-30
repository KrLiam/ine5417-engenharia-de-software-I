import tkinter as tk
from dataclasses import dataclass, field
from typing import Callable

from constants import Constants as c
from game import RingType


class Tile:
    __canvas: tk.Canvas = field(repr=False)
    __board_origin: tuple[float, float]
    __pos: tuple[int, int]
    __on_click: Callable[["Tile"], None] | None = None

    __canvas_pos: tuple[int, int] | None
    __hover_rect_id: int | None
    __rect_id: int | None
    __red_id: int | None
    __green_id: int | None
    __blue_id: int | None

    def __init__(
        self,
        canvas: tk.Canvas,
        board_origin: tuple[float, float],
        pos: tuple[int, int],
        on_click: Callable[["Tile"], None] | None = None,
    ):
        self.__canvas = canvas
        self.__board_origin = board_origin
        self.__pos = pos
        self.__on_click = on_click

        self.__canvas_pos = None
        self.__hover_rect_id = None
        self.__rect_id = None
        self.__red_id = None
        self.__green_id = None
        self.__blue_id = None

        self.mount()
    
    def get_pos(self):
        return self.__pos
    
    def mount(self):
        tile_size = c.BOARD_TILE_SIZE
        board_outline_size = c.BOARD_OUTLINE_SIZE
        tile_outline_size = c.BOARD_TILE_OUTLINE

        board_x, board_y = self.__board_origin
        i, j = self.__pos

        # o -1 é porque a hitbox estava 1 pixel a direita do que devia, apenas pro x
        x = board_x + board_outline_size + j*(tile_size + tile_outline_size) - 1
        y = board_y + board_outline_size + i*(tile_size + tile_outline_size)
        self.__canvas_pos = (x, y)

        self.__hover_rect_id = self.__canvas.create_image(
            x, y, image=c.assets["transparent_tile_overlay"], anchor="nw"
        )
        self.__rect_id = self.__canvas.create_image(
            x, y, image=c.assets["transparent_tile_overlay"], anchor="nw"
        )
        self.add_event_listeners(self.__rect_id)

    def add_event_listeners(self, id: int):
        self.__canvas.tag_bind(id, "<Enter>", self.enter)
        self.__canvas.tag_bind(id, "<Leave>", self.leave)
        self.__canvas.tag_bind(id, "<Button-1>", self.click)
    
    def unmount(self):
        self.__canvas.delete(self.__rect_id)
    
    def enter(self, event: tk.Event):
        self.__canvas.itemconfig(self.__hover_rect_id, image=c.assets["hover_tile_overlay"])

    def leave(self, event: tk.Event):
        self.__canvas.itemconfig(self.__hover_rect_id, image=c.assets["transparent_tile_overlay"])

    def click(self, event: tk.Event):
        if self.__on_click:
            self.__on_click(self)
    
    def update_ring_set(self, ring_set: set[RingType]):
        x, y = self.__canvas_pos
        x += c.BOARD_TILE_SIZE / 2
        y += c.BOARD_TILE_SIZE / 2

        if RingType.RED in ring_set:
            if not self.__red_id:
                self.__red_id = self.__canvas.create_image(x, y, image=c.assets["red_ring"])
                self.add_event_listeners(self.__red_id)

        else:
            if self.__red_id:
                self.__canvas.delete(self.__red_id)
            self.__red_id = None

        if RingType.GREEN in ring_set:
            if not self.__green_id:
                self.__green_id = self.__canvas.create_image(x, y, image=c.assets["green_ring"])
                self.add_event_listeners(self.__green_id)
        else:
            if self.__green_id:
                self.__canvas.delete(self.__green_id)
            self.__green_id = None

        if RingType.BLUE in ring_set:
            if not self.__blue_id:
                self.__blue_id = self.__canvas.create_image(x, y, image=c.assets["blue_ring"])
                self.add_event_listeners(self.__blue_id)
        else:
            if self.__blue_id:
                self.__canvas.delete(self.__blue_id)
            self.__blue_id = None
    
    def highlight_overlay(self):
        self.__canvas.itemconfig(self.__rect_id, image=c.assets["highlight_tile_overlay"])

    def victory_overlay(self):
        self.__canvas.itemconfig(self.__rect_id, image=c.assets["victory_tile_overlay"])

    def defeat_overlay(self):
        self.__canvas.itemconfig(self.__rect_id, image=c.assets["defeat_tile_overlay"])

    def clear_overlay(self):
        self.__canvas.itemconfig(self.__rect_id, image=c.assets["transparent_tile_overlay"])
