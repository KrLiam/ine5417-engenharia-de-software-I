from enum import Enum, auto
from random import choice
import tkinter as tk
import requests
from typing import Any
import dog

from constants import Constants as c
from name import ADJECTIVES, NAMES
from game import Board, Cell, GameMatch, Player, RingType, MoveType, Movement
from button import Button
from ringstack import RingStack, RingType
from tile import Tile


class GameStatus(Enum):
    INIT = auto()
    FAIL_INIT = auto()
    START = auto()
    STARTING = auto()
    MATCH = auto()

class GamePlayerInterface(dog.DogPlayerInterface):
    __window: tk.Tk
    __canvas: tk.Canvas
    __dog_actor: dog.DogActor

    __mounted: dict[str, Any] | None
    __status: GameStatus | None = None
    __match: GameMatch | None = None

    __selected_ring: RingType | None
    __selected_cell_pos: tuple[int, int] | None
    __end_cells: list[Cell] | None = None
    __status_message: str

    def __init__(self):
        super().__init__()

        width, height = c.DEFAULT_SIZE
        
        self.__window = tk.Tk()
        self.__window.title(c.TITLE)
        self.__window.geometry(f"{width}x{height}")
        self.__window.resizable(c.RESIZABLE, c.RESIZABLE)
        self.__window.configure(bg=c.BACKGROUND_COLOR)

        self.__canvas = tk.Canvas(self.__window, width=width, height=height, background=c.BACKGROUND_COLOR)
        self.__canvas.pack()

        self.player_name = self.choose_player_name()

        self.restore_initial_state()

    @property
    def window_size(self) -> tuple[int, int]:
        return (self.__window.winfo_width(), self.__window.winfo_height())    

    def get_status(self):
        return self.__status

    def choose_player_name(self):
        gender, animal = choice(NAMES)
        adj_pair = choice(ADJECTIVES)

        return f"{animal} {adj_pair[gender.value]}"
    
    def clear_match(self):
        self.__match = None

    def restore_initial_state(self):
        self.clear_match()
        self.__mounted = {}

        self.__status_message = ""

        self.__selected_ring = None
        self.__selected_cell_pos = None

    def loop(self):
        self.__window.after(c.DELAY, self.initialize)

        self.__window.mainloop()

    def initialize(self):
        try:
            self.__dog_actor = dog.DogActor()
            connection_result = self.__dog_actor.initialize(self.player_name, self)
            self.update_status_message(connection_result)

            connected = self.process_connection_result(connection_result)
        except requests.exceptions.ConnectionError:
            self.update_status_message("Falha de conexão")

            connected = False

        if connected:
            self.mount_start_screen()
        else:
            self.mount_error_screen()
    
    def process_connection_result(self, connection_result: str):
        return connection_result == "Conectado a Dog Server"

    def mount_error_screen(self):
        self.__canvas.delete("all")
        self.__status = GameStatus.FAIL_INIT

        w, h = self.window_size

        status_text_id = self.__canvas.create_text(
            w/2,
            h/2 - 60,
            justify="center",
            text=f"Dog: {self.__status_message}",
            fill="black",
            font="LuckiestGuy 30 bold"
        )

        self.__mounted = {
            "status_text_id": status_text_id,
        }
    
    def mount_start_screen(self):
        self.__canvas.delete("all")
        self.__status = GameStatus.START

        w, h = self.window_size

        welcome_text_id = self.__canvas.create_text(
            w/2,
            h/2 - 100,
            justify="center",
            text=f"Olá, {self.player_name}!",
            fill="black",
            font="LuckiestGuy 30 bold"
        )

        start_button = Button(
            self.__canvas,
            center_pos=(w/2, h/2),
            size=(200, 75),
            message="Iniciar",
            on_click=lambda _: self.start_match()
        )
        status_text_id = self.__canvas.create_text(
            w/2,
            h/2 + 70,
            justify="center",
            text=self.__status_message,
            fill="black",
            font="LuckiestGuy 15 bold"
        )

        self.__mounted = {
            "welcome_text_id": welcome_text_id,
            "status_text_id": status_text_id,
            "start_button": start_button,
        }    

    def start_match(self):
        start_status = self.__dog_actor.start_match(2)

        code = start_status.get_code()

        if code == "2":
            self.initialize_match(start_status)
        else:
            start_message = start_status.get_message()
            self.update_status_message(start_message)
            self.mount_start_screen()

    def receive_start(self, start_status: dog.StartStatus):
        self.restore_initial_state()

        self.initialize_match(start_status)
    
    def initialize_match(self, start_status: dog.StartStatus):
        self.__match = GameMatch.from_start_status(start_status)

        self.mount_match_screen()

    
    def mount_match_screen(self):
        self.__canvas.delete("all")
        self.__status = GameStatus.MATCH

        w, h = self.window_size

        cx, cy = w/2, h/2
        board_x, board_y = cx - c.BOARD_SIZE/2, cy - c.BOARD_SIZE/2

        board = self.__canvas.create_image(
            cx, cy, image=c.assets["board"]
        )

        tiles: dict[tuple[int, int], Tile] = {}

        for i in range(0, c.NUM_ROWS):
            for j in range(0, c.NUM_COLS):
                tiles[(i, j)] = Tile(
                    canvas=self.__canvas,
                    board_origin=(board_x, board_y),
                    pos=(i, j),
                    on_click=self.click_tile
                )
        
        ring_container_size_x, ring_container_size_y = c.RING_CONTAINER_SIZE

        ring_container_cx = board_x - ring_container_size_x / 2 - c.BOARD_CONTAINER_PADDING
        ring_container = self.__canvas.create_image(
            ring_container_cx, cy, image=c.assets["ring_container"]
        )

        adv_ring_container_cx = cx + c.BOARD_SIZE/2 + ring_container_size_x/2 + c.BOARD_CONTAINER_PADDING
        adv_ring_container = self.__canvas.create_image(
            adv_ring_container_cx, cy, image=c.assets["ring_container"]
        )
        
        red_stack = RingStack(
            canvas=self.__canvas,
            pos=(ring_container_cx, cy - 175),
            ring_type=RingType.RED,
            on_click=self.click_ring_stack,
        )
        blue_stack = RingStack(
            canvas=self.__canvas,
            pos=(ring_container_cx, cy - 14),
            ring_type=RingType.BLUE,
            on_click=self.click_ring_stack,
        )
        green_stack = RingStack(
            canvas=self.__canvas,
            pos=(ring_container_cx, cy + 147),
            ring_type=RingType.GREEN,
            on_click=self.click_ring_stack,
        )

        adv_red_stack = RingStack(
            canvas=self.__canvas,
            pos=(adv_ring_container_cx, cy - 175),
            ring_type=RingType.RED,
        )
        adv_blue_stack = RingStack(
            canvas=self.__canvas,
            pos=(adv_ring_container_cx, cy - 14),
            ring_type=RingType.BLUE,
        )
        adv_green_stack = RingStack(
            canvas=self.__canvas,
            pos=(adv_ring_container_cx, cy + 147),
            ring_type=RingType.GREEN,
        )

        player_name_text = self.__canvas.create_text(
            ring_container_cx,
            cy + ring_container_size_y/2 + 5,
            width=ring_container_size_y,
            justify="center",
            text=f"{self.player_name}\n(Você)",
            fill="black",
            font="LuckiestGuy 18 bold"
        )

        remote_player = self.__match.get_remote_player()
        adversary_name = remote_player.get_name()
        adversary_name_text = self.__canvas.create_text(
            adv_ring_container_cx,
            cy + ring_container_size_y/2 - 5,
            width=ring_container_size_y,
            justify="center",
            text=adversary_name or "",
            fill="black",
            font="LuckiestGuy 18 bold"
        )

        status_text = self.__canvas.create_text(
            cx,
            cy - c.BOARD_SIZE/2 - 10,
            justify="center",
            text="",
            fill="black",
            font="LuckiestGuy 18 bold"
        )

        self.update_turn_marker()

        self.__canvas.pack()

        self.__mounted = {
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
            },
            "adv_stacks": {
                RingType.RED: adv_red_stack,
                RingType.GREEN: adv_green_stack,
                RingType.BLUE: adv_blue_stack,
            }
        }

    def update_match_screen(self):
        board = self.__match.get_board()

        cells = board.get_cells()

        for cell in cells:
            pos = cell.get_pos()
            tile = self.get_tile(pos)

            ring_set = cell.get_ring_set()
            tile.update_ring_set(ring_set)
        
        self.clear_overlay()

        if self.__selected_cell_pos:
            self.highlight_possible_movements()
        elif self.__end_cells:
            self.highlight_end_cells()
        
        for player in (self.__match.get_local_player(), self.__match.get_remote_player()):
            for ring_type in RingType:
                stack = self.get_ring_stack(player, ring_type)
                if not stack:
                    continue

                amount = player.get_ring_amount(ring_type)
                stack.set_count(amount)
        
        self.update_turn_marker()
    
    def update_turn_marker(self):
        self.__canvas.delete("turn-marker")

        if not self.__end_cells:
            w, h = self.window_size
            cx, cy = w/2, h/2
            ring_container_size_x, ring_container_size_y = c.RING_CONTAINER_SIZE
            x_offset = c.BOARD_SIZE/2 + c.BOARD_CONTAINER_PADDING + ring_container_size_x/2
            y = cy - ring_container_size_y / 2 - 75

            local_turn = self.__match.get_local_turn()

            if local_turn:
                x = cx - x_offset
                image = c.assets["local_turn"]
            else:
                x = cx + x_offset
                image = c.assets["remote_turn"]
            
            self.__canvas.create_image(x, y, image=image, tags=("turn-marker",))
            self.__canvas.pack()

    def clear_overlay(self):
        for i in range(4):
            for j in range(4):
                tile = self.get_tile((i, j))
                tile.clear_overlay()

    def highlight_possible_movements(self):
        board = self.__match.get_board()

        selected_cell = board.get_cell(*self.__selected_cell_pos)
        cells = board.get_cells()

        for cell in cells:
            can_move = selected_cell.can_move_to(cell)

            if can_move:
                pos = cell.get_pos()
                tile = self.get_tile(pos)

                tile.highlight_overlay()

    def highlight_end_cells(self):
        local_turn = self.__match.get_local_turn()

        for cell in self.__end_cells:
            pos = cell.get_pos()
            tile = self.get_tile(pos)

            if local_turn:
                tile.victory_overlay()
            else:
                tile.defeat_overlay()

    def mount_end_screen(self):
        board = self.__match.get_board()
        end_cells = board.check_end_condition()

        self.__canvas.delete("turn-marker")

        if end_cells:
            self.__end_cells = end_cells
            local_turn = self.__match.get_local_turn()

            if local_turn:
                self.update_status_message("Victory")
            else:
                self.update_status_message("Defeat")
        else:
            self.update_status_message("Adversary Escaped")
                
        w, h = self.window_size

        def return_button(_):
            self.restore_initial_state()
            self.mount_start_screen()

        button_y = h/2 + c.BOARD_SIZE/2 + 40
        button_id = Button(self.__canvas, (w/2, button_y), (160, 60), "Return", return_button)

        self.__canvas.pack()
        self.__mounted["return_button"] = button_id        


    def update_status_message(self, message: str):
        self.__status_message = message
        if self.__mounted.get("status_text_id"):
            self.__canvas.itemconfig(self.__mounted["status_text_id"], text=message)
    
    def get_tile(self, pos: tuple[int, int]) -> Tile:
        return self.__mounted["tiles"][pos]

    def get_ring_stack(self, player: Player, ring_type: RingType) -> RingStack:

        player_id = player.get_id()

        if player_id == self.__match.get_local_player().get_id():
            stacks = self.__mounted["stacks"]
        else:
            stacks = self.__mounted["adv_stacks"]

        return stacks[ring_type]

    def click_ring_stack(self, stack: RingStack):
        # Pre-condição para executar o select ring

        if not self.__match.get_local_turn():
            return
        
        if self.__selected_cell_pos:
            return
        
        self.select_ring(stack.get_ring_type())
    
    def click_tile(self, tile: Tile):
        # Pre condição para executar o select destination ou select cell
        
        if not self.__match.get_local_turn():
            return

        if self.__selected_ring or self.__selected_cell_pos:
            return self.select_destination(tile.get_pos())
        
        return self.select_cell(tile.get_pos())

    def select_ring(self, ring_type: RingType):
        selected_ring = self.__selected_ring

        if selected_ring:
            self.unselect_ring()
        
        if selected_ring != ring_type:
            local_player = self.__match.get_local_player()
            clicked_stack = self.get_ring_stack(local_player, ring_type)
            
            count = clicked_stack.get_count()
            
            if count > 0:
                self.__selected_ring = ring_type
                ring_name = self.__selected_ring.value if self.__selected_ring else "None"        
                self.update_status_message(f"Selected {ring_name} ring")
        
        self.update_match_screen()
    
    def unselect_ring(self):
        self.update_status_message(f"Unselected ring")
        self.__selected_ring = None
    
    def evaluate_game_end(self) -> bool:
        game_ended = self.__match.evaluate_round()

        if game_ended:            
            self.mount_end_screen()
        
        return game_ended

    def select_cell(self, clicked_pos: tuple[int, int]):
        board =  self.__match.get_board()

        clicked_cell = board.get_cell(*clicked_pos)

        empty = clicked_cell.is_empty()
        
        if not empty:
            self.__selected_cell_pos = clicked_pos
        
        self.update_match_screen()

    def unselect_cell(self):
        self.__selected_cell_pos = None

    def select_destination(self, clicked_pos: tuple[int, int]):
        ring_type = self.__selected_ring
        selected_pos = self.__selected_cell_pos

        move = None

        if ring_type:
            local_player = self.__match.get_local_player()
            move = self.__match.place_ring(ring_type, clicked_pos, local_player)
        elif selected_pos:
            if selected_pos != clicked_pos:
                move = self.__match.move_cell_content(selected_pos, clicked_pos)
            else:
                self.unselect_cell()

        self.__selected_ring = None
        self.__selected_cell_pos = None

        if move is not None:
            end = self.evaluate_game_end()

            if end:
                move.set_match_status("finished")
            else:
                move.set_match_status("next")
            
            move_dict = move.to_dict()
            
            self.__dog_actor.send_move(move_dict)
        
        self.update_match_screen()
    
    def receive_move(self, move_dict: dict[str, Any]):
        move = Movement.from_dict(move_dict)

        self.__match.receive_move(move)

        self.evaluate_game_end()

        self.update_match_screen()

    def receive_withdrawal_notification(self):
        self.mount_end_screen()
