"""Tests pour engine.features.camera."""

from engine.features.camera.logic import CameraState


class TestCameraState:
    def test_offset_initial_zero(self):
        cam = CameraState(800, 600)
        assert cam.offset_x == 0.0
        assert cam.offset_y == 0.0

    def test_mode_default_center(self):
        cam = CameraState(800, 600)
        assert cam.mode == "center"

    def test_update_center(self):
        cam = CameraState(800, 600)
        cam.update_center(500, 400)
        assert cam.offset_x == 500 - 400  # 500 - 800//2
        assert cam.offset_y == 400 - 300  # 400 - 600//2

    def test_update_center_negative_offset(self):
        cam = CameraState(800, 600)
        cam.update_center(100, 100)
        assert cam.offset_x < 0
        assert cam.offset_y < 0

    def test_update_box_no_move_if_inside(self):
        cam = CameraState(800, 600)
        cam.mode = "box"
        cam.update_box(400, 300, 16, 16)
        # Target inside box, offset should stay near 0
        assert cam.offset_x == 0.0
        assert cam.offset_y == 0.0

    def test_update_box_pushes_if_outside(self):
        cam = CameraState(800, 600)
        cam.mode = "box"
        cam.update_box(0, 0, 16, 16)
        # Target pushed left of box_left, so offset changes
        assert cam.offset_x <= 0

    def test_update_dispatches_by_mode(self):
        cam = CameraState(800, 600)
        cam.mode = "center"
        cam.update(500, 400)
        assert cam.offset_x == 500 - 400

        cam2 = CameraState(800, 600)
        cam2.mode = "box"
        cam2.update(400, 300, 16, 16)
        assert cam2.offset_x == 0.0
