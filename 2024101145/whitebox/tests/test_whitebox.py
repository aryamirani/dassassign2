import pytest
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup
from moneypoly.board import Board
from moneypoly.bank import Bank
from moneypoly.dice import Dice
from moneypoly.config import STARTING_BALANCE, JAIL_POSITION
from moneypoly.game import Game

# --- 1. Player Tests ---
def test_player_movement():
    player = Player("Alice")
    player.move(5)
    assert player.position == 5
    player.move(36) # Wrap around board (size 40)
    assert player.position == 1
    assert player.balance == STARTING_BALANCE + 200 # GO salary

def test_player_movement_wrap_arroud():
    player = Player("Alice")
    player.position = 38 # Assuming BOARD_SIZE=40
    player.move(5)
    assert player.position == 3 # (38+5)%40
    # verify salary added
    assert player.balance == STARTING_BALANCE + 200

def test_player_net_worth_simple():
    player = Player("Bob")
    player.balance = 1000
    assert player.net_worth() == 1000

def test_player_jail_status():
    player = Player("Charlie")
    player.go_to_jail()
    assert player.in_jail is True
    assert player.position == JAIL_POSITION

def test_player_add_money_negative_raises():
    player = Player("D")
    with pytest.raises(ValueError):
        player.add_money(-1)

# --- 2. Bank Tests ---
def test_bank_initial_state():
    bank = Bank()
    assert bank.get_balance() > 0
    assert bank.loan_count() == 0

def test_bank_collect_positive():
    bank = Bank()
    initial = bank.get_balance()
    bank.collect(100)
    assert bank.get_balance() == initial + 100

def test_bank_pay_out_valid():
    bank = Bank()
    initial = bank.get_balance()
    paid = bank.pay_out(500)
    assert paid == 500
    assert bank.get_balance() == initial - 500

def test_bank_pay_out_zero_or_negative():
    bank = Bank()
    assert bank.pay_out(0) == 0
    assert bank.pay_out(-100) == 0

def test_bank_pay_out_insufficient():
    bank = Bank()
    with pytest.raises(ValueError):
        bank.pay_out(bank.get_balance() + 1)

def test_bank_pay_out_insufficient_funds_message():
    bank = Bank()
    bank._funds = 100
    with pytest.raises(ValueError, match=r"only \$100 available"):
        bank.pay_out(200)

def test_bank_give_loan_positive():
    bank = Bank()
    player = Player("Test")
    initial_p = player.balance
    bank.give_loan(player, 1000)
    assert player.balance == initial_p + 1000
    assert bank.loan_count() == 1
    assert bank.total_loans_issued() == 1000

def test_bank_give_loan_zero_ignored():
    bank = Bank()
    player = Player("Test")
    bank.give_loan(player, 0)
    assert bank.loan_count() == 0

def test_bank_summary_no_crash(capsys):
    bank = Bank()
    bank.summary()
    captured = capsys.readouterr()
    assert "Bank reserves" in captured.out

# --- 3. Property & Mortgage Tests ---
def test_property_rent_doubling():
    group = PropertyGroup("Blue", "Blue")
    p1 = Property("P1", 1, 100, 10, group)
    p2 = Property("P2", 2, 100, 10, group)
    player = Player("Alice")
    
    p1.owner = player
    assert p1.get_rent() == 10 # Only one owned
    
    p2.owner = player
    assert p1.get_rent() == 20 # Full group owned

def test_mortgage_logic():
    p = Property("P1", 1, 100, 10)
    player = Player("Alice")
    player.balance = 100
    p.owner = player
    
    payout = p.mortgage()
    assert payout == 50
    assert p.is_mortgaged is True
    assert p.get_rent() == 0
    
    cost = p.unmortgage()
    assert cost == 55
    assert p.is_mortgaged is False

# --- 4. Dice Logic ---
def test_dice_roll_range():
    dice = Dice()
    for _ in range(100):
        dice.roll()
        assert 1 <= dice.die1 <= 6
        assert 1 <= dice.die2 <= 6

def test_dice_roll_totals():
    dice = Dice()
    for _ in range(100):
        total = dice.roll()
        assert 2 <= total <= 12

def test_dice_doubles_jail():
    dice = Dice()
    dice.die1 = 1
    dice.die2 = 1
    dice.doubles_streak = 0
    # Simulate first double
    if dice.is_doubles():
        dice.doubles_streak += 1
    assert dice.doubles_streak == 1
    
    # Simulate second double
    if dice.is_doubles():
        dice.doubles_streak += 1
    assert dice.doubles_streak == 2
    
    # Simulate third double
    if dice.is_doubles():
        dice.doubles_streak += 1
    assert dice.doubles_streak == 3
    assert dice.is_triple_doubles() is True

# --- 5. Board Tests ---
def test_board_get_property():
    board = Board()
    prop = board.get_property_at(1) # Mediterranean Avenue
    assert prop.name == "Mediterranean Avenue"
    assert board.get_property_at(0) is None

def test_board_size():
    board = Board()
    # 22 properties + special tiles (Go, Jail, etc.) = 40 total tiles
    assert len(board.properties) == 22

# --- 6. Game State & Flow ---
def test_game_init():
    game = Game(["P1", "P2"])
    assert len(game.players) == 2
    assert game.current_index == 0

def test_game_turn_advance():
    game = Game(["P1", "P2"])
    game.advance_turn()
    assert game.current_index == 1
    game.advance_turn()
    assert game.current_index == 0

def test_full_game_flow(monkeypatch):
    from moneypoly.game import Game
    monkeypatch.setattr('builtins.input', lambda _: 's') # Set input to 's' (skip)
    game = Game(["P1", "P2"])
    
    # Test turn 1
    p1 = game.players[0]
    initial_pos = p1.position
    game.play_turn()
    assert p1.position != initial_pos or p1.in_jail # Player moved or jailed
    
    # Test tax tiles
    p1.position = 4 # Income Tax
    game._move_and_resolve(p1, 0) # Trigger tile
    
    # Test go to jail
    p1.position = 30 # Go to jail
    game._move_and_resolve(p1, 0)
    assert p1.in_jail is True
    assert p1.position == 10
