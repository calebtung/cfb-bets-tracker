from dataclasses import dataclass
from team import TeamInGame


@dataclass
class Game:
    teams: list[TeamInGame]
    date: str
    is_over: bool
    is_neutral_site: bool

    def get_team(self, team_name: str):
        for team in self.teams:
            if team.full_name == team_name or team.short_name == team_name or team.abbreviation == team_name:
                return team
        raise ValueError(f"Game does not contain team: {team_name}")
    
    def get_opposing_team(self, team_name: str):
        for i, team in enumerate(self.teams):
            if team.full_name == team_name or team.short_name == team_name or team.abbreviation == team_name:
                if i == 0:
                    return self.teams[1]
                else:
                    return self.teams[0]
        raise ValueError(f"Game does not contain team: {team_name}")