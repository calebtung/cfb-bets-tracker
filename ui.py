import dash
from dash import html, Input, Output
import dash_bootstrap_components as dbc
import os
import pickle
from betgroup import BetGroup
from team import TeamInGame
from bet import (
    BetTypes,
    Bet,
    MoneylineBet,
    SpreadBet,
    OverBet,
    UnderBet,
    TeamOverBet,
    TeamUnderBet,
)
from espnquery import query_cfb_games_data_for_dates, update_cfb_games_for_betgroup


def load_all_cfb_betgroups_from_disk(bets_folder):
    betgroups = {}
    for root, dirs, files in os.walk(bets_folder):
        for file in files:
            if file.endswith(".bets"):
                filepath = os.path.join(root, file)
                betgroup = BetGroup.load_from_disk(filepath)
                betgroups[filepath] = betgroup
    return betgroups


def refresh_pending_cfb_betgroups(betgroups: dict[str, BetGroup]):
    for betgroup_filepath, betgroup in betgroups.items():
        start_date, end_date = betgroup.get_start_and_end_dates_of_all_bets()
        if start_date == end_date:
            end_date = None
        games_data = query_cfb_games_data_for_dates(start_date, end_date)
        update_cfb_games_for_betgroup(betgroup, games_data, only_pending=True)
        betgroup.evaluate()
        betgroup.save_to_disk(betgroup_filepath)
        with open(os.path.join(os.path.dirname(betgroup_filepath), "output.json"), "w") as f:
            f.write(betgroup.to_json())


def bet_to_card(bet: Bet):
    game = bet.game
    teams = game.teams

    left_logo_img = html.Img(src=teams[0].logo_url, width="80px", height="80px")
    left_team_span = html.Span(f"{teams[0].full_name}", className="small")
    left_score_span = html.Big(f"{teams[0].score}", className="left-score")
    dash_big = html.Big(" - ")
    right_logo_img = html.Img(src=teams[1].logo_url, width="80px", height="80px")
    right_team_span = html.Span(f"{teams[1].full_name}", className="small")
    right_score_span = html.Big(f"{teams[1].score}", className="right-score")

    bettor_small = html.Small(f"Picked by {bet.bettor}")
    if isinstance(bet, MoneylineBet):
        ml_bet: MoneylineBet = bet
        bet_description_h4 = html.H4(
            f"{ml_bet.taking_team.full_name} MONEYLINE ({bet.odds:+d})"
        )
    elif isinstance(bet, SpreadBet):
        spread_bet: SpreadBet = bet
        bet_description_h4 = html.H4(
            f"{spread_bet.taking_team.full_name} {spread_bet.taking_spread:+} SPREAD ({bet.odds:+d})"
        )
    elif isinstance(bet, OverBet):
        over_bet: OverBet = bet
        bet_description_h4 = html.H4(
            f"GAME TOTAL OVER {over_bet.taking_points} ({bet.odds:+d})"
        )
    elif isinstance(bet, UnderBet):
        under_bet: UnderBet = bet
        bet_description_h4 = html.H4(
            f"GAME TOTAL UNDER {under_bet.taking_points} ({bet.odds:+d})"
        )
    elif isinstance(bet, TeamOverBet):
        team_over_bet: TeamOverBet = bet
        bet_description_h4 = html.H4(
            f"{team_over_bet.taking_team.full_name} TEAM TOTAL OVER {team_over_bet.taking_points} ({bet.odds:+d})"
        )
    elif isinstance(bet, TeamUnderBet):
        team_under_bet: TeamUnderBet = bet
        bet_description_h4 = html.H4(
            f"{team_under_bet.taking_team.full_name} TEAM TOTAL UNDER {team_under_bet.taking_points} ({bet.odds:+d})"
        )

    team_deets_div = html.Div(
        [
            left_logo_img,
            left_team_span,
            left_score_span,
            dash_big,
            right_score_span,
            right_team_span,
            right_logo_img,
        ],
        className="d-flex justify-content-center align-items-center gap-4 mb-3",
    )
    status_div = html.Div(f"{bet.result.upper()}", className="status")
    if bet.resulting_unit_profit >= 0:
        profit_str = f"Profit: {bet.resulting_unit_profit:+.2f} units"
    else:
        profit_str = f"Loss: {bet.resulting_unit_profit:+.2f} units"
    profit_div = html.Div(
        profit_str, className="profit"
    )

    result_color = {
        "hit": "success",
        "miss": "danger",
        "push": "warning",
        "pending": "secondary",
    }[bet.result]

    return dbc.Card(
        dbc.CardBody(
            [
                team_deets_div,
                bet_description_h4,
                bettor_small,
                status_div,
                profit_div,
            ],
            className="text-center",
        ),
        color=result_color,
        inverse=True,
        className="mb-4",
    )


# Recursive function to display BetGroup and its children
def betgroup_to_layout(betgroup: BetGroup, level=1):
    children = []
    header = (
        html.H2
        if level == 1
        else html.H3 if level == 2 else html.H4 if level == 3 else html.H5 if level == 4 else html.H6
    )
    if betgroup.profit >= 0:
        profit_str = f"{betgroup.group_name} (Profit: {betgroup.profit:.2f}units -- {betgroup.hits} hits, {betgroup.misses} misses)"
    else:
        profit_str = f"{betgroup.group_name} (Loss: {betgroup.profit:.2f}units -- {betgroup.hits} hits, {betgroup.misses} misses)"
    children.append(
        header(
            profit_str,
            style={"marginTop": "24px"},
        )
    )
    if betgroup.bets:
        cards = [bet_to_card(bet) for bet in betgroup.bets]
        children.append(dbc.Row([dbc.Col(card, xs=12, sm=12, md=12, lg=6) for card in cards]))
    else:
        for sub in betgroup.sub_betgroups.values():
            children.append(betgroup_to_layout(sub, level=level + 1))
    return html.Div(children)


def gimme_the_goods(betgroups: list[BetGroup]):
    refresh_pending_cfb_betgroups(betgroups)
    return [
        html.H1("College Football Bets Tracker v0.1", style={"marginTop": "24px"}),
        html.P("(Early preview version) automatically tracks CFB bets from the best sports shows. More shows will be added. Data updates every time you hit the Refresh button.",),
        html.Div([betgroup_to_layout(bg) for bg in betgroups.values()]),
    ]


all_betgroups = load_all_cfb_betgroups_from_disk("/home/caleb/cfb-bets-tracker/bets")

# Compose layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, "/assets/styles.css"])
app.layout = dbc.Container(
    [
        html.Button("Refresh", id="refresh-button", className="btn btn-primary mb-3"),
        html.Div(id="content-div", children=gimme_the_goods(all_betgroups)),
    ],
    fluid=True,
    className="dbc",
)


@app.callback(Output("content-div", "children"), Input("refresh-button", "n_clicks"))
def update_content(n_clicks):
    return gimme_the_goods(all_betgroups)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=42069)
