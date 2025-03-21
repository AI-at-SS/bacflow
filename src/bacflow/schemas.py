from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum

from dacite import Config, from_dict
from typing_extensions import Self

from bacflow.common import DoB_to_age


class DriverProfile(str, Enum):
    regular = "regular"
    novice = "novice"
    professional = "professional"

    def __str__(self) -> str:
        return self.value


DUIMapping = dict[str, dict[DriverProfile, float]]


class Model(str, Enum):
    average = "average"
    Forrest = "Forrest"
    Seidl = "Seidl"
    Ulrich = "Ulrich"
    Watson = "Watson"
    Widmark = "Widmark"

    def __str__(self) -> str:
        return self.value


class Sex(str, Enum):
    F = "F"
    M = "M"

    def __str__(self) -> str:
        return self.value


@dataclass
class Person:
    DoB: date
    height: float
    weight: float
    sex: Sex

    @property
    def age(self) -> int:
        return DoB_to_age(self.DoB)


class FoodCategory(str, Enum):
    light = "light"  # small amount of food, typically consumed to curb hunger between meals, such as a piece of fruit, a handful of nuts, or a small yogurt.
    moderate = "moderate"  # sufficient amount of food to satisfy hunger, usually a regular meal, such as a sandwich, a bowl of salad, or a standard portion of pasta.
    heavy = "heavy"  # large amount of food, often consumed for special occasions or when very hungry, such as a multi-course meal with several dishes, or a buffet.

    def __str__(self) -> str:
        return self.value


@dataclass
class Food:
    category: FoodCategory
    consumed: datetime


class BeverageCategory(str, Enum):
    beer = "beer"
    wine = "wine"
    longdrink = "long drink"
    cocktail = "cocktail"
    shot = "shot"
    eggnog = "eggnog"

    def __str__(self) -> str:
        return self.value


@dataclass
class Beverage:
    category: BeverageCategory
    consumed: datetime
    volume: float
    proportion: float
    interval: int
    quantity: float = field(init=False)

    def __post_init__(self):
        self.quantity = self.volume * self.proportion * 0.789

    def distribute(self) -> list[Self]:
        """ditributes the beverage into uniform sips in the time interval"""
        if self.interval == 1:
            return [self]

        sippings = []
        volume = self.volume / self.interval

        for i in range(self.interval):
            sippings.append(
                Beverage(
                    category=self.category,
                    consumed=self.consumed + timedelta(minutes=i),
                    volume=volume,
                    proportion=self.proportion,
                    interval=1,
                )
            )

        return sippings


@dataclass
class SimulationDataset:
    user: Person
    food: list[Food]
    beverage: list[Beverage]


@dataclass
class SimulationParameters:
    start: datetime
    end: datetime
    halflife: int
    modeling: list[Model]
    quantity: float
    stepping: float
    sobriety: bool
    DUI: float


@dataclass
class SimulationConfig:
    dataset: SimulationDataset
    parameters: SimulationParameters

    @classmethod
    def from_mapping(cls, mapping: dict) -> Self:
        return from_dict(cls, mapping, config=Config(cast=[Enum]))
