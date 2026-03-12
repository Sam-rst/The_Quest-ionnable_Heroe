"""AnimationController: gestion des frames et vitesse d'animation."""

from engine.features.sprite.components import AnimationSetComponent, SpriteComponent


def update_animation(anim: AnimationSetComponent, sprite: SpriteComponent,
                     scale: float) -> None:
    """Met à jour la frame courante de l'animation."""
    frames = anim.animations.get(anim.current_animation)
    if not frames:
        return

    # Initialiser l'image si pas encore définie
    if sprite.image is None:
        sprite.image = frames[0]

    if anim.is_attack:
        if not anim.is_attack_animating:
            anim.is_attack_animating = True
            anim.frame_index = 0

        while anim.frame_index < len(frames):
            sprite.image = frames[int(anim.frame_index)]
            anim.frame_index += anim.speed

        anim.frame_index = 0
        anim.is_attack = False
        anim.is_attack_animating = False
        return

    if anim.is_playing:
        anim.frame_index += anim.speed
        if anim.frame_index >= len(frames):
            anim.frame_index = 0
        sprite.image = frames[int(anim.frame_index)]
