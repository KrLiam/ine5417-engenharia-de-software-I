
from enum import Enum


class Gender(Enum):
    Male = 0
    Female = 1

NAMES: list[tuple[Gender, str]] = [
    (Gender.Male, "Urso"),
    (Gender.Male, "Cachorro"),
    (Gender.Male, "Elefante"),
    (Gender.Male, "Tigre"),
    (Gender.Male, "Gato"),
    (Gender.Male, "Leão"),
    (Gender.Female, "Onça"),
    (Gender.Male, "Mamute"),
    (Gender.Male, "Lobo"),
    (Gender.Male, "Rato"),
    (Gender.Female, "Girafa"),
    (Gender.Female, "Arara"),
    (Gender.Female, "Cobra"),
    (Gender.Female, "Vaca"),
    (Gender.Female, "Galinha"),
    (Gender.Female, "Gaivota"),
    (Gender.Male, "Cavalo"),
    (Gender.Male, "Dinossauro"),
]
ADJECTIVES = [
    ("Generoso", "Generosa"),
    ("Inteligente", "Inteligente"),
    ("Veloz", "Veloz"),
    ("Ligeiro", "Ligeira"),
    ("Bebê", "Bebê"),
]