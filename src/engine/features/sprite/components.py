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
        # Cache pour éviter pygame.transform.scale à chaque frame
        self._cached_scaled = None
        self._cached_raw_ref = None
        self._cached_w: int = 0
        self._cached_h: int = 0

    def get_scaled(self, w: int, h: int):
        """Retourne l'image scalée cachée si la frame n'a pas changé."""
        if (self._cached_scaled is not None
                and self.image is self._cached_raw_ref
                and self._cached_w == w and self._cached_h == h):
            return self._cached_scaled
        return None

    def set_scaled(self, raw, scaled, w: int, h: int) -> None:
        """Stocke l'image scalée en cache."""
        self._cached_raw_ref = raw
        self._cached_scaled = scaled
        self._cached_w = w
        self._cached_h = h


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
