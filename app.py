import dash
from dash import html
import dash_bootstrap_components as dbc
import os
import pickle
from betgroup import BetGroup
from bet import BetTypes

# Helper to recursively load all .bets files in bets folder
def load_all_betgroups(bets_folder):
    betgroups = []
    for root, dirs, files in os.walk(bets_folder):
        for file in files:
            if file.endswith("output.bets"):
                with open(os.path.join(root, file), "rb") as f:
                    betgroups.append(pickle.load(f))
    return betgroups

# Helper to display a single bet as a dbc.Card
def bet_to_card(bet):
    game = bet.game
    teams = game.teams
    team_cards = []
    for team in teams:
        logo = html.Img(src=team.logo_url, height="40px", style={"marginRight": "8px"})
        score = html.Span(f"{team.full_name} ({team.abbreviation}) - {team.score}", style={"fontWeight": "bold" if hasattr(bet, "taking_team") and team.full_name == getattr(bet, "taking_team").full_name else "normal"})
        team_cards.append(html.Div([logo, score], style={"display": "flex", "alignItems": "center"}))

    bet_type_str = ""
    if bet.bet_type == BetTypes.MONEYLINE.value:
        bet_type_str = f"{bet.taking_team.full_name} Moneyline pick by {bet.bettor}"
    elif bet.bet_type == BetTypes.SPREAD.value:
        bet_type_str = f"{bet.taking_team.full_name} {bet.taking_spread:+} pick by {bet.bettor}"
    elif bet.bet_type == BetTypes.OVER.value:
        bet_type_str = f"Over {bet.taking_points} pick by {bet.bettor}"
    elif bet.bet_type == BetTypes.UNDER.value:
        bet_type_str = f"Under {bet.taking_points} pick by {bet.bettor}"
    elif bet.bet_type == BetTypes.TEAM_OVER.value:
        bet_type_str = f"{bet.taking_team.full_name} Over {bet.taking_points} pick by {bet.bettor}"
    elif bet.bet_type == BetTypes.TEAM_UNDER.value:
        bet_type_str = f"{bet.taking_team.full_name} Under {bet.taking_points} pick by {bet.bettor}"

    result_color = {
        "hit": "success",
        "miss": "danger",
        "push": "warning",
        "pending": "secondary"
    }[bet.result]

    return dbc.Card(
        dbc.CardBody([
            html.Div(team_cards, style={"display": "flex", "gap": "16px"}),
            html.H5(bet_type_str, className="card-title", style={"marginTop": "10px"}),
            html.Div([
                html.Span(f"Odds: {bet.odds}", style={"marginRight": "16px"}),
                html.Span(f"Result: {bet.result.capitalize()}", className=f"text-{result_color}", style={"marginRight": "16px"}),
                html.Span(f"Profit: {bet.resulting_unit_profit:.2f}", style={"marginRight": "16px"}),
                html.Span(f"Game Date: {game.date}")
            ], style={"marginTop": "8px"})
        ]),
        color=result_color,
        inverse=True,
        style={"marginBottom": "16px"}
    )

# Recursive function to display BetGroup and its children
def betgroup_to_layout(betgroup, level=1):
    children = []
    header = html.H2 if level == 1 else html.H3 if level == 2 else html.H4 if level == 3 else html.H5
    children.append(header(f"{betgroup.group_name} (Profit: {betgroup.profit:.2f})", style={"marginTop": "24px"}))
    if betgroup.bets:
        for bet in betgroup.bets:
            children.append(bet_to_card(bet))
    else:
        for sub in betgroup.sub_betgroups.values():
            children.append(betgroup_to_layout(sub, level=level+1))
    return html.Div(children, style={"marginLeft": f"{level*16}px"})

# Load all betgroups
all_betgroups = load_all_betgroups("/home/caleb/cfb-bets-tracker/bets")

# Compose layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.layout = dbc.Container(
    [
        html.H1("CFB Bets Tracker", style={"marginTop": "24px"}),
        html.Div([betgroup_to_layout(bg) for bg in all_betgroups])
    ],
    fluid=True,
    className="dbc"
)

if __name__ == "__main__":
    app.run(debug=True)
