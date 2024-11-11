from abc import ABC, abstractmethod


class LogicError(Exception):
    pass


class DbEntityAlreadyExists(LogicError, ABC):
    @property
    @abstractmethod
    def entity_name(self) -> str:
        """
        This property will be supplied by 
        the inheriting classes individually.
        """
        pass

    def __init__(self, name: str):
        super().__init__(f"{self.entity_name} already exists: {name}")
