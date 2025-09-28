from dataclasses import dataclass


@dataclass
class Team:
    full_name: str
    short_name: str
    abbreviation: str
    logo_url: str


@dataclass
class TeamInGame(Team):
    score: int
    is_home_team: bool
