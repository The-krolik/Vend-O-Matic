import pytest
import vendomatic as vom
import json
from typing import Type


@pytest.fixture
def app():
    app = vom.create_app()
    yield app

@pytest.fixture
def test_client(app):
    yield app.test_client()

@pytest.fixture
def vm():
    vm = vom.VendingMachine()
    yield vm

@pytest.fixture
def cvm():
    cvm = vom.VendingMachine()
    yield cvm


def test_machine_init(vm):
    assert vm.accepted_coins == 0
    assert len(vm.inventory) == vm.NUMBER_OF_DRINKS
    for i in range(0, len(vm.inventory)):
        assert vm.inventory[i] == vm.MAX_STOCKED

def test_accept_coin(vm):
    coins_before_insert = vm.accepted_coins
    vm.accept_coin()
    assert vm.accepted_coins == coins_before_insert + 1

def test_dispense_coins(vm):
    vm.accept_coin()
    total_coins = vm.accepted_coins
    dispensed_coins = vm.dispense_coins()
    assert dispensed_coins == total_coins

def test_dispense_drink(vm):
    vm.accepted_coins = vm.DRINK_PRICE - 1
    with pytest.raises(ValueError) as e_info:
        vm.dispense_drink(0)

    dispensed_drinks_before = vm.dispensed_drinks
    vm.accepted_coins = vm.DRINK_PRICE + 1
    dispensed_coins = vm.dispense_drink(0)
    dispensed_drinks_after = vm.dispensed_drinks
    assert vm.inventory[0] == vm.MAX_STOCKED - 1
    assert dispensed_coins == 1
    assert dispensed_drinks_after == dispensed_drinks_before + 1

    # test for out of stock
    vm.inventory[0] = 0
    vm.accepted_coins = vm.DRINK_PRICE
    with pytest.raises(ValueError) as e_info:
        vm.dispense_drink(0)


def test_home_put(test_client, cvm):
    response = test_client.put("/", headers={
        "coin": 1
    })
    cvm.accept_coin()
    assert response.status_code == 204
    assert response.headers["X-Coins"] == str(cvm.accepted_coins)

def test_home_delete(test_client, cvm):
    response = test_client.delete("/")
    dispensed_coins = cvm.dispense_coins()
    assert response.status_code == 204
    assert response.headers["X-Coins"] == str(dispensed_coins)

def test_inventory_get(test_client, cvm):
    response = test_client.get("/inventory")
    inventory = response.json
    assert response.status_code == 200
    assert inventory == cvm.inventory

def test_inventory_id_get(test_client, cvm):
    for i in range(0, cvm.NUMBER_OF_DRINKS):
        response = test_client.get(f"/inventory/{i}")
        n = response.json
        assert response.status_code == 200
        assert n == str(cvm.inventory[i])

def test_inventory_id_put(test_client, cvm):
    # make sure we have enough coins for the purchase
    for i in range(0, cvm.DRINK_PRICE):
        cvm.accept_coin()
        test_client.put("/")

    # buy drink 0
    dispensed_coins = cvm.dispense_drink(0)
    response = test_client.put("/inventory/0")
    dispensed_drinks = response.json
    assert response.status_code == 200
    assert response.headers["X-Coins"] == dispensed_coins
    assert response.headers["X-Inventory-Remaining"] == str(cvm.inventory[0])
    assert dispensed_drinks == str(cvm.dispensed_drinks)

# oos: out of stock
def test_inventory_id_put_oos(test_client, cvm):
    # buy drink 0 until out stock
    for i in range(0, cvm.inventory[0]):
        for j in range(0, cvm.DRINK_PRICE):
            test_client.put("/")
        test_client.put("/inventory/0")

    # put in enough coins to attempt to buy another
    for i in range(0, cvm.DRINK_PRICE):
        cvm.accept_coin()
        test_client.put("/")
    
    # try to buy it
    response = test_client.put("/inventory/0")
    assert response.status_code == 404
    assert response.headers["X-Coins"] == str(cvm.accepted_coins)

# nec: not enough coins
def test_inventory_id_put_nec(test_client, cvm):
    # make sure the vending machine has 0 coins
    test_client.delete("/")
    cvm.dispense_coins()

    # attempt to buy something
    response = test_client.put("/inventory/0")
    assert response.status_code == 403
    assert response.headers["X-Coins"] == str(cvm.accepted_coins)
