
from datetime import datetime

from src.common.enums import TrainingOccurencePlayerStatus


class TrainingOccurence:

    def __init__(self, id: str, start_time : datetime, end_time : datetime, training_plan_id : str):
        self._start_time = start_time
        self._end_time = end_time
        self._cancelled = False
        self._players = {}

    def cancel(self) -> None:
        self._cancelled = True

    def mark_player_present(self, player_id : str) -> None:
        if player_id not in self._players:
            self._players[player_id] = TrainingOccurencePlayerStatus.PRESENT

    def mark_player_absent(self, player_id : str) -> None:
        if player_id not in self._players:
            self._players[player_id] = TrainingOccurencePlayerStatus.ABSENT

    def mark_player_late(self, player_id : str) -> None:
        if player_id not in self._players:
            self._players[player_id] = TrainingOccurencePlayerStatus.LATE

    def mark_player_absent_without_reason(self, player_id : str) -> None:
        if player_id not in self._players:
            self._players[player_id] = TrainingOccurencePlayerStatus.ABSENT_WITHOUT_REASON

    def remove_player(self, player_id : str) -> None:
        if player_id in self._players:
            self._players.pop(player_id)
