from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class LastRecordedEventPosition(Base):
    __tablename__ = "last_recorded_event_position"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    position: Mapped[int] = mapped_column(Integer, default=0)


class User(Base):
    __tablename__ = "user"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=True)

class Club(Base):
    __tablename__ = "club"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    registration_number: Mapped[str] = mapped_column(String, nullable=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey(User.id), nullable=True)
    number_of_players: Mapped[int] = mapped_column(Integer, default=0)


class Collective(Base):
    __tablename__ = "collective"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    club_id: Mapped[str] = mapped_column(ForeignKey(Club.id))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, nullable=True)
    number_of_players: Mapped[int] = mapped_column(Integer, default=0)
    players: Mapped[list["CollectivePlayer"]] = relationship(back_populates="collective")

class Player(Base):
    __tablename__ = "player"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    club_id: Mapped[str] = mapped_column(ForeignKey(Club.id), nullable=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    gender: Mapped[str] = mapped_column(String)
    date_of_birth: Mapped[str] = mapped_column(String)
    license_number: Mapped[str] = mapped_column(String, nullable=True)
    license_type: Mapped[str] = mapped_column(String, nullable=True)

class CollectivePlayer(Base):
    __tablename__ = "collective_player"
    collective_id: Mapped[str] = mapped_column(ForeignKey(Collective.id), primary_key=True)
    player_id: Mapped[str] = mapped_column(ForeignKey(Player.id), primary_key=True)
    collective: Mapped[Collective] = relationship(back_populates="players")
    player: Mapped[Player] = relationship()
