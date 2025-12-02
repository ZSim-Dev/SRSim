from dataclasses import dataclass


@dataclass
class Stats:
    max_hp: int
    atk: int
    defense: int
    spd: int
    max_energy: int = 100

    def copy(self) -> Stats:
        return Stats(
            max_hp=self.max_hp,
            atk=self.atk,
            defense=self.defense,
            spd=self.spd,
            max_energy=self.max_energy,
        )
