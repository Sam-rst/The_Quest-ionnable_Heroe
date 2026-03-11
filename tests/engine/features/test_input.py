"""Tests pour engine.features.input."""

from engine.features.input.logic import InputAction, InputState, InputMap


class TestInputAction:
    def test_members_exist(self):
        assert InputAction.MOVE_UP
        assert InputAction.MOVE_DOWN
        assert InputAction.MOVE_LEFT
        assert InputAction.MOVE_RIGHT
        assert InputAction.SHOOT
        assert InputAction.INTERACT
        assert InputAction.PICKUP
        assert InputAction.ESCAPE


class TestInputState:
    def test_press_and_is_pressed(self):
        s = InputState()
        s.press(InputAction.MOVE_UP)
        assert s.is_pressed(InputAction.MOVE_UP)

    def test_just_pressed(self):
        s = InputState()
        s.press(InputAction.MOVE_UP)
        assert s.is_just_pressed(InputAction.MOVE_UP)

    def test_clear_frame_clears_just_pressed(self):
        s = InputState()
        s.press(InputAction.MOVE_UP)
        s.clear_frame()
        assert not s.is_just_pressed(InputAction.MOVE_UP)
        assert s.is_pressed(InputAction.MOVE_UP)

    def test_release(self):
        s = InputState()
        s.press(InputAction.MOVE_UP)
        s.release(InputAction.MOVE_UP)
        assert not s.is_pressed(InputAction.MOVE_UP)

    def test_mouse_pos(self):
        s = InputState()
        s.set_mouse((100, 200), False)
        assert s.mouse_pos == (100, 200)

    def test_mouse_clicked(self):
        s = InputState()
        s.set_mouse((0, 0), True)
        assert s.mouse_clicked

    def test_clear_frame_clears_mouse_clicked(self):
        s = InputState()
        s.set_mouse((0, 0), True)
        s.clear_frame()
        assert not s.mouse_clicked

    def test_press_twice_not_just_pressed(self):
        s = InputState()
        s.press(InputAction.MOVE_UP)
        s.clear_frame()
        s.press(InputAction.MOVE_UP)
        assert not s.is_just_pressed(InputAction.MOVE_UP)


class TestInputMap:
    def test_bind_and_get_action(self):
        m = InputMap()
        m.bind(119, InputAction.MOVE_UP)  # 'w' key
        assert m.get_action(119) is InputAction.MOVE_UP

    def test_unbound_returns_none(self):
        m = InputMap()
        assert m.get_action(999) is None
