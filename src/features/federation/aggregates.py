from src.eventsourcing.exceptions import InvalidOperationError
from src.features.federation.events import ClubRegistered, FederationCreated, PlayerRegistered
from src.eventsourcing.aggregates import AggregateRoot
from multipledispatch import dispatch

class Federation(AggregateRoot):
    clubs : list[str] = []
    players : list[str] = []

    def __init__(self, first_creation : bool = False) -> None:
        super().__init__()
        if first_creation:
            self._apply_change(FederationCreated())

    @property
    def id(self) -> str:
        return "FFHB"
    
    @staticmethod
    def to_stream_id(id : str = "FFHB") -> str:
        return "FFHB"

    def register_club(self, registration_number : str, name : str, owner_id : str) -> None:
        if registration_number in self.clubs:
            raise InvalidOperationError(f"Club with registration number {registration_number} already registered")
        self._apply_change(ClubRegistered(registration_number=registration_number, name=name, owner_id=owner_id))

    def register_player(self, license_id : str) -> None:
        if license_id in self.players:
            raise InvalidOperationError(f"Player with license id {license_id} already registered")
        self._apply_change(PlayerRegistered(license_id=license_id))


    @dispatch(ClubRegistered)
    def _apply(self, e: ClubRegistered) -> None:
        self.clubs.append(e.registration_number)

    @dispatch(FederationCreated)
    def _apply(self, e: FederationCreated) -> None:
        self.clubs = []
        self.players = []

    @dispatch(PlayerRegistered)
    def _apply(self, e: PlayerRegistered) -> None:
        self.players.append(e.license_id)