

import os
from typing import Generic, TypeVar
from uuid import UUID
from src.common.base_entity import BaseEntity
import json

T = TypeVar("T", bound=BaseEntity)

class BaseRepository(Generic[T]):

    def __init__(self, entity_type: type[T]):

        self.db : dict[UUID, T] = {}
        self.file_path = f"./db/{entity_type.__name__}.json"
        self.entity_type = entity_type
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                db_dict = json.load(f)
                for id, entity in db_dict.items():
                    self.db[id] = self.entity_type.model_construct(**entity)

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump({id: entity.model_dump() for id, entity in self.db.items()}, f)

    async def create(self, entity: T) -> T:
        self.db[entity.id] = entity
        self.save()
        return entity
    
    async def get(self, id: UUID) -> T:
        return self.db[id]
    
    async def update(self, entity: T) -> T:
        self.db[entity.id] = entity
        self.save()
        return entity
    
    async def delete(self, id: UUID) -> None:
        del self.db[id]
        self.save()

    async def list(self) -> list[T]:
        return list(self.db.values())