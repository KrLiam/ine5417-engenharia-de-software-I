from dataclasses import dataclass, field
from enum import Enum, auto
from random import choice
from threading import Thread
import tkinter as tk
import requests
from typing import Any, Callable, ClassVar, Literal
from constants import Constants as c
import dog
from name import ADJECTIVES, NAMES
from game import Board, Cell, GameMatch, Player, RingType
class GameStatus(Enum):
    INIT = auto()
    FAIL_INIT = auto()
    START = auto()
    STARTING = auto()
    MATCH = auto()
class MoveType(Enum):
    PLACE_RING = 0
    MOVE_CELL_CONTENT = 1
class Movement:
    match_status: str | None
    type: MoveType
    ring_type: RingType | None
    origin: tuple[int, int] | None
    destination: tuple[int, int]

    def __init__(
        self,
        type: MoveType,
        destination: tuple[int, int],
        origin: tuple[int, int] | None = None,
        ring_type: RingType | None = None,
        match_status: str | None = None
    ):
        self.type = type
        self.ring_type = ring_type
        self.origin = origin
        self.destination = destination
        self.match_status = match_status

    def get_type(self) -> MoveType:
        return self.move_type

    def get_ring_type(self) -> RingType:
        return self.ring_type

    def get_origin(self) -> tuple[int, int]:
        return self.origin

    def get_destination(self) -> tuple[int, int]:
        return self.destination
    
    def get_match_status(self) -> str:
        return self.match_status
    
    def set_match_status(self, match_status: str):
        self.match_status = match_status
    
    def to_dict(self):
        return {
            "match_status": self.match_status,
            "type": self.type.value,
            "destination": list(self.destination),
            "origin": list(self.origin) if self.origin else None,
            "ring_type": self.ring_type.value if self.ring_type else None,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Movement":
        match_status = value.get("match_status")
        type = value.get("type")
        destination = value.get("destination")
        origin = value.get("origin")
        ring_type = value.get("ring_type")

        return Movement(
            type,
            destination,
            origin,
            ring_type,
            match_status
        )


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
    
    def selected(self):
        ...
    
    def highlight(self):
        ...


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
            text=self.amount
        )

        self.canvas.tag_bind(self.ring_id, "<Button-1>", self.click)
    
    def click(self, event: tk.Event):
        if self.on_click:
            self.on_click(self)
    
    def set_amount(self, amount: int):
        self.amount = amount
        self.canvas.itemconfig(self.text_id, text=self.amount)


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

class GamePlayerInterface(dog.DogPlayerInterface):
    window: tk.Tk
    canvas: tk.Canvas
    dog_actor: dog.DogActor

    mounted: dict[str, Any] | None
    status: GameStatus | None = None
    match: GameMatch | None = None
    next_status: GameStatus | None = None
    start_status: dog.StartStatus | None
    dog_message: str

    selected_ring: RingType | None
    selected_cell_pos: tuple[int, int] | None
    status_message: str

    def __init__(self):
        super().__init__()

        width, height = c.DEFAULT_SIZE
        
        self.window = tk.Tk()
        self.window.title(c.TITLE)
        self.window.geometry(f"{width}x{height}")
        self.window.resizable(c.RESIZABLE, c.RESIZABLE)
        self.window.configure(bg=c.BACKGROUND_COLOR)

        self.canvas = tk.Canvas(self.window, width=width, height=height, background=c.BACKGROUND_COLOR)
        self.canvas.pack()

        self.start_status = None
        self.player_name = self.choose_player_name()

        self.restore_initial_state()

    @property
    def window_size(self) -> tuple[int, int]:
        return (self.window.winfo_width(), self.window.winfo_height())

    @property
    def adversary_name(self) -> str | None:
        if not self.start_status:
            return None
        
        players = self.start_status.get_players()

        for name, player_id, _ in players:
            if player_id != self.start_status.local_id:
                return name
    

    def choose_player_name(self):
        gender, animal = choice(NAMES)
        adj_pair = choice(ADJECTIVES)

        return f"{animal} {adj_pair[gender.value]}"


    def restore_initial_state(self):
        self.next_status = GameStatus.INIT
        self.mounted = None

        self.selected_ring = None
        self.selected_cell_pos = None

        self.status_message = ""

    def loop(self):
        def callback():
            self.update()
            self.window.after(c.DELAY, callback)

        self.window.after(c.DELAY, callback)
        self.window.mainloop()

    def unmount(self):
        self.canvas.delete("all")

    def update(self):
        if self.next_status:
            self.unmount()

            if self.next_status == GameStatus.INIT:
                self.mount_init()
            elif self.next_status == GameStatus.FAIL_INIT:
                self.mount_fail_init()
            elif self.next_status == GameStatus.START:
                self.mount_start()
            elif self.next_status == GameStatus.STARTING:
                self.mount_starting_match()
            elif self.next_status == GameStatus.MATCH:
                self.mount_board()

            self.status = self.next_status
            self.next_status = None


    def receive_withdrawal_notification(self):
        ...


    def mount_init(self):
        w, h = self.window_size

        text_id = self.canvas.create_text(
            w/2,
            h/2,
            justify="center",
            text=f"Dog: Conectando...",
            fill="black",
            font="LuckiestGuy 30 bold"
        )

        thread = Thread(target=self.initialize)
        thread.start()

        self.mounted = {
            "text_id": text_id,
            "thread": thread
        }

    def initialize(self):
        try:
            self.dog_actor = dog.DogActor()
            message = self.dog_actor.initialize(self.player_name, self)
        except requests.exceptions.ConnectionError:
            self.dog_message = "Falha de conexão"
            self.next_status = GameStatus.FAIL_INIT
            return

        self.dog_message = message

        if message == "Conectado a Dog Server":
            self.next_status = GameStatus.START
        else:
            self.next_status = GameStatus.FAIL_INIT


    def mount_fail_init(self):
        w, h = self.window_size

        dog_text_id = self.canvas.create_text(
            w/2,
            h/2 - 60,
            justify="center",
            text=f"Dog: {self.dog_message}",
            fill="black",
            font="LuckiestGuy 30 bold"
        )

        retry_button = Button(
            self.canvas,
            center_pos=(w/2, h/2),
            size=(400, 75),
            message="Tentar Novamente",
            on_click=self.clicked_retry_init
        )

        self.mounted = {
            "dog_text_id": dog_text_id,
            "retry_button": retry_button,
        }
    
    def clicked_retry_init(self, _: Button):
        self.next_status = GameStatus.INIT


    def mount_start(self):
        w, h = self.window_size

        welcome_text_id = self.canvas.create_text(
            w/2,
            h/2 - 100,
            justify="center",
            text=f"Olá, {self.player_name}!",
            fill="black",
            font="LuckiestGuy 30 bold"
        )

        start_button = Button(
            self.canvas,
            center_pos=(w/2, h/2),
            size=(200, 75),
            message="Iniciar",
            on_click=self.clicked_start
        )
        dog_text_id = self.canvas.create_text(
            w/2,
            h/2 + 70,
            justify="center",
            text=f"Dog: {self.dog_message}",
            fill="black",
            font="LuckiestGuy 15 bold"
        )

        self.mounted = {
            "welcome_text_id": welcome_text_id,
            "dog_text_id": dog_text_id,
            "start_button": start_button,
        }
    
    def clicked_start(self, _: Button):
        self.next_status = GameStatus.STARTING
    

    def mount_starting_match(self):
        w, h = self.window_size

        text_id = self.canvas.create_text(
            w/2,
            h/2,
            justify="center",
            text=f"Iniciando partida...",
            fill="black",
            font="LuckiestGuy 30 bold"
        )

        thread = Thread(target=self.start_match)
        thread.start()

        self.mounted = {
            "text_id": text_id,
            "thread": thread
        }

    def start_match(self):
        start = self.dog_actor.start_match(2)

        if start.code == "2":
            self.next_status = GameStatus.MATCH
            self.start_status = start
            self.match = GameMatch.from_start_status(start)
            return

        self.dog_message = start.get_message()
        self.next_status = GameStatus.START



    def receive_start(self, start_status: dog.StartStatus):
        self.next_status = GameStatus.MATCH
        self.start_status = start_status
        self.match = GameMatch.from_start_status(start_status)

    
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

        adv_ring_container_cx = cx + c.BOARD_SIZE/2 + ring_container_size_x/2 + c.BOARD_CONTAINER_PADDING
        adv_ring_container = self.canvas.create_image(
            adv_ring_container_cx, cy, image=c.assets["ring_container"]
        )
        
        red_stack = RingStack(
            canvas=self.canvas,
            pos=(ring_container_cx, cy - 175),
            ring_type=RingType.RED,
            on_click=self.click_ring_stack,
        )
        blue_stack = RingStack(
            canvas=self.canvas,
            pos=(ring_container_cx, cy - 14),
            ring_type=RingType.BLUE,
            on_click=self.click_ring_stack,
        )
        green_stack = RingStack(
            canvas=self.canvas,
            pos=(ring_container_cx, cy + 147),
            ring_type=RingType.GREEN,
            on_click=self.click_ring_stack,
        )

        player_name_text = self.canvas.create_text(
            ring_container_cx,
            cy + ring_container_size_y/2 + 5,
            width=ring_container_size_y,
            justify="center",
            text=f"{self.player_name}\n(Você)",
            fill="black",
            font="LuckiestGuy 18 bold"
        )
        adversary_name_text = self.canvas.create_text(
            adv_ring_container_cx,
            cy + ring_container_size_y/2 - 5,
            width=ring_container_size_y,
            justify="center",
            text=self.adversary_name or "",
            fill="black",
            font="LuckiestGuy 18 bold"
        )

        status_text = self.canvas.create_text(
            cx,
            cy - c.BOARD_SIZE/2 - 10,
            justify="center",
            text="",
            fill="black",
            font="LuckiestGuy 18 bold"
        )

        self.canvas.pack()

        self.mounted = {
            "board_id": board,
            "ring_container_id": ring_container,
            "adv_ring_container_id": adv_ring_container,
            "status_text_id": status_text,
            "player_name_text_id": player_name_text,
            "adversary_name_text_id": adversary_name_text,
            "tiles": tiles,
            "stacks": (red_stack, blue_stack, green_stack)
        }
    
    def update_status_message(self, message: str):
        self.canvas.itemconfig(self.mounted["status_text_id"], text=message)
    
    def get_tile(self, pos: tuple[int, int]) -> Tile:
        return self.mounted["tiles"][pos]
    
    def click_ring_stack(self, stack: RingStack):
        if self.selected_ring == stack.ring_type:
            self.update_status_message(f"Unselected ring")
            self.selected_ring = None
            return

        self.selected_ring = stack.ring_type
        ring_name = self.selected_ring.value if self.selected_ring else "None"        
        self.update_status_message(f"Selected {ring_name} ring")
        
    def click_tile(self, tile: Tile):
        if self.selected_ring or self.selected_cell_pos:
            return self.select_destination(tile.pos)
        
        return self.select_cell(tile.pos)
    
    def select_cell(self, clicked_pos: tuple[int, int]):
        board =  self.match.get_board()

        clicked_cell = board.get_cell(*clicked_pos)

        if clicked_cell.is_empty():
            return

        clicked_tile = self.get_tile(clicked_pos)

        clicked_tile.selected()
        self.selected_cell_pos = clicked_pos
        self.update_status_message(f"selected cell {self.selected_cell_pos}")

        self.highlight_possible_movements(board, clicked_cell)

    def select_destination(self, clicked_pos: tuple[int, int]):
        ring_type = self.selected_ring
        selected_pos = self.selected_cell_pos

        move = None

        if ring_type:
            local_player = self.match.local_player
            move = self.place_ring(ring_type, clicked_pos, local_player)
        elif selected_pos:
            selected_cell = self.match.board.get_cell(*selected_pos)

            if selected_pos != clicked_pos:
                move = self.move_cell_content(selected_pos, clicked_pos)
            else:
                selected_cell.unselect()
        
        if move is not None:
            end = self.evaluate_game_end()

            if end:
                move.set_match_status("finish")
            else:
                move.set_match_status("next")
            
            move_dict = move.to_dict()
            print("sending move", move_dict)

            self.dog_actor.send_move(move_dict)
    
    def evaluate_game_end(self) -> bool:
        ...
    
    def highlight_possible_movements(self, board: Board, clicked_cell: Cell):
        for cell in board.get_cells():
            if cell is clicked_cell:
                continue

            if not clicked_cell.can_move_to(cell):
                continue

            pos = cell.get_pos()
            tile = self.get_tile(pos)

            tile.highlight()
    
    def place_ring(self, ring_type: RingType, destination_pos: tuple[int, int], player: Player):

        return Movement(
            type=MoveType.PLACE_RING,
            destination=destination_pos,
            ring_type=ring_type
        )
    
    def move_cell_content(self, origin_pos: tuple[int, int], destination_pos: tuple[int, int]):
        ...

    def receive_move(self, move_dict: dict[Any, Any]):
        move = Movement.from_dict(move_dict)

        print("received move", move_dict)

