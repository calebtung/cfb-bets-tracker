from dataclasses import dataclass
from game import Game
from team import Team
from enum import Enum


class BetResults(Enum):
    PENDING = "pending"
    PUSH = "push"
    HIT = "hit"
    MISS = "miss"


class BetTypes(Enum):
    MONEYLINE = "moneyline"
    OVER = "over"
    UNDER = "under"
    SPREAD = "spread"
    TEAM_OVER = "team_over"
    TEAM_UNDER = "team_under"


@dataclass
class Bet:
    bettor: str
    game: Game
    odds: int
    result: str
    resulting_unit_profit: float

    def __post_init__(self):
        self.evaluate()

    def evaluate(self):
        raise NotImplementedError(
            "Base class Bet does not have evaluation implementation"
        )

    def update_profits(self):
        if self.result == BetResults.HIT.value:
            if self.odds > 0:
                self.resulting_unit_profit = self.odds / 100
            else:
                self.resulting_unit_profit = 100 / abs(self.odds)
        elif self.result == BetResults.MISS.value:
            self.resulting_unit_profit = -1.0
        else:
            self.resulting_unit_profit = 0.0


@dataclass
class MoneylineBet(Bet):
    taking_team: Team
    bet_type: str = BetTypes.MONEYLINE.value

    def evaluate(self):
        if not self.game.is_over:
            self.result: str = BetResults.PENDING.value
        else:
            taking_score = self.game.get_team(self.taking_team.full_name).score
            against_score = self.game.get_opposing_team(
                self.taking_team.full_name
            ).score
            if taking_score > against_score:
                self.result = BetResults.HIT.value
            else:
                self.result = BetResults.MISS.value
        super().update_profits()


@dataclass
class SpreadBet(Bet):
    taking_team: Team
    taking_spread: float
    bet_type: str = BetTypes.SPREAD.value

    def evaluate(self):
        if not self.game.is_over:
            self.result = BetResults.PENDING.value
        else:
            taking_score = self.game.get_team(self.taking_team.full_name).score
            against_score = self.game.get_opposing_team(
                self.taking_team.full_name
            ).score

            if (taking_score + self.taking_spread) > against_score:
                self.result = BetResults.HIT.value
            elif (taking_score + self.taking_spread) == against_score:
                self.result = BetResults.PUSH.value
            else:
                self.result = BetResults.MISS.value
        super().update_profits()


@dataclass
class OverBet(Bet):
    taking_points: float
    bet_type: str = BetTypes.OVER.value

    def evaluate(self):
        if not self.game.is_over:
            self.result = BetResults.PENDING.value
        else:
            combined_score = self.game.teams[0].score + self.game.teams[1].score

            if combined_score > self.taking_points:
                self.result = BetResults.HIT.value
            elif combined_score == self.taking_points:
                self.result = BetResults.PUSH.value
            else:
                self.result = BetResults.MISS.value
        super().update_profits()


@dataclass
class UnderBet(Bet):
    taking_points: float
    bet_type: str = BetTypes.UNDER.value

    def evaluate(self):
        if not self.game.is_over:
            self.result = BetResults.PENDING.value
        else:
            combined_score = self.game.teams[0].score + self.game.teams[1].score

            if combined_score < self.taking_points:
                self.result = BetResults.HIT.value
            elif combined_score == self.taking_points:
                self.result = BetResults.PUSH.value
            else:
                self.result = BetResults.MISS.value
        super().update_profits()


@dataclass
class TeamOverBet(Bet):
    taking_team: Team
    taking_points: float
    bet_type: str = BetTypes.TEAM_OVER.value

    def evaluate(self):
        if not self.game.is_over:
            self.result = BetResults.PENDING.value
        else:
            taking_score = self.game.get_team(self.taking_team.full_name).score

            if taking_score > self.taking_points:
                self.result = BetResults.HIT.value
            elif taking_score == self.taking_points:
                self.result = BetResults.PUSH.value
            else:
                self.result = BetResults.MISS.value
        super().update_profits()


@dataclass
class TeamUnderBet(Bet):
    taking_team: Team
    taking_points: float
    bet_type: str = BetTypes.TEAM_UNDER.value

    def evaluate(self):
        if not self.game.is_over:
            self.result = BetResults.PENDING.value
        else:
            taking_score = self.game.get_team(self.taking_team.full_name).score

            if taking_score < self.taking_points:
                self.result = BetResults.HIT.value
            elif taking_score == self.taking_points:
                self.result = BetResults.PUSH.value
            else:
                self.result = BetResults.MISS.value
        super().update_profits()
