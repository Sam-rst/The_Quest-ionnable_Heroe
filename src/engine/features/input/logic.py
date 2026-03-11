"""Input system: actions abstraites, indépendantes de pygame."""

from enum import Enum, auto


class InputAction(Enum):
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    SHOOT = auto()
    INTERACT = auto()
    PICKUP = auto()
    OPEN_SHOP = auto()
    USE_POTION = auto()
    ESCAPE = auto()
    CONFIRM = auto()


class InputState:
    """Etat des inputs à un instant donné — rempli par un adapter."""

    def __init__(self) -> None:
        self._pressed: set[InputAction] = set()
        self._just_pressed: set[InputAction] = set()
        self._mouse_pos: tuple[int, int] = (0, 0)
        self._mouse_clicked: bool = False

    def is_pressed(self, action: InputAction) -> bool:
        return action in self._pressed

    def is_just_pressed(self, action: InputAction) -> bool:
        return action in self._just_pressed

    @property
    def mouse_pos(self) -> tuple[int, int]:
        return self._mouse_pos

    @property
    def mouse_clicked(self) -> bool:
        return self._mouse_clicked

    def clear_frame(self) -> None:
        self._just_pressed.clear()
        self._mouse_clicked = False

    def press(self, action: InputAction) -> None:
        if action not in self._pressed:
            self._just_pressed.add(action)
        self._pressed.add(action)

    def release(self, action: InputAction) -> None:
        self._pressed.discard(action)

    def set_mouse(self, pos: tuple[int, int], clicked: bool) -> None:
        self._mouse_pos = pos
        self._mouse_clicked = clicked


class InputMap:
    """Mappe des codes clavier vers des InputAction."""

    def __init__(self) -> None:
        self._key_map: dict[int, InputAction] = {}

    def bind(self, key_code: int, action: InputAction) -> None:
        self._key_map[key_code] = action

    def get_action(self, key_code: int) -> InputAction | None:
        return self._key_map.get(key_code)
