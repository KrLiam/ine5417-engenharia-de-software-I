from functools import cache
import tkinter as tk
from PIL import Image, ImageTk

class Constants:
    TITLE = "Conjunto" # Title for the window
    DEFAULT_SIZE = (1600, 900) # Default size for the window
    RESIZABLE = True  # Whether the window is resizable or not
    DELAY = 15 # Delay for the main loop
    BACKGROUND_COLOR = '#CDDFA0'

    NUM_ROWS = 4
    NUM_COLS = 4

    BOARD_CONTAINER_PADDING = 30

    BOARD_PATH = "assets/board.png"
    # Dimensions for the board
    BOARD_SIZE = 780
    BOARD_OUTLINE_SIZE = 42.5
    BOARD_TILE_OUTLINE = 5
    BOARD_TILE_SIZE = 170

    RING_CONTAINER_PATH = "assets/ring_container.png"
    RING_CONTAINER_SIZE = (300, 700)

    RED_RING_PATH = "assets/red_ring.png"
    BLUE_RING_PATH = "assets/blue_ring.png"
    GREEN_RING_PATH = "assets/green_ring.png"
    CONTAINER_EMPTY_PATH = "assets/container_empty.png"
    CONTAINER_EMPTY_ADVERSARY_PATH = "assets/container_empty_adversary.png"
    CONTAINER_COMPLETE_WITH_RINGS_PATH = "assets/container_complete_with_rings.png"
    CONTAINER_COMPLETE_WITH_RINGS_ADVERSARY_PATH = "assets/container_complete_with_rings_adversary.png"
    CONTAINER_COMPLETE_WITHOUT_RINGS_ADVERSARY_PATH = "assets/container_complete_without_rings_adversary.png"
    SUA_VEZ_PATH = "assets/sua_vez.png"
    VEZ_DO_ADVERSARIO_PATH = "assets/vez_do_adversario.png"

    HOVER_COLOR = (255, 196, 64)

    @classmethod
    @property
    @cache
    def assets(cls) -> dict[str, tk.PhotoImage]:
        return {
            "board": tk.PhotoImage(file=cls.BOARD_PATH),
            "selected_tile_overlay": ImageTk.PhotoImage(
                Image.new(
                    mode="RGBA",
                    size=(cls.BOARD_TILE_SIZE, cls.BOARD_TILE_SIZE),
                    color=(*cls.HOVER_COLOR, 128)
                )
            ),
            "unselected_tile_overlay": ImageTk.PhotoImage(
                Image.new(
                    mode="RGBA",
                    size=(cls.BOARD_TILE_SIZE, cls.BOARD_TILE_SIZE),
                    color=(*cls.HOVER_COLOR, 0)
                )
            ),
            "ring_container": tk.PhotoImage(file=cls.RING_CONTAINER_PATH),
            "blue_ring": tk.PhotoImage(file=cls.BLUE_RING_PATH),
            "red_ring": tk.PhotoImage(file=cls.RED_RING_PATH),
            "green_ring": tk.PhotoImage(file=cls.GREEN_RING_PATH),
        }
