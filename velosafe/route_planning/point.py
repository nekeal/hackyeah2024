from dataclasses import dataclass


@dataclass
class Point:
    latitude: float
    longitude: float


    def __iter__(self):
        return iter([self.latitude, self.longitude])
