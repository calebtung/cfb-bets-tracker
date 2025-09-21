from bet import Bet, BetResults
import json
from typing_extensions import Self


class BetGroup:
    def __init__(self, bettor: str, description: str, bets: list[Bet]):
        self.bets = bets
        self.bettor = bettor
        self.description = description
        self.hits = 0
        self.misses = 0
        self.pushes = 0
        self.pending = 0
        self.unit_profit = 0.0
        self.compute_record()

    def merge_betgroups(
        new_bettor: str, new_description: str, betgroups: list[Self]
    ) -> Self:
        all_bets = []
        for betgroup in betgroups:
            all_bets += betgroup.bets

        new_betgroup = BetGroup(new_bettor, new_description, all_bets)
        return new_betgroup

    def compute_record(self):
        self.hits = 0
        self.misses = 0
        self.pushes = 0
        self.pending = 0
        self.unit_profit = 0.0
        for bet in self.bets:
            if bet.score.is_final:
                if bet.bet_status == BetResults.HIT.value:
                    self.hits += 1
                    self.unit_profit += bet.unit_profit
                elif bet.bet_status == BetResults.MISS.value:
                    self.misses += 1
                    self.unit_profit -= 1
                elif bet.bet_status == BetResults.PUSH.value:
                    self.pushes += 1
            else:
                self.pending += 1

    def as_dict(self):
        return self.__dict__.copy()

    def as_json(self):
        self_dict = self.as_dict()
        bets_json_list = [bet.as_jsonable_dict() for bet in self.bets]
        self_dict["bets"] = bets_json_list
        self_json = json.dumps(self_dict, indent=4)
        return self_json

    def from_json(betgroup_json: str) -> Self:
        betgroup = BetGroup(bettor="", description="", bets=[])
        betgroup_dict = json.loads(betgroup_json)
        bets = [Bet.from_jsonable_dict(bet_json) for bet_json in betgroup_dict["bets"]]
        betgroup_dict["bets"] = bets

        for key, value in betgroup_dict.items():
            setattr(betgroup, key, value)

        return betgroup
