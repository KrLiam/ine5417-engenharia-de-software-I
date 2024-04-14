from dataclasses import dataclass, field
from enum import Enum
import tkinter as tk
from typing import Any, Callable
from constants import Constants as c


class RingType(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"


@dataclass
class Tile:
    canvas: tk.Canvas = field(repr=False)
    board_origin: tuple[float, float]
    pos: tuple[int, int]

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

        self.rect_id = self.canvas.create_image(
            x, y, image=c.assets["unselected_tile_overlay"], anchor="nw"
        )

        self.canvas.tag_bind(self.rect_id, "<Enter>", self.enter)
        self.canvas.tag_bind(self.rect_id, "<Leave>", self.leave)
        self.canvas.tag_bind(self.rect_id, "<Button-1>", self.click)
    
    def unmount(self):
        self.canvas.delete(self.rect_id)
    
    def enter(self, event: tk.Event):
        self.canvas.itemconfig(self.rect_id, image=c.assets["selected_tile_overlay"])

    def leave(self, event: tk.Event):
        self.canvas.itemconfig(self.rect_id, image=c.assets["unselected_tile_overlay"])

    def click(self, event: tk.Event):
        if self.on_click:
            self.on_click(self)


class GamePlayerInterface:
    window: tk.Tk
    canvas: tk.Canvas

    mounted: dict[str, Any] | None
    selected_ring: RingType | None
    status_message: str

    def __init__(self):
        width, height = c.DEFAULT_SIZE

        self.window = tk.Tk()
        self.window.title(c.TITLE)
        self.window.geometry(f"{width}x{height}")
        self.window.resizable(c.RESIZABLE, c.RESIZABLE)
        self.window.configure(bg=c.BACKGROUND_COLOR)

        self.canvas = tk.Canvas(self.window, width=width, height=height, background=c.BACKGROUND_COLOR)
        self.canvas.pack()

        self.mounted = None
        self.selected_ring = None
        self.status_message = ""

    def loop(self):
        def callback():
            self.update()
            self.window.after(c.DELAY, callback)

        self.window.after(c.DELAY, callback)
        self.window.mainloop()

    
    def mount_board(self):
        w, h = self.window_size

        cx, cy = w/2, h/2
        board_x, board_y = cx - c.BOARD_SIZE/2, cy - c.BOARD_SIZE/2

        board = self.canvas.create_image(
            cx, cy, image=c.assets["board"]
        )

        tiles: dict[tuple[int, int], Tile] = {}

        for i in range(0, c.NUM_ROWS):
            for j in range(0, c.NUM_COLS):
                tiles[(i, j)] = Tile(
                    canvas=self.canvas,
                    board_origin=(board_x, board_y),
                    pos=(i, j),
                    on_click=self.click_tile
                )
        
        ring_container_size_x, ring_container_size_y = c.RING_CONTAINER_SIZE
        ring_container_cx = board_x - ring_container_size_x / 2 - c.BOARD_CONTAINER_PADDING
        ring_container = self.canvas.create_image(
            ring_container_cx, cy, image=c.assets["ring_container"]
        )
        
        red_ring = self.canvas.create_image(
            ring_container_cx, cy - 175, image=c.assets["red_ring"]
        )
        blue_ring = self.canvas.create_image(
            ring_container_cx, cy- 10, image=c.assets["blue_ring"]
        )
        green_ring = self.canvas.create_image(
            ring_container_cx, cy + 150, image=c.assets["green_ring"]
        )

        self.canvas.tag_bind(red_ring, "<Button-1>", lambda _: self.click_ring(RingType.RED))
        self.canvas.tag_bind(green_ring, "<Button-1>", lambda _: self.click_ring(RingType.GREEN))
        self.canvas.tag_bind(blue_ring, "<Button-1>", lambda _: self.click_ring(RingType.BLUE))

        status_text = self.canvas.create_text(
            ring_container_cx,
            cy + ring_container_size_y/2 + 30,
            width=ring_container_size_x,
            justify="center",
            text="",
            fill="black",
            font="LuckiestGuy 18 bold"
        )

        self.canvas.pack()

        self.mounted = {
            "board_id": board,
            "ring_container_id": ring_container,
            "red_ring_id": red_ring,
            "green_ring_id": green_ring,
            "blue_ring_id": blue_ring,
            "status_text_id": status_text,
            "tiles": tiles,
        }
    
    def update_status_message(self, message: str):
        self.canvas.itemconfig(self.mounted["status_text_id"], text=message)
    
    def click_ring(self, ring: RingType):
        if self.selected_ring == ring:
            self.update_status_message(f"Unselected ring")
            self.selected_ring = None
            return

        self.selected_ring = ring
        ring_name = self.selected_ring.value if self.selected_ring else "None"
        self.update_status_message(f"Selected {ring_name} ring")
        
    
    def click_tile(self, tile: Tile):
        i, j = tile.pos
        self.update_status_message(f"Clicked position {i}, {j}")
        
    
    def update(self):
        if self.mounted is None:
            self.mount_board()

    @property
    def window_size(self) -> tuple[int, int]:
        return (self.window.winfo_width(), self.window.winfo_height())