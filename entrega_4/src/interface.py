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
            MoveType(type),
            destination,
            origin,
            RingType(ring_type) if ring_type else None,
            match_status
        )


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
    
    def selected(self):
        ...

    def unselected(self):
        ...


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

        self.player_name = self.choose_player_name()

        self.restore_initial_state()
        self.mount_init() # mover isso pro loop posteriormente

    @property
    def window_size(self) -> tuple[int, int]:
        return (self.window.winfo_width(), self.window.winfo_height())    

    def choose_player_name(self):
        gender, animal = choice(NAMES)
        adj_pair = choice(ADJECTIVES)

        return f"{animal} {adj_pair[gender.value]}"
    
    def clear_match(self):
        self.match = None

    def restore_initial_state(self):
        self.clear_match()
        self.mounted = None

        self.status_message = ""

        self.selected_ring = None
        self.selected_cell_pos = None


    def loop(self):
        # a tela de init fica zoada se montada antes do tkinter executar o loop
        # isso é problema pra "resolver" só depois :)
        # def callback():
        #     self.mount_init()
        # self.window.after(c.DELAY, callback)

        self.window.mainloop()


    def mount_init(self):
        self.canvas.delete("all")
        self.status = GameStatus.INIT

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
            self.mount_error_screen()
            return

        self.dog_message = message

        if message == "Conectado a Dog Server":
            self.mount_start_screen()
        else:
            self.mount_error_screen()


    def mount_error_screen(self):
        self.canvas.delete("all")
        self.status = GameStatus.FAIL_INIT

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
            on_click=lambda _: self.mount_init()
        )

        self.mounted = {
            "dog_text_id": dog_text_id,
            "retry_button": retry_button,
        }
    def mount_start_screen(self):
        self.canvas.delete("all")
        self.status = GameStatus.START

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
            on_click=lambda _: self.mount_starting_match()
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

    def mount_starting_match(self):
        self.canvas.delete("all")
        self.status = GameStatus.STARTING

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
            self.initialize_match(start)
            return

        self.dog_message = start.get_message()
        self.mount_start_screen()

    def receive_start(self, start_status: dog.StartStatus):
        self.restore_initial_state()

        self.initialize_match(start_status)
    
    def initialize_match(self, start_status: dog.StartStatus):
        self.match = GameMatch.from_start_status(start_status)

        self.mount_match_screen()

    
    def mount_match_screen(self):
        self.canvas.delete("all")
        self.status = GameStatus.MATCH

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

        remote_player = self.match.get_remote_player()
        adversary_name = remote_player.get_name()
        adversary_name_text = self.canvas.create_text(
            adv_ring_container_cx,
            cy + ring_container_size_y/2 - 5,
            width=ring_container_size_y,
            justify="center",
            text=adversary_name or "",
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
            "stacks": {
                RingType.RED: red_stack,
                RingType.GREEN: green_stack,
                RingType.BLUE: blue_stack,
            }
        }

    def update_match_screen(self):
        board = self.match.get_board()

        for cell in board.get_cells():
            pos = cell.get_pos()
            tile = self.get_tile(pos)

            ring_set = cell.get_ring_set()
            tile.update_ring_set(ring_set)
        
        for player in (self.match.local_player, self.match.remote_player):
            for ring_type in RingType:
                stack = self.get_ring_stack(player, ring_type)
                if not stack:
                    continue

                amount = player.get_ring_amount(ring_type)
                stack.set_amount(amount)


    def mount_end_screen(self):
        board = self.match.get_board()
        end = board.check_end_condition()

        if end:
            local_turn = self.match.get_local_turn()

            if local_turn:
                self.update_status_message("Victory")
            else:
                self.update_status_message("Defeat")

            for cell in end:
                pos = cell.get_pos()
                tile = self.get_tile(pos)

                if local_turn:
                    tile.victory_overlay()
                else:
                    tile.defeat_overlay()
        else:
            self.update_status_message("Adversary Escaped")
        
        w, h = self.window_size

        button_y = h/2 + c.BOARD_SIZE/2 + 40
        button_id = Button(self.canvas, (w/2, button_y), (160, 60), "Return", lambda _: self.mount_start_screen())
        self.mounted["return_button"] = button_id        


    def update_status_message(self, message: str):
        self.canvas.itemconfig(self.mounted["status_text_id"], text=message)
    
    def get_tile(self, pos: tuple[int, int]) -> Tile:
        return self.mounted["tiles"][pos]

    def get_ring_stack(self, player: Player, ring_type: RingType) -> RingStack:
        stacks = self.mounted["stacks"]

        player_id = player.get_id()

        if player_id == self.match.local_player.get_id():
            return stacks[ring_type]
        
        return None

    def click_ring_stack(self, stack: RingStack):
        if not self.match.local_turn:
            self.update_status_message("Not Your Turn")
            return
        
        self.select_ring(stack.ring_type)
    
    def select_ring(self, ring_type: RingType):
        selected_ring = self.selected_ring

        if selected_ring:
            self.unselect_ring()
        
        if selected_ring != ring_type:
            local_player = self.match.get_local_player()
            clicked_stack = self.get_ring_stack(local_player, ring_type)
            
            count = clicked_stack.amount
            
            if count > 0:
                self.selected_ring = ring_type
                ring_name = self.selected_ring.value if self.selected_ring else "None"        
                self.update_status_message(f"Selected {ring_name} ring")
    
    def unselect_ring(self):
        selected_ring = self.selected_ring

        selected_stack = self.get_ring_stack(self.match.local_player, selected_ring)
        selected_stack.unselected()

        self.selected_ring = None
        self.update_status_message(f"Unselected ring")


    def click_tile(self, tile: Tile):
        if not self.match.local_turn:
            self.update_status_message("Not Your Turn")
            return

        if self.selected_ring or self.selected_cell_pos:
            return self.select_destination(tile.pos)
        
        return self.select_cell(tile.pos)
    
    def clear_overlay(self):
        for i in range(4):
            for j in range(4):
                tile = self.get_tile((i, j))
                tile.clear_overlay()

    def highlight_possible_movements(self, board: Board, clicked_cell: Cell):
        for cell in board.get_cells():
            if cell is clicked_cell:
                continue

            if not clicked_cell.can_move_to(cell):
                continue

            pos = cell.get_pos()
            tile = self.get_tile(pos)

            tile.highlight_overlay()

    def evaluate_game_end(self) -> bool:
        board = self.match.get_board()
        end = board.check_end_condition()

        if end:            
            self.mount_end_screen()
        else:
            local_turn = self.match.switch_turn()

            if local_turn:
                self.update_status_message("Your Turn")
            else:
                self.update_status_message("Their Turn")
        
        return end


    def select_cell(self, clicked_pos: tuple[int, int]):
        board =  self.match.get_board()

        clicked_cell = board.get_cell(*clicked_pos)

        if clicked_cell.is_empty():
            return

        clicked_tile = self.get_tile(clicked_pos)

        clicked_tile.highlight_overlay()
        self.selected_cell_pos = clicked_pos
        self.update_status_message(f"selected cell {self.selected_cell_pos}")

        self.highlight_possible_movements(board, clicked_cell)

    def unselect_cell(self):
        self.selected_cell_pos = None
        self.clear_overlay()

    def select_destination(self, clicked_pos: tuple[int, int]):
        ring_type = self.selected_ring
        selected_pos = self.selected_cell_pos

        move = None

        if ring_type:
            local_player = self.match.local_player
            move = self.place_ring(ring_type, clicked_pos, local_player)
        elif selected_pos:
            if selected_pos != clicked_pos:
                move = self.move_cell_content(selected_pos, clicked_pos)
            else:
                self.unselect_cell()

        self.selected_ring = None
        self.selected_cell_pos = None
        self.clear_overlay()

        if move is not None:
            end = self.evaluate_game_end()

            if end:
                move.set_match_status("finished")
            else:
                move.set_match_status("next")
            
            move_dict = move.to_dict()
            
            thread = Thread(target=lambda: self.dog_actor.send_move(move_dict))
            thread.start()
            self.mounted["send_thread"] = thread
        
        self.update_match_screen()
        
    def place_ring(self, ring_type: RingType, destination_pos: tuple[int, int], player: Player):
        board = self.match.get_board()

        inserted = board.insert_ring(destination_pos, ring_type)

        if not inserted:
            return None
        
        player.consume_ring(ring_type)

        return Movement(
            type=MoveType.PLACE_RING,
            destination=destination_pos,
            ring_type=ring_type
        )
    
    def move_cell_content(self, origin_pos: tuple[int, int], destination_pos: tuple[int, int]):
        board = self.match.get_board()

        moved = board.move(origin_pos, destination_pos)

        if not moved:
            return None
    
        return Movement(
            type=MoveType.MOVE_CELL_CONTENT,
            origin=origin_pos,
            destination=destination_pos,
        )

    def receive_move(self, move_dict: dict[Any, Any]):
        move = Movement.from_dict(move_dict)

        if move.type == MoveType.PLACE_RING:
            remote_player = self.match.remote_player
            self.place_ring(move.ring_type, move.destination, remote_player)
        elif move.type == MoveType.MOVE_CELL_CONTENT:
            self.move_cell_content(move.origin, move.destination)
        
        self.evaluate_game_end()
        
        self.update_match_screen()

    def receive_withdrawal_notification(self):
        self.mount_end_screen()