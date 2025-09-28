import json
from convenience import str_to_cfb_bet
from espnquery import query_cfb_games_data_for_weekend
from dataclasses import asdict
from betgroup import BetGroup
import pickle
import os


def read_cfb_week_bets_input(week_bets_filepath: str):
    with open(week_bets_filepath) as week_bets_file:
        week_bets_input = json.load(week_bets_file)
        cfb_friday = week_bets_input["cfb_friday"]
        games_data = query_cfb_games_data_for_weekend(cfb_friday)

        week_bets = BetGroup(group_name=os.path.basename(os.path.dirname(week_bets_filepath)))

        for show_name, show_bets in week_bets_input["shows"].items():
            week_bets.new_sub_betgroup(
                get_bets_in_category(
                    bet_category_name=show_name,
                    bet_category_contents=show_bets,
                    games_data=games_data,
                )
            )
        week_bets.evaluate()
        return week_bets


def get_bets_in_category(
    bet_category_name: str,
    bet_category_contents: dict[str, dict] | list[tuple[str, int]],
    games_data: dict,
):
    return_betgroup = BetGroup(group_name=bet_category_name)
    if isinstance(bet_category_contents, dict):
        for key, value in bet_category_contents.items():
            return_betgroup.new_sub_betgroup(
                get_bets_in_category(
                    bet_category_name=key,
                    bet_category_contents=value,
                    games_data=games_data,
                )
            )
    elif isinstance(
        bet_category_contents, list
    ):  # leaf node, it's individual bets here
        bettor = bet_category_name

        for bet_str, odds in bet_category_contents:
            bet = str_to_cfb_bet(
                bet_str=bet_str, bettor=bettor, odds=odds, games_data=games_data
            )
            return_betgroup.new_bet(bet)
    else:
        raise ValueError("bet_category_contents must be dict or list")

    return return_betgroup


if __name__ == "__main__":
    import time
    

    week_bets =  read_cfb_week_bets_input("/home/caleb/cfb-bets-tracker/bets/Week 5/input.json")
    week_bets.save_to_disk("/home/caleb/cfb-bets-tracker/bets/Week 5/output.bets")
    with open("/home/caleb/cfb-bets-tracker/bets/Week 5/output.json", "w") as f:
        f.write(week_bets.to_json())
    week_bets = read_cfb_week_bets_input("/home/caleb/cfb-bets-tracker/bets/Week 4/input.json")
    week_bets.save_to_disk("/home/caleb/cfb-bets-tracker/bets/Week 4/output.bets")
    with open("/home/caleb/cfb-bets-tracker/bets/Week 4/output.json", "w") as f:
        f.write(week_bets.to_json())