from dataclasses import dataclass, asdict


@dataclass
class Game:
    home_team: str
    home_team_logo_url: str
    away_team: str
    away_team_logo_url: str
    date: str
    is_neutral_site: bool

    def as_dict(self):
        return asdict(self)


@dataclass
class Score:
    home_team_score: int
    away_team_score: int
    is_final: bool

    def as_dict(self):
        return asdict(self)
