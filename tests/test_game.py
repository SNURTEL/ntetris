# region imports ----------------------------------------------------------------
import time
import pytest

from testing_tools import *

enable_import_from_game_dir()

from game import Game, Active, Paused, Ended, GameEnded, StartMenu, Countdown


# endregion


def test_game_init(silent_screen, mock_json_operations):
    game = Game(silent_screen)


def test_game_prep_for_new_game(game):
    game._points = 234234
    game._board._block_move_period = 2342
    game._cleared_lines = 234
    game._level = 15

    game.prep_for_new_game(3)

    assert game.level == 3
    assert game.score == 0
    assert game.cleared_lines == 0
    assert game._board._block_move_period == game._block_movement_periods[3]


def test_game_get_speed(game):
    assert game._get_speed(5) == 0.3833333
    assert game._get_speed(27) == game._get_speed(19)


def test_game_update_scoreboard(game):
    game._points = 25
    game._scoreboard = [90, 80, 70, 60, 50, 40, 30, 20, 10, 0]
    game.update_scoreboard()
    new_sb = [90, 80, 70, 60, 50, 40, 30, 25, 20, 10]
    assert game._scoreboard == new_sb
    assert game._read_scoreboard(scoreboard_io) == new_sb

    game._points = 25
    game.update_scoreboard()
    assert game._scoreboard == new_sb
    assert game._read_scoreboard(scoreboard_io) == new_sb


def test_game_state_switching(game, monkeypatch):
    flag = False

    def flag_true(*args, **kwargs):
        nonlocal flag
        flag = True

    def flag_false(*args, **kwargs):
        nonlocal flag
        flag = False

    monkeypatch.setattr('game.Paused.greet', flag_true)
    monkeypatch.setattr('game.Ended.greet', flag_false)

    game.switch_to_state(Paused)
    assert flag
    assert isinstance(game._state, Paused)

    game.revert_state()
    assert flag
    assert isinstance(game._state, Ended)


def test_game_add_points(game):
    game.add_points(3)
    assert not game.ui.blinking_score
    assert game._points == 3
    game.add_points(34523452)
    assert game.ui.blinking_score
    assert game._points == 34523455


def test_game_runtime_exceptions(game, monkeypatch):
    class Flag(Exception):
        pass

    monkeypatch.setattr('curses.endwin', exception_raiser_factory(Flag))
    monkeypatch.setattr('game.Game._wait_till_next_tick', exception_raiser_factory(ImportError))

    with pytest.raises(Flag):
        game.run_game()

    monkeypatch.setattr('game.Game._wait_till_next_tick', exception_raiser_factory(AssertionError))

    with pytest.raises(Flag):
        game.run_game()

    monkeypatch.setattr('game.Game._wait_till_next_tick', empty_function)
    monkeypatch.setattr('game.Game.update_scoreboard', exception_raiser_factory(Flag))

    with pytest.raises(Flag):
        game.run_game()


def test_game_update_scoreboard_on_exit(game, monkeypatch):
    monkeypatch.setattr('game.Game._wait_till_next_tick', sys.exit)
    game._points = 999
    try:
        game.run_game()
    except SystemExit:
        pass

    assert game._read_scoreboard() == [999, 9, 8, 7, 6, 5, 4, 3, 2, 1]


def test_active(game, monkeypatch):
    monkeypatch.setattr('game.keyboard.is_pressed', lambda k: k == 1)

    game.switch_to_state(Active)
    game.state.handle_events()
    assert isinstance(game.state, Paused)

    monkeypatch.setattr('components.Board.update', exception_raiser_factory(GameEnded))
    monkeypatch.setattr('game.keyboard.is_pressed', empty_function)

    game.switch_to_state(Active)
    game.state.handle_events()
    assert isinstance(game.state, Ended)


def test_menu(game, monkeypatch):
    game._start_menu._last_update = 0
    monkeypatch.setattr('time.time', time.time_ns)

    monkeypatch.setattr('keyboard.is_pressed', lambda k: k == 105)
    game._state = game._start_menu
    game._state.handle_events()

    monkeypatch.setattr('keyboard.is_pressed', lambda k: k == 106)
    for _ in range(3):
        game._state.handle_events()

    monkeypatch.setattr('keyboard.is_pressed', lambda k: k == 57)
    game._state.handle_events()

    assert isinstance(game._state, Countdown)
    assert game._level == 3
