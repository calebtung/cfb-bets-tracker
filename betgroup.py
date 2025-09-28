from dataclasses import dataclass, field, asdict
from typing_extensions import Self
from bet import Bet, BetResults
import json
import pickle


@dataclass
class BetGroup:
    group_name: str
    sub_betgroups: dict[str, Self] = field(default_factory=dict)
    bets: list[Bet] = field(default_factory=list)
    hits: int = 0
    misses: int = 0
    pushes: int = 0
    pendings: int = 0
    profit: float = 0.0

    def new_sub_betgroup(self, betgroup: Self):
        if len(self.bets) > 0:
            raise ValueError(
                f"This betgroup with name {self.group_name} already has bets. You cannot use it to store betgroups."
            )
        self.sub_betgroups[betgroup.group_name] = betgroup

    def new_bet(self, bet: Bet):
        if len(self.sub_betgroups) > 0:
            raise ValueError(
                f"This betgroup with name {self.group_name} already has sub betgroups. You cannot use it to store bets."
            )
        if self.bets is None:
            self.bets = []
        self.bets.append(bet)

    def evaluate(self):
        self.hits = 0
        self.misses = 0
        self.pushes = 0
        self.pendings = 0
        self.profit = 0
        if len(self.bets) > 0:
            for bet in self.bets:
                bet.evaluate()
                if bet.result == BetResults.HIT.value:
                    self.hits += 1
                elif bet.result == BetResults.MISS.value:
                    self.misses += 1
                elif bet.result == BetResults.PUSH.value:
                    self.pushes += 1
                else:
                    self.pendings += 1
                self.profit += bet.resulting_unit_profit
        else:
            for betgroup_name, betgroup in self.sub_betgroups.items():
                betgroup.evaluate()
                self.hits += betgroup.hits
                self.misses += betgroup.misses
                self.pushes += betgroup.pushes
                self.pendings += betgroup.pendings
                self.profit += betgroup.profit

    def to_json(self, indent: int = 4):
        betgroup_dict = asdict(self)
        betgroup_json = json.dumps(betgroup_dict, indent=indent)
        return betgroup_json

    def save_to_disk(self, filepath: str):
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    def get_start_and_end_dates_of_all_bets(self) -> tuple[str, str]:
        all_dates = []
        if len(self.bets) > 0:
            for bet in self.bets:
                all_dates.append(bet.game.date)
        else:
            for sub_betgroup in self.sub_betgroups.values():
                sub_start, sub_end = sub_betgroup.get_start_and_end_dates_of_all_bets()
                all_dates.append(sub_start)
                all_dates.append(sub_end)
        if len(all_dates) == 0:
            return None, None
        return min(all_dates), max(all_dates)

    @staticmethod
    def load_from_disk(filepath: str) -> Self:
        with open(filepath, "rb") as f:
            return pickle.load(f)
