import pytest
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup
from moneypoly.board import Board
from moneypoly.bank import Bank
from moneypoly.dice import Dice
from moneypoly.config import STARTING_BALANCE, JAIL_POSITION

def test_player_movement():
    player = Player("Alice")
    player.move(5)
    assert player.position == 5
    player.move(36) # Wrap around board (size 40)
    assert player.position == 1
    assert player.balance == STARTING_BALANCE + 200 # GO salary

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

def test_bank_pay_out_insufficient_funds():
    bank = Bank()
    bank._funds = 100
    with pytest.raises(ValueError, match=r"only \$100 available"):
        bank.pay_out(200)

def test_dice_roll_range():
    dice = Dice()
    for _ in range(100):
        dice.roll()
        assert 1 <= dice.die1 <= 6
        assert 1 <= dice.die2 <= 6

def test_dice_doubles_jail():
    dice = Dice()
    # Mocking dice values
    dice.die1 = 1
    dice.die2 = 1
    # Manually increment streak as roll() does this
    if dice.is_doubles():
        dice.doubles_streak += 1
    assert dice.doubles_streak == 1
    
    dice.die1 = 2
    dice.die2 = 2
    if dice.is_doubles():
        dice.doubles_streak += 1
    assert dice.doubles_streak == 2
    
    dice.die1 = 3
    dice.die2 = 3
    if dice.is_doubles():
        dice.doubles_streak += 1
    assert dice.doubles_streak == 3
    assert dice.is_triple_doubles() is True
