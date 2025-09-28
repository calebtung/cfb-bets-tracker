import re
from bet import (
    MoneylineBet,
    OverBet,
    UnderBet,
    TeamOverBet,
    TeamUnderBet,
    SpreadBet,
    BetResults,
)
from espnquery import search_for_cfb_game_using_team_name


def str_to_cfb_bet(
    bet_str: str,
    bettor: str,
    odds: int,
    games_data: dict,
):
    moneyline_regex = r"^(.*?)\s+ML$"
    moneyline_match = re.match(moneyline_regex, bet_str)
    over_regex = r"^(.+?)/(.+?)\s+O\s+(\d+\.\d)$"
    over_match = re.match(over_regex, bet_str)
    under_regex = r"^(.+?)/(.+?)\s+U\s+(\d+\.\d)$"
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
    opposing_team_name = None
    if moneyline_match:
        team_name = moneyline_match.group(1)
    elif over_match:
        team_name = over_match.group(1)
        opposing_team_name = over_match.group(2)
        taking_points = float(over_match.group(3))
    elif under_match:
        team_name = under_match.group(1)
        opposing_team_name = under_match.group(2)
        taking_points = float(under_match.group(3))
    elif team_over_match:
        team_name = team_over_match.group(1)
        taking_points = float(team_over_match.group(2))
    elif team_under_match:
        team_name = team_under_match.group(1)
        taking_points = float(team_under_match.group(2))
    elif spread_match:
        team_name = spread_match.group(1)
        taking_spread = float(spread_match.group(2))
    else:
        raise ValueError(f"Unrecognized bet_str {bet_str}")

    game = search_for_cfb_game_using_team_name(
        search_team_name=team_name,
        games_data=games_data,
        search_opposing_team_name=opposing_team_name,
    )

    if game is None:
        raise ValueError(f"Unable to find a matching game for the bet_str {bet_str}")

    if moneyline_match:
        bet = MoneylineBet(
            bettor=bettor,
            game=game,
            odds=odds,
            result=BetResults.PENDING.value,
            resulting_unit_profit=None,
            taking_team=game.get_team(team_name),
        )
    elif over_match:
        bet = OverBet(
            bettor=bettor,
            game=game,
            odds=odds,
            result=BetResults.PENDING.value,
            resulting_unit_profit=None,
            taking_points=taking_points,
        )
    elif under_match:
        bet = UnderBet(
            bettor=bettor,
            game=game,
            odds=odds,
            result=BetResults.PENDING.value,
            resulting_unit_profit=None,
            taking_points=taking_points,
        )
    elif team_over_match:
        bet = TeamOverBet(
            bettor=bettor,
            game=game,
            odds=odds,
            result=BetResults.PENDING.value,
            resulting_unit_profit=None,
            taking_team=game.get_team(team_name),
            taking_points=taking_points,
        )
    elif team_under_match:
        bet = TeamUnderBet(
            bettor=bettor,
            game=game,
            odds=odds,
            result=BetResults.PENDING.value,
            resulting_unit_profit=None,
            taking_team=game.get_team(team_name),
            taking_points=taking_points,
        )
    elif spread_match:
        bet = SpreadBet(
            bettor=bettor,
            game=game,
            odds=odds,
            result=BetResults.PENDING.value,
            resulting_unit_profit=None,
            taking_team=game.get_team(team_name),
            taking_spread=taking_spread,
        )
    else:
        raise ValueError(f"Unrecognized bet_str {bet_str}")

    bet.evaluate()
    return bet
