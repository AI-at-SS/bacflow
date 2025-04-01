from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Protocol

import yaml
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
    

class Consumable(Protocol):
    consumed: datetime


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
    longdrink = "longdrink"
    cocktail = "cocktail"
    shot = "shot"
    eggnog = "eggnog"

    def __str__(self) -> str:
        return self.value


@dataclass
class Beverage:
    category: BeverageCategory
    consumed: datetime
    dilution: int
    quantity: float = field(init=False)
    proportion: float
    volume: float

    def __post_init__(self):
        self.quantity = self.volume * self.proportion * 0.789

    def distribute(self) -> list[Self]:
        """ditributes the beverage into uniform sips in the time interval"""
        if self.dilution == 1:
            return [self]

        sippings = []
        volume = self.volume / self.dilution

        for i in range(self.dilution):
            sippings.append(
                Beverage(
                    category=self.category,
                    consumed=self.consumed + timedelta(minutes=i),
                    dilution=1,
                    proportion=self.proportion,
                    volume=volume,
                )
            )

        return sippings
    

@dataclass(frozen=True)
class Threshold:
    description: str
    value: float


@dataclass
class SimulationDataset:
    drinking: list[Beverage]
    eating: list[Food]
    person: Person


@dataclass
class SimulationParameters:
    start: datetime
    end: datetime
    halflife: int
    modeling: list[Model]
    quantity: float
    stepping: float
    thresholding: list[Threshold]


def _consumed_in_the_simulation(consumable: Consumable, parameters: SimulationParameters) -> bool:
    """ensures a consumable is consumed within the simulation time range."""
    return parameters.start < consumable.consumed < parameters.end


@dataclass
class SimulationConfig:
    """The blood alcohol concentration simulation config"""
    dataset: SimulationDataset
    parameters: SimulationParameters

    @classmethod
    def from_file(cls, absfile: str) -> Self:
        with open(absfile, "r") as f:
            mapping = yaml.safe_load(f)

        return cls.from_mapping(mapping)

    @classmethod
    def from_mapping(cls, mapping: dict) -> Self:
        return from_dict(cls, mapping, config=Config(cast=[Enum]))


@dataclass
class SimulationOutput:
    """The blood alcohol concentration simulation output"""
    timestamp: list[float]
    mean: list[float]
    stddev: list[float]

    @classmethod
    def from_file(cls, absfile: str) -> Self:
        with open(absfile, "r") as f:
            mapping = yaml.safe_load(f)

        return cls.from_mapping(mapping)

    @classmethod
    def from_mapping(cls, mapping: dict) -> Self:
        return from_dict(cls, mapping, config=Config(cast=[Enum]))
