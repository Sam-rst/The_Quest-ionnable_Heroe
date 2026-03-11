"""Tests pour engine.features.sprite."""

import json
from engine.features.sprite.components import SpriteComponent, AnimationSetComponent
from engine.features.sprite.animation import update_animation
from engine.features.sprite.asset_loader import AssetLoader


class TestSpriteComponent:
    def test_defaults(self):
        s = SpriteComponent()
        assert s.sprite_id == ""
        assert s.scale == 4
        assert s.visible is True
        assert s.layer == 0
        assert s.image is None

    def test_custom(self):
        s = SpriteComponent(sprite_id="hero", scale=2, visible=False, layer=5)
        assert s.sprite_id == "hero"
        assert s.scale == 2
        assert s.visible is False
        assert s.layer == 5


class TestAnimationSetComponent:
    def test_defaults(self):
        a = AnimationSetComponent()
        assert a.animations == {}
        assert a.current_animation == "Bottom Walk"
        assert a.frame_index == 0.0
        assert a.is_playing is False


class TestUpdateAnimation:
    def test_advance_frame(self):
        anim = AnimationSetComponent()
        sprite = SpriteComponent()
        anim.animations["Bottom Walk"] = ["frame0", "frame1", "frame2"]
        anim.is_playing = True
        anim.speed = 1.0
        update_animation(anim, sprite, 4)
        assert sprite.image == "frame1"

    def test_wrap_around(self):
        anim = AnimationSetComponent()
        sprite = SpriteComponent()
        anim.animations["Bottom Walk"] = ["frame0", "frame1"]
        anim.is_playing = True
        anim.speed = 1.0
        anim.frame_index = 1.5
        update_animation(anim, sprite, 4)
        assert anim.frame_index == 0
        assert sprite.image == "frame0"

    def test_not_playing_noop(self):
        anim = AnimationSetComponent()
        sprite = SpriteComponent()
        anim.animations["Bottom Walk"] = ["frame0"]
        anim.is_playing = False
        update_animation(anim, sprite, 4)
        assert sprite.image is None

    def test_no_frames_noop(self):
        anim = AnimationSetComponent()
        sprite = SpriteComponent()
        anim.is_playing = True
        update_animation(anim, sprite, 4)
        assert sprite.image is None


class TestAssetLoader:
    def test_manifest_valid(self, tmp_path):
        manifest = {"sprites": {"hero": {"base_path": "characters/hero"}}}
        path = str(tmp_path / "manifest.json")
        with open(path, "w") as f:
            json.dump(manifest, f)
        loader = AssetLoader(path)
        assert loader.manifest == manifest

    def test_manifest_missing(self, tmp_path):
        path = str(tmp_path / "nope.json")
        loader = AssetLoader(path)
        assert loader.manifest == {}

    def test_manifest_corrupted(self, tmp_path):
        path = str(tmp_path / "bad.json")
        with open(path, "w") as f:
            f.write("not json!")
        loader = AssetLoader(path)
        assert loader.manifest == {}

    def test_manifest_caching(self, tmp_path):
        manifest = {"sprites": {}}
        path = str(tmp_path / "manifest.json")
        with open(path, "w") as f:
            json.dump(manifest, f)
        loader = AssetLoader(path)
        m1 = loader.manifest
        m2 = loader.manifest
        assert m1 is m2
