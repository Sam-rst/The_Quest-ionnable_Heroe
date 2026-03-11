"""UIState: arbre d'éléments UI."""


class UIElement:
    def __init__(self, name: str = "", x: float = 0, y: float = 0,
                 width: float = 0, height: float = 0) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.children: list[UIElement] = []

    def contains_point(self, px: float, py: float) -> bool:
        return (self.x <= px <= self.x + self.width and
                self.y <= py <= self.y + self.height)
