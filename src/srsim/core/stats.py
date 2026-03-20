from dataclasses import dataclass
from typing import Self


@dataclass
class Stats:
    max_hp: int
    atk: int
    defense: int
    spd: int
    max_energy: int = 100

    def copy(self) -> Self:
        return self.__class__(
            max_hp=self.max_hp,
            atk=self.atk,
            defense=self.defense,
            spd=self.spd,
            max_energy=self.max_energy,
        )
