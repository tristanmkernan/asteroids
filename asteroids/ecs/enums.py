import enum


class CollidableKind(enum.IntEnum):
    Circle = enum.auto()
    Triangle = enum.auto()


class ScoreEventKind(enum.IntEnum):
    EnemyKill = enum.auto()
    Time = enum.auto()


class InputEventKind(enum.IntEnum):
    KeyUp = enum.auto()
    KeyDown = enum.auto()


class PlayerActionKind(enum.IntEnum):
    Accelerate = enum.auto()
    StopAccelerating = enum.auto()

    Decelerate = enum.auto()
    StopDecelerating = enum.auto()

    RotateLeft = enum.auto()
    StopRotateLeft = enum.auto()

    RotateRight = enum.auto()
    StopRotateRight = enum.auto()

    Fire = enum.auto()


class RenderableKind(enum.IntEnum):
    Circle = enum.auto()
    Triangle = enum.auto()
