from gamescore import Game, Score
from enum import Enum
import json
import re
import queryespn


class SimpleBetTypes(Enum):
    MONEYLINE = "moneyline"
    OVER = "over"
    UNDER = "under"
    OTHER = "other"
    SPREAD = "spread"
    TEAM_OVER = "team_over"
    TEAM_UNDER = "team_under"


class BetResults(Enum):
    PENDING = "pending"
    PUSH = "push"
    HIT = "hit"
    MISS = "miss"


def str2bet(bet_str: str, bettor: str, odds: int, wager: float, date: str = None):
    moneyline_regex = r"^(.*?)\s+ML$"
    moneyline_match = re.match(moneyline_regex, bet_str)
    over_regex = r"^(.*?)\s+vs\s+(.*?)\s+O\s+(\d+\.\d+)$"
    over_match = re.match(over_regex, bet_str)
    under_regex = r"^(.*?)\s+vs\s+(.*?)\s+U\s+(\d+\.\d+)$"
    under_match = re.match(under_regex, bet_str)
    spread_regex = r"^(.*?)\s+([+-]?\d*\.?\d+)$"
    spread_match = re.match(spread_regex, bet_str)
    team_over_regex = r"^(.*?)\s+TTP\s+O\s+(\d*\.?\d*)$"
    team_over_match = re.match(team_over_regex, bet_str)
    team_under_regex = r"^(.*?)\s+TTP\s+U\s+(\d*\.?\d*)$"
    team_under_match = re.match(team_under_regex, bet_str)

    # The order of the if elifs matter!
    # Because these regexes weren't super bullet proof,
    # spread_match technically can match team_over and team_under,
    # and team_over/team_under can technically match over/under
    if moneyline_match:
        team = moneyline_match.group(1)
    elif over_match:
        team = over_match.group(1)
        taking_points = float(over_match.group(3))
    elif under_match:
        team = under_match.group(1)
        taking_points = float(under_match.group(3))
    elif team_over_match:
        team = team_over_match.group(1)
        taking_points = float(team_over_match.group(2))
    elif team_under_match:
        team = team_under_match.group(1)
        taking_points = float(team_under_match.group(2))
    elif spread_match:
        team = spread_match.group(1)
        spread = float(spread_match.group(2))
    else:
        raise ValueError(f"Unrecognized bet_str {bet_str}")

    if date is None:
        game, score = queryespn.query_next_game_w_team(team)
    else:
        game, score = queryespn.query_game_w_team_and_date(team, date)

    if moneyline_match:
        bet = MoneylineBet(
            game=game,
            bettor=bettor,
            odds=odds,
            wager=wager,
            taking_team=team,
            score=score,
        )
    elif over_match:
        bet = OverBet(
            game=game,
            bettor=bettor,
            odds=odds,
            wager=wager,
            taking_points=taking_points,
            score=score,
        )
    elif under_match:
        bet = UnderBet(
            game=game,
            bettor=bettor,
            odds=odds,
            wager=wager,
            taking_points=taking_points,
            score=score,
        )
    elif team_over_match:
        bet = TeamOverBet(
            game=game,
            bettor=bettor,
            odds=odds,
            wager=wager,
            taking_points=taking_points,
            taking_team=team,
            score=score,
        )
    elif team_under_match:
        bet = TeamUnderBet(
            game=game,
            bettor=bettor,
            odds=odds,
            wager=wager,
            taking_points=taking_points,
            taking_team=team,
            score=score,
        )
    elif spread_match:
        bet = SpreadBet(
            game=game,
            bettor=bettor,
            odds=odds,
            wager=wager,
            taking_team=team,
            spread=spread,
            score=score,
        )

    return bet


class Bet:
    def __init__(
        self,
        game: Game,
        bettor: str,
        description: str,
        odds: int,
        wager: float,
        score: Score,
    ):
        self.game = game
        self.bettor = bettor
        self.description = description
        self.odds = odds
        self.wager = wager
        self.score = score
        self.odds_str = f"+{odds}" if odds > 0 else f"{odds}"
        self.bet_type: str = None
        self.bet_status: str = None
        self.unit_profit = self.compute_unit_profit()
        self.profit = self.unit_profit * self.wager

    def evaluate(self, score: Score):
        raise NotImplementedError("Make a specific bet.")

    def compute_unit_profit(self):
        if self.odds < 0:
            unit_profit = 100 / abs(self.odds)
        else:  # odds > 0
            unit_profit = self.odds / 100

        return unit_profit

    def update_wager(self, wager: float):
        self.wager = wager
        self.profit = self.unit_profit * self.wager

    def as_dict(self):
        return self.__dict__.copy()

    def as_json(self):
        self_dict = self.as_jsonable_dict(self)

        return json.dumps(self_dict, indent=4)

    def as_jsonable_dict(self):
        self_dict = self.as_dict()
        game: Game = self_dict["game"]
        game_dict = game.as_dict()
        self_dict["game"] = game_dict
        score: Score = self_dict["score"]
        score_dict = score.as_dict()
        self_dict["score"] = score_dict
        return self_dict

    def from_jsonable_dict(bet_dict: dict):
        game_dict = bet_dict["game"]
        game = Game(
            home_team="",
            home_team_logo_url="",
            away_team="",
            away_team_logo_url="",
            date="",
            is_neutral_site=False,
        )
        for key, value in game_dict.items():
            setattr(game, key, value)

        score_dict = bet_dict["score"]
        score = Score(home_team_score=0, away_team_score=1, is_final=False)
        for key, value in score_dict.items():
            setattr(score, key, value)

        if bet_dict["bet_type"] == SimpleBetTypes.MONEYLINE.value:
            bet = MoneylineBet(
                game=game,
                bettor="",
                odds=-110,
                wager=1.00,
                taking_team=game.home_team,
                score=score,
            )
        elif bet_dict["bet_type"] == SimpleBetTypes.OVER.value:
            bet = OverBet(
                game=game,
                bettor="",
                odds=-110,
                wager=1.00,
                taking_points=10,
                score=score,
            )
        elif bet_dict["bet_type"] == SimpleBetTypes.UNDER.value:
            bet = UnderBet(
                game=game,
                bettor="",
                odds=-110,
                wager=1.00,
                taking_points=10,
                score=score,
            )
        elif bet_dict["bet_type"] == SimpleBetTypes.TEAM_OVER.value:
            bet = TeamOverBet(
                game=game,
                bettor="",
                odds=-110,
                wager=1.00,
                taking_team=game.home_team,
                taking_points=10,
                score=score,
            )
        elif bet_dict["bet_type"] == SimpleBetTypes.TEAM_UNDER.value:
            bet = TeamUnderBet(
                game=game,
                bettor="",
                odds=-110,
                wager=1.00,
                taking_team=game.home_team,
                taking_points=10,
                score=score,
            )
        elif bet_dict["bet_type"] == SimpleBetTypes.SPREAD.value:
            bet = SpreadBet(
                game=game,
                bettor="",
                odds=-110,
                wager=1.00,
                taking_team=game.home_team,
                spread=-6.5,
                score=score,
            )
        else:  # Other
            raise ValueError("Unknown bet type")

        for key, value in bet_dict.items():
            if key == "game" or key == "score":
                continue
            setattr(bet, key, value)

        return bet

    def from_json(bet_json: str):
        bet_dict = json.loads(bet_json)
        bet = Bet.from_jsonable_dict(bet_dict)

        return bet


class MoneylineBet(Bet):
    def __init__(
        self,
        game: Game,
        bettor: str,
        odds: int,
        wager: float,
        score: Score,
        taking_team: str,
    ):
        if taking_team == game.home_team:
            description = f"{game.home_team} ML vs {game.away_team}"
        else:
            description = f"{game.away_team} ML @ {game.home_team}"

        super().__init__(game, description, bettor, odds, wager, score)
        self.taking_team = taking_team
        self.bet_type = SimpleBetTypes.MONEYLINE.value

        self.evaluate(score)

    def evaluate(self, score: Score):
        self.score = score
        if not score.is_final:
            self.bet_status = BetResults.PENDING.value
        else:
            if (
                self.game.home_team == self.taking_team
                and score.home_team_score > score.away_team_score
            ):
                self.bet_status = BetResults.HIT.value
            elif (
                self.game.away_team == self.taking_team
                and score.away_team_score > score.home_team_score
            ):
                self.bet_status = BetResults.HIT.value
            else:
                self.bet_status = BetResults.MISS.value


class OverBet(Bet):
    def __init__(
        self,
        game: Game,
        bettor: str,
        odds: int,
        wager: float,
        score: Score,
        taking_points: int,
    ):
        description = f"{game.home_team} vs {game.away_team} O {taking_points}"
        super().__init__(game, description, bettor, odds, wager, score)
        self.taking_points = taking_points
        self.bet_type = SimpleBetTypes.OVER.value

        self.evaluate(score)

    def evaluate(self, score: Score):
        self.score = score
        if not score.is_final:
            self.bet_status = BetResults.PENDING.value
        else:
            combined_score = score.away_team_score + score.home_team_score
            if combined_score > self.taking_points:
                self.bet_status = BetResults.HIT.value
            elif combined_score < self.taking_points:
                self.bet_status = BetResults.MISS.value
            else:  # score is equal
                self.bet_status = BetResults.PUSH.value


class TeamOverBet(Bet):
    def __init__(
        self,
        game: Game,
        bettor: str,
        odds: int,
        wager: float,
        taking_points: int,
        score: Score,
        taking_team: str,
    ):
        description = f"{taking_team} TTP O {taking_points}"
        super().__init__(game, description, bettor, odds, wager, score)
        self.taking_points = taking_points
        self.taking_team = taking_team
        self.bet_type = SimpleBetTypes.TEAM_OVER.value

        self.evaluate(score)

    def evaluate(self, score: Score):
        self.score = score
        if not score.is_final:
            self.bet_status = BetResults.PENDING.value
        else:
            if self.taking_team == self.game.away_team:
                team_score = score.away_team_score
            else:
                team_score = score.home_team_score
            if team_score > self.taking_points:
                self.bet_status = BetResults.HIT.value
            elif team_score < self.taking_points:
                self.bet_status = BetResults.MISS.value
            else:  # score is equal
                self.bet_status = BetResults.PUSH.value


class TeamUnderBet(Bet):
    def __init__(
        self,
        game: Game,
        bettor: str,
        odds: int,
        wager: float,
        taking_points: int,
        score: Score,
        taking_team: str,
    ):
        description = f"{taking_team} TTP U {taking_points}"
        super().__init__(game, description, bettor, odds, wager, score)
        self.taking_points = taking_points
        self.taking_team = taking_team
        self.bet_type = SimpleBetTypes.TEAM_UNDER.value

        self.evaluate(score)

    def evaluate(self, score: Score):
        self.score = score
        if not score.is_final:
            self.bet_status = BetResults.PENDING.value
        else:
            if self.taking_team == self.game.away_team:
                team_score = score.away_team_score
            else:
                team_score = score.home_team_score
            if team_score < self.taking_points:
                self.bet_status = BetResults.HIT.value
            elif team_score > self.taking_points:
                self.bet_status = BetResults.MISS.value
            else:  # score is equal
                self.bet_status = BetResults.PUSH.value


class UnderBet(Bet):
    def __init__(
        self,
        game: Game,
        bettor: str,
        odds: int,
        wager: float,
        score: Score,
        taking_points: int,
    ):
        description = f"{game.home_team} vs {game.away_team} U {taking_points}"
        super().__init__(game, description, bettor, odds, wager, score)
        self.taking_points = taking_points
        self.bet_type = SimpleBetTypes.UNDER.value

        self.evaluate(score)

    def evaluate(self, score: Score):
        self.score = score
        if not score.is_final:
            self.bet_status = BetResults.PENDING.value
        else:
            combined_score = score.away_team_score + score.home_team_score
            if combined_score < self.taking_points:
                self.bet_status = BetResults.HIT.value
            elif combined_score > self.taking_points:
                self.bet_status = BetResults.MISS.value
            else:  # score is equal
                self.bet_status = BetResults.PUSH.value


class SpreadBet(Bet):
    def __init__(
        self,
        game: Game,
        bettor: str,
        odds: int,
        wager: float,
        score: Score,
        taking_team: str,
        spread: float,
    ):
        if spread > 0:
            spread_str = f"+{spread}"
        else:
            spread_str = f"{spread}"
        if taking_team == game.home_team:
            description = f"{game.home_team} {spread_str} vs {game.away_team}"
        else:
            description = f"{game.away_team} {spread_str} @ {game.home_team}"
        super().__init__(game, description, bettor, odds, wager, score)
        self.taking_team = taking_team
        self.bet_type = SimpleBetTypes.SPREAD.value
        self.spread = spread
        self.spread_str = spread_str

        self.evaluate(score)

    def evaluate(self, score: Score):
        self.score = score
        if not score.is_final:
            self.bet_status = BetResults.PENDING.value
        else:
            if self.game.home_team == self.taking_team:
                taking_score = score.home_team_score
                against_score = score.away_team_score
            else:
                taking_score = score.away_team_score
                against_score = score.home_team_score

            if self.spread < 0:
                if (taking_score - against_score) > abs(self.spread):
                    self.bet_status = BetResults.HIT.value
                elif (taking_score - against_score) < abs(self.spread):
                    self.bet_status = BetResults.MISS.value
                else:
                    self.bet_status = BetResults.PUSH.value
            else:  # spread is positive
                if (against_score - taking_score) < self.spread:
                    self.bet_status = BetResults.HIT.value
                elif (against_score - taking_score) > self.spread:
                    self.bet_status = BetResults.MISS.value
                else:
                    self.bet_status = BetResults.PUSH.value
