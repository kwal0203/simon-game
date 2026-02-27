from apps.api.main import increment_state


def test_increment_state_handles_existing_value():
    assert increment_state(7) == 8


def test_increment_state_adds_one():
    assert increment_state(0) == 1
