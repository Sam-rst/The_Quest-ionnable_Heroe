"""Widgets UI réutilisables."""

from engine.features.ui.logic import UIElement


class Button(UIElement):
    def __init__(self, name: str, x: float, y: float, width: float, height: float,
                 label: str = "") -> None:
        super().__init__(name, x, y, width, height)
        self.label = label


class Label(UIElement):
    def __init__(self, name: str, x: float, y: float, text: str = "") -> None:
        super().__init__(name, x, y)
        self.text = text


class ProgressBar(UIElement):
    def __init__(self, name: str, x: float, y: float, width: float, height: float,
                 value: float = 1.0) -> None:
        super().__init__(name, x, y, width, height)
        self.value = value  # 0.0 to 1.0
