import tkinter as tk

class Constants:
    TITLE = "Conjunto" # Title for the window
    DEFAULT_SIZE = (1920, 1080) # Default size for the window
    RESIZABLE = True  # Whether the window is resizable or not
    DELAY = 15 # Delay for the main loop
    BACKGROUND_COLOR = '#CDDFA0'
    # Dimensions for the board
    BOARD_WIDTH = 800
    BOARD_HEIGHT = 600

    NUM_ROWS = 4
    NUM_COLS = 4

    WIDTH = DEFAULT_SIZE[0]
    HEIGHT = DEFAULT_SIZE[1]

    # Calcular proporções com base na tela de referência de 1920x1080
    BOARD_TOP = HEIGHT * (168 / 1080)
    BOARD_BOTTOM = HEIGHT * (178 / 1080)
    BOARD_LEFT = WIDTH * (593 / 1920)
    BOARD_RIGHT = WIDTH * (593 / 1920)

    CONTAINER_EMPTY_TOP = HEIGHT * (240 / 1080)
    CONTAINER_EMPTY_BOTTOM = HEIGHT * (101 / 1080)
    CONTAINER_EMPTY_LEFT = WIDTH * (72 / 1920)
    CONTAINER_EMPTY_RIGHT = WIDTH * (1437 / 1920)

    CONTAINER_EMPTY_ADVERSARY_TOP = HEIGHT * (240 / 1080)
    CONTAINER_EMPTY_ADVERSARY_BOTTOM = HEIGHT * (101 / 1080)
    CONTAINER_EMPTY_ADVERSARY_LEFT = WIDTH * (1437 / 1920)
    CONTAINER_EMPTY_ADVERSARY_RIGHT = WIDTH * (72 / 1920)

    RED_RING_PATH = "assets/red_ring.png"
    BLUE_RING_PATH = "assets/blue_ring.png"
    GREEN_RING_PATH = "assets/green_ring.png"
    CONTAINER_EMPTY_PATH = "assets/container_empty.png"
    CONTAINER_EMPTY_ADVERSARY_PATH = "assets/container_empty_adversary.png"
    CONTAINER_COMPLETE_WITH_RINGS_PATH = "assets/container_complete_with_rings.png"
    CONTAINER_COMPLETE_WITH_RINGS_ADVERSARY_PATH = "assets/container_complete_with_rings_adversary.png"
    CONTAINER_COMPLETE_WITHOUT_RINGS_PATH = "assets/container_complete_without_rings.png"
    CONTAINER_COMPLETE_WITHOUT_RINGS_ADVERSARY_PATH = "assets/container_complete_without_rings_adversary.png"
    SUA_VEZ_PATH = "assets/sua_vez.png"
    VEZ_DO_ADVERSARIO_PATH = "assets/vez_do_adversario.png"
