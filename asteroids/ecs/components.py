import dataclasses
import math

from .enums import CollidableKind, RenderableKind, ScoreEventKind


@dataclasses.dataclass
class Spawning:
    rate: float = 0.0
    elapsed: float = 0.0

    @property
    def every(self):
        """
        How many seconds delay between spawns
        """
        return 1.0 / self.rate


class Asteroid:
    pass


@dataclasses.dataclass
class Renderable:
    kind: RenderableKind

    color: tuple = (0, 0, 255)

    # for circle
    radius: float = 0.0

    # for triangle
    height: float = 0.0
    rotation: float = 0.0


@dataclasses.dataclass
class Position:
    x: float = 0.0
    y: float = 0.0

    @property
    def tuple(self):
        return (self.x, self.y)

    def distance(self, other: "Position") -> float:
        """
        Calculate Euclidian distance
        """
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclasses.dataclass
class Velocity:
    x: float = 0.0
    y: float = 0.0

    max: float = 0.0


@dataclasses.dataclass
class Acceleration:
    x: float = 0.0
    y: float = 0.0


@dataclasses.dataclass
class Bullet:
    pass


@dataclasses.dataclass
class Collidable:
    kind: CollidableKind

    # for circle
    radius: float = 0.0

    # for triangle
    height: float = 0.0
    rotation: float = 0.0


@dataclasses.dataclass
class ScoreTracker:
    scores: dict[ScoreEventKind, int] = dataclasses.field(
        default_factory=lambda: {kind: 0 for kind in ScoreEventKind}
    )
    recent_events: list[ScoreEventKind] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class PlayerKeyInput:
    keydowns: set[int] = dataclasses.field(default_factory=set)


class PlayerShip:
    pass


@dataclasses.dataclass
class Rotation:
    rotation: float = 0.0
