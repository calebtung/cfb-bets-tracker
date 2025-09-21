import requests
from gamescore import Game, Score
from datetime import datetime, timedelta


ESPN_API_BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates="  # follow with YYYYMMDD format


def get_next_weekday(current_date: datetime, target_weekday: int):
    days_ahead = (target_weekday - current_date.weekday() + 7) % 7
    if days_ahead == 0:  # If today is the target weekday, then you're all good
        return current_date
    return current_date + timedelta(days=days_ahead)


def get_next_thursday():
    return get_next_weekday(datetime.now(), 3)  # Thursday is 3


def get_next_friday():
    return get_next_weekday(datetime.now(), 4)  # Friday is 4


def get_next_saturday():
    return get_next_weekday(datetime.now(), 5)  # Saturday is 5


def check_score(game: Game):
    _, score = query_game_w_team_and_date(game.home_team, game.date)
    return score


def query_next_game_w_team(team_name: str):
    friday = get_next_friday().strftime("%Y%m%d")
    game, score = query_game_w_team_and_date(team_name, friday)
    if game is None or score is None:
        saturday = get_next_saturday().strftime("%Y%m%d")
        game, score = query_game_w_team_and_date(team_name, saturday)

    return game, score


def query_game_w_team_and_date(team_name: str, date: str):
    url = f"{ESPN_API_BASE_URL}{date}"
    response = requests.get(url)
    games_data = response.json()
    for event in games_data["events"]:
        if team_name in event["name"]:
            competition = event["competitions"][0]
            is_neutral_site = bool(competition["neutralSite"])
            competitors = competition["competitors"]

            for competitor in competitors:
                team_name = competitor["team"]["displayName"]
                team_logo_url = competitor["team"]["logo"]
                score = int(competitor["score"])
                if "winner" in competitor:
                    is_over = True
                else:
                    is_over = False

                if competitor["homeAway"] == "home":
                    home_team = team_name
                    home_team_logo_url = team_logo_url
                    home_team_score = score
                else:
                    away_team = team_name
                    away_team_logo_url = team_logo_url
                    away_team_score = score
            game = Game(
                home_team=home_team,
                home_team_logo_url=home_team_logo_url,
                away_team=away_team,
                away_team_logo_url=away_team_logo_url,
                date=date,
                is_neutral_site=is_neutral_site,
            )
            score = Score(
                home_team_score=home_team_score,
                away_team_score=away_team_score,
                is_final=is_over,
            )

            return game, score
    return None, None
