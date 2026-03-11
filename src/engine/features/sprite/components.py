"""Sprite components — données d'affichage."""

from engine.core.component import Component


class SpriteComponent(Component):
    """Contient l'image courante et les dimensions pour le rendu."""

    def __init__(self, sprite_id: str = "", scale: float = 4,
                 visible: bool = True, layer: int = 0) -> None:
        self.sprite_id = sprite_id
        self.scale = scale
        self.visible = visible
        self.layer = layer
        self.image = None  # sera un pygame.Surface après chargement
        self.width: float = 0
        self.height: float = 0


class AnimationSetComponent(Component):
    """Contient les animations par direction/action."""

    def __init__(self) -> None:
        self.animations: dict[str, list] = {}
        self.current_animation: str = "Bottom Walk"
        self.frame_index: float = 0.0
        self.speed: float = 0.5
        self.is_playing: bool = False
        self.is_attack: bool = False
        self.is_attack_animating: bool = False
