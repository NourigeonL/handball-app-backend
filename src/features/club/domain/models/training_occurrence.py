
from datetime import datetime


class TrainingOccurence:

    def __init__(self, start_time : datetime, end_time : datetime, training_plan_id : str, collective_id : str):
        self._start_time = start_time
        self._end_time = end_time
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True