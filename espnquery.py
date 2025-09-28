import requests
from game import Game
from team import TeamInGame
from datetime import datetime, timedelta
from betgroup import BetGroup
from bet import BetResults

ESPN_API_BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates="


def query_cfb_games_data_for_dates(start_date: str, end_date: str = None) -> dict:
    url = f"{ESPN_API_BASE_URL}{start_date}"
    if end_date is not None:
        url = f"{url}-{end_date}"
    response = requests.get(url)
    games_data = response.json()

    return games_data


def query_cfb_games_data_for_weekend(friday_date: str):
    friday_datetime = datetime.strptime(friday_date, "%Y%m%d")
    saturday_datetime = friday_datetime + timedelta(days=1)
    saturday_date = saturday_datetime.strftime("%Y%m%d")
    games_data = query_cfb_games_data_for_dates(start_date=friday_date, end_date=saturday_date)
    return games_data


def search_for_cfb_game_using_team_name(
    search_team_name: str, games_data: dict, search_opposing_team_name: str = None
):
    for event in games_data["events"]:
        competition = event["competitions"][0]
        is_neutral_site = bool(competition["neutralSite"])
        competitors = competition["competitors"]
        game_date = datetime.fromisoformat(
            competition["date"].replace("Z", "+00:00")
        ).strftime("%Y%m%d")

        teams = []
        is_game_found = False
        is_over = False
        search_team_found_in_game = False
        search_opposing_team_found_in_game = False

        for competitor in competitors:
            team_full_name = competitor["team"]["displayName"]
            team_short_name = competitor["team"]["shortDisplayName"]
            team_abbreviation = competitor["team"]["abbreviation"]
            team_logo_url = competitor["team"]["logo"]
            team_score = int(competitor["score"])
            team_is_home_team = True if competitor["homeAway"] == "home" else False

            team = TeamInGame(
                full_name=team_full_name,
                short_name=team_short_name,
                abbreviation=team_abbreviation,
                logo_url=team_logo_url,
                score=team_score,
                is_home_team=team_is_home_team,
            )
            teams.append(team)

            if "winner" in competitor:
                is_over = True

            # Found the game with the search team
            if (
                search_team_name == team_full_name
                or search_team_name == team_short_name
                or team_abbreviation == search_team_name
            ):
                search_team_found_in_game = True

            if (
                search_opposing_team_name == team_full_name
                or search_opposing_team_name == team_short_name
                or team_abbreviation == search_opposing_team_name
            ):
                search_opposing_team_found_in_game = True

        if search_team_found_in_game:
            if search_opposing_team_name is not None:
                if search_opposing_team_found_in_game:
                    is_game_found = True
            else:
                is_game_found = True

        if is_game_found:
            game = Game(
                teams=teams,
                date=game_date,
                is_over=is_over,
                is_neutral_site=is_neutral_site,
            )
            return game
    raise ValueError(f"Could not find a game for team: {search_team_name}/{search_opposing_team_name}")


def update_cfb_game_score(game: Game, games_data: dict):
    search_team_name = game.teams[0].full_name
    search_opposing_team_name = game.teams[1].full_name
    game_date = game.date

    updated_game = search_for_cfb_game_using_team_name(
        search_team_name=search_team_name,
        games_data=games_data,
        search_opposing_team_name=search_opposing_team_name,
    )
    if updated_game is None:
        raise ValueError(f"Could not find a game with the teams {search_team_name} and {search_opposing_team_name} in games_data")
    elif updated_game.date != game_date:
        raise ValueError(
            f"Found a game in games_data with the teams {search_team_name} and {search_opposing_team_name}, but the found date was {updated_game.date}, not the {game_date} provided."
        )
    else:
        game.is_over = updated_game.is_over
        for updated_team in updated_game.teams:
            for team in game.teams:
                if team.full_name == updated_team.full_name:
                    team.score = updated_team.score

def update_cfb_games_for_betgroup(betgroup: BetGroup, games_data: dict, only_pending: bool = True):
    if len(betgroup.bets) > 0:
        for bet in betgroup.bets:
            if only_pending and bet.result != BetResults.PENDING.value:
                continue
            update_cfb_game_score(bet.game, games_data)
    else:
        for sub_betgroup in betgroup.sub_betgroups.values():
            update_cfb_games_for_betgroup(sub_betgroup, games_data, only_pending=only_pending)