from dataclasses import dataclass
from enum import Enum, auto
from functools import partial
import tkinter as tk
from typing import Any
from constants import Constants as c



@dataclass(frozen=True)
class Tile:
    rect_id: int
    pos: tuple[int, int]


class PlayerActor:
    window: tk.Tk
    canvas: tk.Canvas
    counter: int
    cell_map: list

    mounted: dict[str, Any] | None

    def __init__(self):
        width, height = c.DEFAULT_SIZE

        self.window = tk.Tk()
        self.window.title(c.TITLE)
        self.window.geometry(f"{width}x{height}")
        self.window.resizable(c.RESIZABLE, c.RESIZABLE)
        self.window.configure(bg=c.BACKGROUND_COLOR)

        self.canvas = tk.Canvas(self.window, width=width, height=height, background=c.BACKGROUND_COLOR)
        self.canvas.pack()

        self.counter = 0
        self.mounted = None
        self.cell_map = []

    def loop(self):
        def callback():
            self.update()
            self.window.after(c.DELAY, callback)

        self.window.after(1, callback)
        self.window.mainloop()


    def rect(x, y, width, height, centered=True):
        if centered:
            x -= width // 2
            y -= height // 2
        return (x, y, x + width, y + height)
    
    def mount_board(self):
        w, h = self.window_size

        cx, cy = w/2, h/2
        board_x, board_y = cx - c.BOARD_SIZE/2, cy - c.BOARD_SIZE/2

        board_img = tk.PhotoImage(file=c.BOARD_PATH)
        board = self.canvas.create_image(
            cx, cy, image=board_img
        )

        tiles: dict[tuple[int, int], Tile] = {}
        tile_size = c.BOARD_TILE_SIZE
        board_outline_size = c.BOARD_OUTLINE_SIZE
        tile_outline_size = c.BOARD_TILE_OUTLINE

        for i in range(0, c.NUM_ROWS):
            for j in range(0, c.NUM_COLS):
                # o -1 é porque a hitbox estava 1 pixel a direita do que devia, apenas pro x
                x = board_x + board_outline_size + j*(tile_size + tile_outline_size) - 1
                y = board_y + board_outline_size + i*(tile_size + tile_outline_size)

                rect_id = self.canvas.create_rectangle(
                    x, y, x + tile_size, y + tile_size, outline="", fill=""
                )
                tile = Tile(rect_id, (i, j))

                self.canvas.tag_bind(rect_id, "<Button-1>", partial(self.clicked_tile, tile))
                self.canvas.tag_bind(rect_id, "<Enter>", partial(self.enter_tile, tile))
                self.canvas.tag_bind(rect_id, "<Leave>", partial(self.leave_tile, tile))
                tiles[(i, j)] = tile
        
        ring_container_img = tk.PhotoImage(file=c.RING_CONTAINER)
        ring_container_size_x = c.RING_CONTAINER_SIZE[0]
        ring_container_cx = board_x - ring_container_size_x / 2 - c.BOARD_CONTAINER_PADDING
        ring_container = self.canvas.create_image(
            ring_container_cx, cy, image=ring_container_img
        )

        blue_ring_img = tk.PhotoImage(file=c.BLUE_RING_PATH)
        blue_ring = self.canvas.create_image(
            ring_container_cx, cy- 10, image=blue_ring_img
        )

        red_ring_img = tk.PhotoImage(file=c.RED_RING_PATH)
        red_ring = self.canvas.create_image(
            ring_container_cx, cy - 175, image=red_ring_img
        )

        green_ring_img = tk.PhotoImage(file=c.GREEN_RING_PATH)
        green_ring = self.canvas.create_image(
            ring_container_cx, cy + 150, image=green_ring_img
        )

        self.canvas.pack()

        self.mounted = {
            "board_id": board,
            "ring_container_id": ring_container,
            "blue_ring_id": blue_ring,
            "green_ring_id": green_ring,
            "blue_ring_id": blue_ring,
            "images": [board_img, ring_container_img, blue_ring_img, red_ring_img, green_ring_img],
            "tiles": tiles,
        }
    
    def enter_tile(self, tile: Tile, event: tk.Event):
        self.canvas.itemconfig(tile.rect_id, fill="yellow")

    def leave_tile(self, tile: Tile, event: tk.Event):
        self.canvas.itemconfig(tile.rect_id, fill="")

    def clicked_tile(self, tile: Tile, event: tk.Event):
        print("clicked", tile, event)        

    def update(self):
        self.counter += 1

        if self.mounted is None:
            self.mount_board()

    @property
    def window_size(self) -> tuple[int, int]:
        return (self.window.winfo_width(), self.window.winfo_height())