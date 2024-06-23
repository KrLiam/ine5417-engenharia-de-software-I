
from enum import Enum
from typing import Any

from game import RingType


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
