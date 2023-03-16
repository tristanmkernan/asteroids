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
class PositionOffset:
    x: float = 0.0
    y: float = 0.0


@dataclasses.dataclass
class Position:
    x: float = 0.0
    y: float = 0.0

    rotation: float = 0.0

    @property
    def tuple(self):
        return (self.x, self.y)

    def distance(self, other: "Position") -> float:
        """
        Calculate Euclidian distance
        """
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def normalize_rotation(self):
        """
        keep rotation within (-pi, pi)
        """
        if self.rotation > math.pi:
            self.rotation -= math.pi * 2
        elif self.rotation < -math.pi:
            self.rotation += math.pi * 2


@dataclasses.dataclass
class Velocity:
    x: float = 0.0
    y: float = 0.0

    max: float = 0.0

    @property
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def clamp(self):
        """
        clamp to max speed
        """
        current_speed = math.sqrt(self.x**2 + self.y**2)

        if current_speed > self.max:
            ratio = self.max / current_speed

            self.x *= ratio
            self.y *= ratio

    def maximize(self):
        """
        set to max speed
        """
        current_speed = math.sqrt(self.x**2 + self.y**2)

        if current_speed < self.max:
            ratio = self.max / current_speed

            self.x *= ratio
            self.y *= ratio


@dataclasses.dataclass
class Acceleration:
    x: float = 0.0
    y: float = 0.0


@dataclasses.dataclass
class Rotation:
    # radians / ms
    speed: float = 0.0


@dataclasses.dataclass
class BulletAmmo:
    recharge_rate: float
    count: int
    max: int
    elapsed: float = 0.0

    @property
    def every(self):
        """
        How many seconds delay between recharge
        """
        return 1.0 / self.recharge_rate

    @property
    def full(self):
        return self.count == self.max

    @property
    def empty(self):
        return self.count == 0


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
class Renderable:
    kind: RenderableKind

    color: tuple = (0, 0, 255)

    # for circle
    radius: float = 0.0

    # for triangle
    height: float = 0.0
    rotation: float = 0.0

    # for offset
    offset: PositionOffset | None = None


@dataclasses.dataclass
class RenderableCollection:
    items: list[Renderable]


@dataclasses.dataclass
class Lifetime:
    remaining: float = 0.0
