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
    test_client = app.test_client()
    yield test_client

# for vending machine tests
@pytest.fixture
def vm():
    vm = vom.VendingMachine()
    yield vm

# for vending machine interface tests
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
    returned_coins = vm.return_coins()
    assert returned_coins == total_coins

def test_dispense_drink(vm):
    vm.accepted_coins = vm.DRINK_PRICE - 1
    returned_coins = vm.dispense_drink(0)
    assert returned_coins == -1

    dispensed_drinks_before = vm.dispensed_drinks
    vm.accepted_coins = vm.DRINK_PRICE + 1
    returned_coins = vm.dispense_drink(0)
    dispensed_drinks_after = vm.dispensed_drinks
    assert vm.inventory[0] == vm.MAX_STOCKED - 1
    assert returned_coins == 1
    assert dispensed_drinks_after == dispensed_drinks_before + 1

    # test for out of stock
    vm.inventory[0] = 0
    vm.accepted_coins = vm.DRINK_PRICE
    returned_coins = vm.dispense_drink(0)
    assert returned_coins == -2


def test_home_put(test_client, cvm):
    # test giving a coin
    cvm.accept_coin()
    response = test_client.put("/", json={"coin": 1})
    assert response.status_code == 204
    assert response.headers["X-Coins"] == str(cvm.accepted_coins)

    # test giving multiple coins
    response = test_client.put("/", json={"coin": 3})
    assert response.status_code == 404

    # test attempting to give a coin without json body
    response = test_client.put("/")
    assert response.status_code == 404

    # test giving a coin with incorrect content type
    response = test_client.put("/", data={"coin: 1"})
    assert response.status_code == 404

def test_home_delete(test_client, cvm):
    # test getting our coins back
    returned_coins = cvm.return_coins()
    response = test_client.delete("/")
    assert response.status_code == 204
    assert response.headers["X-Coins"] == str(returned_coins)

def test_inventory_get(test_client, cvm):
    # test retrieving the inventory
    response = test_client.get("/inventory")
    inventory = response.json
    assert response.status_code == 200
    assert inventory == cvm.inventory

def test_inventory_id_get(test_client, cvm):
    # test getting the number of remaining drinks of each type
    for i in range(0, cvm.NUMBER_OF_DRINKS):
        response = test_client.get(f"/inventory/{i}")
        n = response.text
        assert response.status_code == 200
        assert n == str(cvm.inventory[i])

def test_inventory_id_put(test_client, cvm):
    # make sure we have enough coins for the purchase
    for i in range(0, cvm.DRINK_PRICE):
        cvm.accept_coin()
        test_client.put("/", json={"coin": 1})

    # buy drink 0
    returned_coins = cvm.dispense_drink(0)
    response = test_client.put("/inventory/0")
    dispensed_drinks = response.json["quantity"]
    assert response.status_code == 200
    assert response.headers["X-Coins"] == str(returned_coins)
    assert response.headers["X-Inventory-Remaining"] == str(cvm.inventory[0])
    assert dispensed_drinks == cvm.dispensed_drinks

# nec: not enough coins
def test_inventory_id_put_nec(test_client, cvm):
    # make sure the vending machine has 0 coins
    cvm.return_coins()
    test_client.delete("/")

    # attempt to buy drink 0 with no coins
    response = test_client.put("/inventory/0")
    assert response.status_code == 403
    assert response.headers["X-Coins"] == str(cvm.accepted_coins)

    # attempt to buy drink 0 with only one coin
    if cvm.DRINK_PRICE > 1:
        cvm.accept_coin()
        test_client.put("/", json={"coin": 1})
        response = test_client.put("/inventory/0")
        assert response.status_code == 403
        assert response.headers["X-Coins"] == str(cvm.accepted_coins)

def test_inventory_id_put_oos(test_client, cvm):
    # buy drink 0 until out stock
    for i in range(0, cvm.inventory[0]):
        for j in range(0, cvm.DRINK_PRICE):
            test_client.put("/", json={"coin": 1})
        test_client.put("/inventory/0")

    # put in enough coins to attempt to buy another
    for i in range(0, cvm.DRINK_PRICE):
        cvm.accept_coin()
        test_client.put("/", json={"coin": 1})
    
    # try to buy it
    response = test_client.put("/inventory/0")
    assert response.status_code == 404
    assert response.headers["X-Coins"] == str(cvm.accepted_coins)
