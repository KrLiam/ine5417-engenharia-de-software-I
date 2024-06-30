from dataclasses import dataclass, field
from enum import Enum
from dog import StartStatus
from typing import Any, Union


class MoveType(Enum):
    PLACE_RING = 0
    MOVE_CELL_CONTENT = 1

class Movement:
    __match_status: str | None
    __type: MoveType
    __ring_type: Union["RingType", None]
    __origin: tuple[int, int] | None
    __destination: tuple[int, int]

    def __init__(
        self,
        type: MoveType,
        destination: tuple[int, int],
        origin: tuple[int, int] | None = None,
        ring_type: Union["RingType", None] = None,
        match_status: str | None = None
    ):
        self.__type = type
        self.__ring_type = ring_type
        self.__origin = origin
        self.__destination = destination
        self.__match_status = match_status

    def get_move_type(self) -> MoveType:
        return self.__type

    def get_ring_type(self) -> "RingType":
        return self.__ring_type

    def get_origin_pos(self) -> tuple[int, int]:
        return self.__origin

    def get_destination_pos(self) -> tuple[int, int]:
        return self.__destination
    
    def get_match_status(self) -> str:
        return self.__match_status
    
    def set_match_status(self, match_status: str):
        self.__match_status = match_status
    
    def to_dict(self):
        return {
            "match_status": self.__match_status,
            "type": self.__type.value,
            "destination": list(self.__destination),
            "origin": list(self.__origin) if self.__origin else None,
            "ring_type": self.__ring_type.value if self.__ring_type else None,
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


def sign(x: int | float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0

class RingType(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"


@dataclass
class Player:
    __name: str
    __id: str
    __red_amount: int = field(init=False, default=16)
    __green_amount: int = field(init=False, default=16)
    __blue_amount: int = field(init=False, default=16)

    def get_name(self) -> str:
        return self.__name

    def get_id(self) -> str:
        return self.__id

    def get_ring_amount(self, ring_type: RingType) -> int:
        if ring_type == RingType.RED:
            return self.__red_amount
        if ring_type == RingType.GREEN:
            return self.__green_amount
        return self.__blue_amount


    def consume_ring(self, ring_type: RingType):
        if ring_type == RingType.RED:
            self.__red_amount = max(self.__red_amount - 1, 0)
        elif ring_type == RingType.GREEN:
            self.__green_amount = max(self.__green_amount - 1, 0)
        else:
            self.__blue_amount = max(self.__blue_amount - 1, 0)


class Board:
    __cells: list["Cell"]

    def __init__(self):
        self.__cells = []

        for i in range(4):
            for j in range(4):
                self.__cells.append(Cell(self, (i, j)))
    
    def get_cells(self) -> tuple["Cell", ...]:
        return tuple(self.__cells)
    
    def get_cell(self, i: int, j: int) -> "Cell":
        return self.__cells[i*4 + j]

    def get_rows(self):
        return tuple(
            tuple(self.get_cell(i, j) for j in range(4))
            for i in range(4)
        )
    
    def get_columns(self):
        return tuple(
            tuple(self.get_cell(i, j) for i in range(4))
            for j in range(4)
        )

    def get_diagonals(self):
        return (
            tuple(self.get_cell(i, i) for i in range(4)),
            tuple(self.get_cell(3 - i, i) for i in range(4)),
        )

    def move(self, origin_pos: tuple[int, int], destination_pos: tuple[int, int]) -> bool:
        origin_cell = self.get_cell(*origin_pos)
        destination_cell = self.get_cell(*destination_pos)

        if origin_cell.is_empty():
            return False
        
        if not origin_cell.can_move_to(destination_cell):
            return False
        
        ring_set = origin_cell.get_ring_set()
        destination_cell.set_ring_set(ring_set)
        origin_cell.clear()

        return True
    
    def check_end_condition(self) -> tuple["Cell", ...] | None:
        sequences = self.get_rows() + self.get_columns() + self.get_diagonals()

        for sequence in sequences:
            a, b, c, d = sequence

            if not a.is_empty() and a == b == c == d:
                return sequence
        
        return None


    def __repr__(self):
        lines: list[str] = []

        lines.append("  0     1     2     3")

        for i in range(4):
            line = str(i)

            for j in range(4):
                cell = self.get_cell(i, j)

                red = "R" if cell.has_ring(RingType.RED) else " "
                green = "G" if cell.has_ring(RingType.GREEN) else " "
                blue = "B" if cell.has_ring(RingType.BLUE) else " "

                line += " [" + red + green + blue + "]"
            
            lines.append(line)
        
        return "\n".join(lines)


@dataclass(init=False)
class Cell:
    __board: Board = field(repr=False)
    __pos: tuple[int, int]
    __rings: set[RingType]

    def __init__(self, board: Board, pos: tuple[int, int]):
        self.__board = board
        self.__pos = pos
        self.__rings = set()
    
    def __eq__(self, other: "Cell") -> bool:
        return self.__rings == other.get_ring_set()
    
    def get_pos(self) -> tuple[int, int]:
        return self.__pos

    def get_ring_set(self) -> set[RingType]:
        return set(self.__rings)
    
    def has_ring(self, ring_type: RingType) -> bool:
        return ring_type in self.__rings

    def is_empty(self) -> bool:
        return not self.__rings

    def insert_ring(self, ring_type: RingType):
        self.__rings.add(ring_type)
    
    def clear(self):
        self.__rings.clear()
    
    def set_ring_set(self, ring_set: set[RingType]):
        self.__rings.clear()
        self.__rings.update(ring_set)

    def can_move_to(self, other_cell: "Cell") -> bool:
        pos = self.__pos
        other_pos = other_cell.get_pos()
                
        dx = other_pos[0] - pos[0]
        dy = other_pos[1] - pos[1]

        valid_direction = dx == 0 or dy == 0 or abs(dx) == abs(dy)

        if pos != other_pos and valid_direction:
            distance = max(abs(dx), abs(dy))

            for i in range(1, distance + 1):
                x = pos[0] + i*sign(dx)
                y = pos[1] + i*sign(dy)

                cell = self.__board.get_cell(x, y)

                if not cell.is_empty():
                    return False

            return True
        
        return False


class GameMatch:
    __local_turn: bool
    __local_player: Player
    __remote_player: Player
    __board: Board

    def __init__(self, local_turn: bool, local_player: Player, remote_player: Player):
        self.__local_turn = local_turn
        self.__local_player = local_player
        self.__remote_player = remote_player
        self.__board = Board()

    @classmethod
    def from_start_status(cls, status: StartStatus) -> "GameMatch":
        local, remote = status.get_players()

        local_player = Player(local[0], local[1])
        remote_player = Player(remote[0], remote[1])
        local_turn = cls.evaluate_turn(local)

        return GameMatch(local_turn, local_player, remote_player)
    
    def get_board(self) -> Board:
        return self.__board
    
    def get_local_turn(self) -> bool:
        return self.__local_turn
    
    def get_local_player(self) -> Player:
        return self.__local_player

    def get_remote_player(self) -> Player:
        return self.__remote_player

    def place_ring(self, ring_type: RingType, destination_pos: tuple[int, int], player: Player):
        destination_cell = self.__board.get_cell(*destination_pos)

        present = destination_cell.has_ring(ring_type)

        if not present:        
            player.consume_ring(ring_type)

            destination_cell.insert_ring(ring_type)

            return Movement(
                type=MoveType.PLACE_RING,
                destination=destination_pos,
                ring_type=ring_type
            )
    
    def move_cell_content(self, origin_pos: tuple[int, int], destination_pos: tuple[int, int]):
        moved = self.__board.move(origin_pos, destination_pos)

        if moved:
            return Movement(
                type=MoveType.MOVE_CELL_CONTENT,
                origin=origin_pos,
                destination=destination_pos,
            )

    def receive_move(self, move: Movement):
        move_type = move.get_move_type()

        if move_type == MoveType.PLACE_RING:
            ring_type = move.get_ring_type()
            pos = move.get_destination_pos()

            self.place_ring(ring_type, pos, self.__remote_player)
        elif move_type == MoveType.MOVE_CELL_CONTENT:
            origin_pos = move.get_origin_pos()
            destination = move.get_destination_pos()

            self.move_cell_content(origin_pos, destination)
    
    def evaluate_round(self):        
        end = self.__board.check_end_condition()

        if not end:
            self.switch_turn()
        
        return end
    
    @classmethod
    def evaluate_turn(cls, local: list[str]) -> bool:
        return local[2] == "1"

    def switch_turn(self) -> bool:
        self.__local_turn = not self.__local_turn
        return self.__local_turn

