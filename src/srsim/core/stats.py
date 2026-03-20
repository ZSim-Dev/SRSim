from dataclasses import dataclass


@dataclass
class Stats:
    max_hp: int
    atk: int
    defense: int
    spd: int
    max_energy: int = 100
    crit_rate: float = 0.05
    crit_dmg: float = 0.50
    dmg_boost: float = 0.0
    break_effect: float = 0.0
    energy_regen_rate: float = 0.0
    effect_res: float = 0.0
    resistance: float = 0.0

    def copy(self) -> "Stats":
        return Stats(
            max_hp=self.max_hp,
            atk=self.atk,
            defense=self.defense,
            spd=self.spd,
            max_energy=self.max_energy,
            crit_rate=self.crit_rate,
            crit_dmg=self.crit_dmg,
            dmg_boost=self.dmg_boost,
            break_effect=self.break_effect,
            energy_regen_rate=self.energy_regen_rate,
            effect_res=self.effect_res,
            resistance=self.resistance,
        )
