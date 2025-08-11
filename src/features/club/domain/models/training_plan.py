
from datetime import date, datetime
from src.common.eventsourcing.exceptions import InvalidOperationError
from src.features.club.domain.models.collective import Collective


class TrainingPlan:

    def __init__(self, training_plan_id : str, day_of_week : str, start_time : datetime, end_time : datetime, from_date: date, to_date: date, skip_public_holidays : bool, assigned_collectives : list[Collective]):
        self.training_plan_id = training_plan_id
        self.collectives = assigned_collectives
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.skip_public_holidays = skip_public_holidays
        self.from_date = from_date
        self.to_date = to_date
