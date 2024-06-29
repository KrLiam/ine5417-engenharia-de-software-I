from dataclasses import dataclass, field
from enum import Enum
from dog import StartStatus
from typing import Any


class MoveType(Enum):
    PLACE_RING = 0
    MOVE_CELL_CONTENT = 1

class Movement:
    match_status: str | None
    type: MoveType
    ring_type: "RingType" | None
    origin: tuple[int, int] | None
    destination: tuple[int, int]

    def __init__(
        self,
        type: MoveType,
        destination: tuple[int, int],
        origin: tuple[int, int] | None = None,
        ring_type: "RingType" | None = None,
        match_status: str | None = None
    ):
        self.type = type
        self.ring_type = ring_type
        self.origin = origin
        self.destination = destination
        self.match_status = match_status

    def get_move_type(self) -> MoveType:
        return self.move_type

    def get_ring_type(self) -> "RingType":
        return self.ring_type

    def get_origin_pos(self) -> tuple[int, int]:
        return self.origin

    def get_destination_pos(self) -> tuple[int, int]:
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
    name: str
    id: str
    red_amount: int = field(init=False, default=16)
    green_amount: int = field(init=False, default=16)
    blue_amount: int = field(init=False, default=16)

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> str:
        return self.id

    def get_ring_amount(self, ring_type: RingType) -> int:
        if ring_type == RingType.RED:
            return self.red_amount
        if ring_type == RingType.GREEN:
            return self.green_amount
        return self.blue_amount


    def consume_ring(self, ring_type: RingType):
        if ring_type == RingType.RED:
            self.red_amount = max(self.red_amount - 1, 0)
        elif ring_type == RingType.GREEN:
            self.green_amount = max(self.green_amount - 1, 0)
        else:
            self.blue_amount = max(self.blue_amount - 1, 0)


class Board:
    cells: list["Cell"]

    def __init__(self):
        self.cells = []

        for i in range(4):
            for j in range(4):
                self.cells.append(Cell(self, (i, j)))
    
    def get_cells(self) -> tuple["Cell", ...]:
        return tuple(self.cells)
    
    def get_cell(self, i: int, j: int) -> "Cell":
        return self.cells[i*4 + j]

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
    board: Board = field(repr=False)
    pos: tuple[int, int]
    rings: set[RingType]

    def __init__(self, board: Board, pos: tuple[int, int]):
        self.board = board
        self.pos = pos
        self.rings = set()
    
    def __eq__(self, other: "Cell") -> bool:
        return self.rings == other.rings
    
    def get_pos(self) -> tuple[int, int]:
        return self.pos

    def get_ring_set(self) -> set[RingType]:
        return set(self.rings)
    
    def has_ring(self, ring_type: RingType) -> bool:
        return ring_type in self.rings

    def is_empty(self) -> bool:
        return not self.rings

    def insert_ring(self, ring_type: RingType):
        self.rings.add(ring_type)
    
    def clear(self):
        self.rings.clear()
    
    def set_ring_set(self, ring_set: set[RingType]):
        self.rings.clear()
        self.rings.update(ring_set)

    def can_move_to(self, other_cell: "Cell") -> bool:
        pos = self.pos
        other_pos = other_cell.get_pos()
                
        dx = other_pos[0] - pos[0]
        dy = other_pos[1] - pos[1]

        valid_direction = dx == 0 or dy == 0 or abs(dx) == abs(dy)

        if pos != other_pos and valid_direction:
            distance = max(abs(dx), abs(dy))

            for i in range(1, distance + 1):
                x = pos[0] + i*sign(dx)
                y = pos[1] + i*sign(dy)

                cell = self.board.get_cell(x, y)

                if not cell.is_empty():
                    return False

            return True
        
        return False


class GameMatch:
    local_turn: bool
    local_player: Player
    remote_player: Player
    board: Board

    def __init__(self, local_turn: bool, local_player: Player, remote_player: Player):
        self.local_turn = local_turn
        self.local_player = local_player
        self.remote_player = remote_player
        self.board = Board()

    @classmethod
    def from_start_status(cls, status: StartStatus) -> "GameMatch":
        local, remote = status.get_players()

        local_player = Player(local[0], local[1])
        remote_player = Player(remote[0], remote[1])
        local_turn = cls.evaluate_turn(local)

        return GameMatch(local_turn, local_player, remote_player)
    
    def get_board(self) -> Board:
        return self.board
    
    def get_local_turn(self) -> bool:
        return self.local_turn
    
    def get_local_player(self) -> Player:
        return self.local_player

    def get_remote_player(self) -> Player:
        return self.remote_player

    def place_ring(self, ring_type: RingType, destination_pos: tuple[int, int], player: Player):
        destination_cell = self.board.get_cell(*destination_pos)

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
        moved = self.board.move(origin_pos, destination_pos)

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
            pos = move.get_destination()

            self.place_ring(ring_type, pos, self.remote_player)
        elif move_type == MoveType.MOVE_CELL_CONTENT:
            origin_pos = move.get_origin_pos()
            destination = move.get_destination_pos()

            self.move_cell_content(origin_pos, destination)
    
    def evaluate_round(self):        
        end = self.board.check_end_condition()

        if not end:
            self.match.switch_turn()
        
        return end
    
    @classmethod
    def evaluate_turn(cls, local: list[str]) -> bool:
        return local[2] == "1"

    def switch_turn(self) -> bool:
        self.local_turn = not self.local_turn
        return self.local_turn

