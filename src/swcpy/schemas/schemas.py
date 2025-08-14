from datetime import datetime
from typing import List

from pydantic import ConfigDict, BaseModel


class Performance(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    performance_id: int
    player_id: int
    week_number: str
    fantasy_points: float
    last_changed_date: datetime


class PlayerBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    player_id: int
    gsis_id: str
    first_name: str
    last_name: str
    position: str
    last_changed_date: datetime


class Player(PlayerBase):
    model_config = ConfigDict(from_attributes=True)
    performances: List[Performance]


class TeamBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    league_id: int
    team_id: int
    team_name: str
    last_changed_date: datetime


class Team(TeamBase):
    model_config = ConfigDict(from_attributes=True)
    players: List[PlayerBase] = []


class League(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    league_id: int
    league_name: str
    scoring_type: str
    last_changed_date: datetime
    teams: List[TeamBase] = []


class Counts(BaseModel):
    league_count: int
    team_count: int
    player_count: int
