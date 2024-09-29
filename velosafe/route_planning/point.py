from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    latitude: float
    longitude: float

    def __iter__(self):
        return iter([self.latitude, self.longitude])

    def __lt__(self, other):
        return tuple(self) < tuple(other)