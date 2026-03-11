"""Camera logic: calcul de l'offset (center/box), pas de pygame."""

from __future__ import annotations


class CameraState:
    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.mode: str = "center"

        # Box camera
        self.border_left = 300
        self.border_right = 300
        self.border_top = 200
        self.border_bottom = 200
        self._box_left = self.border_left
        self._box_top = self.border_top
        self._box_width = screen_width - self.border_left - self.border_right
        self._box_height = screen_height - self.border_top - self.border_bottom

    def update_center(self, target_x: float, target_y: float) -> None:
        self.offset_x = target_x - self.screen_width // 2
        self.offset_y = target_y - self.screen_height // 2

    def update_box(self, target_x: float, target_y: float,
                   target_w: float, target_h: float) -> None:
        box_right = self._box_left + self._box_width
        box_bottom = self._box_top + self._box_height

        if self._box_top < 0:
            self._box_top = 0
        if self._box_left < 0:
            self._box_left = 0

        if target_x < self._box_left:
            self._box_left = target_x
        if target_x + target_w > box_right:
            self._box_left = target_x + target_w - self._box_width

        if target_y < self._box_top:
            self._box_top = target_y
        if target_y + target_h > box_bottom:
            self._box_top = target_y + target_h - self._box_height

        self.offset_x = self._box_left - self.border_left
        self.offset_y = self._box_top - self.border_top

    def update(self, target_x: float, target_y: float,
               target_w: float = 0, target_h: float = 0) -> None:
        if self.mode == "center":
            self.update_center(target_x, target_y)
        elif self.mode == "box":
            self.update_box(target_x, target_y, target_w, target_h)
