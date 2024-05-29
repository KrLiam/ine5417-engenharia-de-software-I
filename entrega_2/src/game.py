from dataclasses import dataclass, field
from enum import Enum
from dog import StartStatus


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

    def insert_ring(self, pos: tuple[int, int], ring_type: RingType) -> bool:
        if not (0 <= pos[0] <= 3 and 0 <= pos[1] <= 3):
            return False
        
        cell = self.get_cell(*pos)

        if cell.has_ring(ring_type):
            return False

        cell.insert(ring_type)

        return True

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

    def insert(self, ring_type: RingType):
        self.rings.add(ring_type)
    
    def clear(self):
        self.rings.clear()
    
    def set_ring_set(self, ring_set: set[RingType]):
        self.rings.clear()
        self.rings.update(ring_set)

    def can_move_to(self, other_cell: "Cell") -> bool:
        if not other_cell.is_empty():
            return False

        pos = self.pos
        other_pos = other_cell.get_pos()

        if pos == other_pos:
            return False
        
        x1, y1 = pos
        x2, y2 = other_pos

        # horizontal
        if x1 == x2:
            for y in range(min(y1, y2) + 1, max(y1, y2)):
                cell = self.board.get_cell(x1, y)

                if not cell.is_empty():
                    return False

            return True
        
        # vertical
        if y1 == y2:
            for x in range(min(x1, x2) + 1, max(x1, x2)):
                cell = self.board.get_cell(x, y1)

                if not cell.is_empty():
                    return False
                
            return True
        
        # diagonal
        if abs(x1 - x2) == abs(y1 - y2):
            dx = 1 if x2 > x1 else -1
            dy = 1 if y2 > y1 else -1

            x, y = x1 + dx, y1 + dy

            while (x, y) != other_pos:
                cell = self.board.get_cell(x, y)

                if not cell.is_empty():
                    return False
                
                x += dx
                y += dy

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
    
    def get_board(self) -> Board:
        return self.board
    
    def get_local_turn(self) -> bool:
        return self.local_turn
    
    def get_local_player(self) -> Player:
        return self.local_player

    def get_remote_player(self) -> Player:
        return self.remote_player

    @classmethod
    def from_start_status(cls, status: StartStatus) -> "GameMatch":
        local, remote = status.get_players()

        local_turn = local[2] == "1"
        local_player = Player(local[0], local[1])
        remote_player = Player(remote[0], remote[1])

        return GameMatch(local_turn, local_player, remote_player)

    def switch_turn(self) -> bool:
        self.local_turn = not self.local_turn
        return self.local_turn
    
    @classmethod
    def evaluate_turn(cls, players: list[str], local_id: str):
        ...
