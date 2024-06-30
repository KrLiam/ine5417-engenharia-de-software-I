import tkinter as tk
from dataclasses import dataclass, field
from typing import Callable

from constants import Constants as c
from game import RingType


@dataclass
class Tile:
    canvas: tk.Canvas = field(repr=False)
    board_origin: tuple[float, float]
    pos: tuple[int, int]
    canvas_pos: tuple[int, int] = field(init=False)

    hover_rect_id: int | None = field(default=None, init=False)
    rect_id: int | None = field(default=None, init=False)
    red_id: int | None = field(default=None, init=False)
    green_id: int | None = field(default=None, init=False)
    blue_id: int | None = field(default=None, init=False)

    on_click: Callable[["Tile"], None] | None = None

    def __post_init__(self):
        self.mount()
    
    def mount(self):
        tile_size = c.BOARD_TILE_SIZE
        board_outline_size = c.BOARD_OUTLINE_SIZE
        tile_outline_size = c.BOARD_TILE_OUTLINE

        board_x, board_y = self.board_origin
        i, j = self.pos

        # o -1 é porque a hitbox estava 1 pixel a direita do que devia, apenas pro x
        x = board_x + board_outline_size + j*(tile_size + tile_outline_size) - 1
        y = board_y + board_outline_size + i*(tile_size + tile_outline_size)
        self.canvas_pos = (x, y)

        self.hover_rect_id = self.canvas.create_image(
            x, y, image=c.assets["transparent_tile_overlay"], anchor="nw"
        )
        self.rect_id = self.canvas.create_image(
            x, y, image=c.assets["transparent_tile_overlay"], anchor="nw"
        )
        self.add_event_listeners(self.rect_id)

    def add_event_listeners(self, id: int):
        self.canvas.tag_bind(id, "<Enter>", self.enter)
        self.canvas.tag_bind(id, "<Leave>", self.leave)
        self.canvas.tag_bind(id, "<Button-1>", self.click)
    
    def unmount(self):
        self.canvas.delete(self.rect_id)
    
    def enter(self, event: tk.Event):
        self.canvas.itemconfig(self.hover_rect_id, image=c.assets["hover_tile_overlay"])

    def leave(self, event: tk.Event):
        self.canvas.itemconfig(self.hover_rect_id, image=c.assets["transparent_tile_overlay"])

    def click(self, event: tk.Event):
        if self.on_click:
            self.on_click(self)
    
    def update_ring_set(self, ring_set: set[RingType]):
        x, y = self.canvas_pos
        x += c.BOARD_TILE_SIZE / 2
        y += c.BOARD_TILE_SIZE / 2

        if RingType.RED in ring_set:
            if not self.red_id:
                self.red_id = self.canvas.create_image(x, y, image=c.assets["red_ring"])
                self.add_event_listeners(self.red_id)

        else:
            if self.red_id:
                self.canvas.delete(self.red_id)
            self.red_id = None

        if RingType.GREEN in ring_set:
            if not self.green_id:
                self.green_id = self.canvas.create_image(x, y, image=c.assets["green_ring"])
                self.add_event_listeners(self.green_id)
        else:
            if self.green_id:
                self.canvas.delete(self.green_id)
            self.green_id = None

        if RingType.BLUE in ring_set:
            if not self.blue_id:
                self.blue_id = self.canvas.create_image(x, y, image=c.assets["blue_ring"])
                self.add_event_listeners(self.blue_id)
        else:
            if self.blue_id:
                self.canvas.delete(self.blue_id)
            self.blue_id = None
    
    def highlight_overlay(self):
        self.canvas.itemconfig(self.rect_id, image=c.assets["highlight_tile_overlay"])

    def victory_overlay(self):
        self.canvas.itemconfig(self.rect_id, image=c.assets["victory_tile_overlay"])

    def defeat_overlay(self):
        self.canvas.itemconfig(self.rect_id, image=c.assets["defeat_tile_overlay"])

    def clear_overlay(self):
        self.canvas.itemconfig(self.rect_id, image=c.assets["transparent_tile_overlay"])
