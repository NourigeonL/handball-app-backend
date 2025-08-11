

from src.common.eventsourcing.exceptions import InvalidOperationError


class Collective:

    def __init__(self, collective_id : str):
        self.collective_id = collective_id
        self.players = []

    def add_player(self, player_id : str) -> None:
        if player_id in self.players:
            raise InvalidOperationError(f"Player {player_id} already assigned to collective {self.collective_id}")
        self.players.append(player_id)

    def remove_player(self, player_id : str) -> None:
        if player_id not in self.players:
            raise InvalidOperationError(f"Player {player_id} not found in collective {self.collective_id}")
        self.players.remove(player_id)