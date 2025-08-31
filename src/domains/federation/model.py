from datetime import date
from multipledispatch import dispatch
from pydantic import BaseModel
from src.common.eventsourcing.event import IEvent
from src.common.eventsourcing.exceptions import InvalidOperationError
from src.common.guid import guid
from src.common.enums import Gender, LicenseType
from src.common.eventsourcing.aggregates import AggregateRoot
from src.domains.federation.events import PlayerLicenseRegistered


class PlayerLicense(BaseModel):
    player_id: str
    license_number: str
    license_type: LicenseType


class Federation(AggregateRoot):

    @property
    def id(self) -> str:
        return self.__id

    @staticmethod
    def to_stream_id(id: str) -> str:
        return id

    def __init__(self):
        super().__init__()
        self.__id = "FFHB"
        self.player_licenses : dict[str, PlayerLicense] = {}

    def get_player_license(self, license_number: str) -> PlayerLicense | None:
        return self.player_licenses.get(license_number)

    
    def register_player_license(self, player_id: str, license_number: str, license_type: LicenseType, actor_id: str):
        if license:= self.player_licenses.get(license_number):
            if license.player_id != player_id:
                raise InvalidOperationError(f"License {license_number} already registered to player {license.player_id}")
        self._apply_change(PlayerLicenseRegistered(player_id=player_id, license_number=license_number, license_type=license_type, actor_id=actor_id))


    @dispatch(PlayerLicenseRegistered)
    def _apply(self, event: PlayerLicenseRegistered):
        self.player_licenses[event.license_number] = PlayerLicense(player_id=event.player_id, license_number=event.license_number, license_type=event.license_type)