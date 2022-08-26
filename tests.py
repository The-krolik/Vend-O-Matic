import pytest
import vendomatic as vom


@pytest.fixture
def app():
    app = vom.create_app()
    yield app

@pytest.fixture
def test_client(app):
    yield app.test_client()

def test_machine_init():
    vm = vom.VendingMachine()
    assert vm._accepted_coins == 0
    assert len(vm._inventory) == vm.NUMBER_OF_DRINKS
    for i in range(0, len(vm._inventory)):
        assert vm._inventory[i] == vm.MAX_STOCKED

def test_setters():
    vm = vom.VendingMachine()
    new_inventory = [3] * 2
    with pytest.raises(AttributeError) as e_info:
        vm.accepted_coins = 0
    with pytest.raises(AttributeError) as e_info:
        vm.inventory = new_inventory
    # broken test, need to fix in api
    with pytest.raises(AttributeError) as e_info:
        vm.inventory[0] = vm.MAX_STOCKED + 1

def test_accept_coin():
    vm = vom.VendingMachine()
    coins_before_insert = vm.accepted_coins
    vm.accept_coin()
    assert vm.accepted_coins == coins_before_insert + 1

def test_dispense_coins():
    vm = vom.VendingMachine()
    vm.accept_coin()
    total_coins = vm.accepted_coins
    dispensed_coins = vm.dispense_coins()
    assert dispensed_coins == total_coins

def test_dispense_drink():
    vm = vom.VendingMachine()
    vm._accepted_coins = vm.DRINK_PRICE - 1
    with pytest.raises(ValueError) as e_info:
        vm.dispense_drink(0)

    vm._accepted_coins = vm.DRINK_PRICE + 1
    dispensed_coins = vm.dispense_drink(0)
    assert vm.inventory[0] == vm.MAX_STOCKED - 1
    assert dispensed_coins == 1

    # test for out of stock
    vm._inventory[0] = 0
    vm._accepted_coins = vm.DRINK_PRICE
    with pytest.raises(ValueError) as e_info:
        vm.dispense_drink(0)
    

def test_home_put(test_client):
    response = test_client.put("/", headers={
        "coin": 1
    })
    assert response.status_code == 204
    assert response.headers["Content-Type"] == "application/json"
    assert response.headers["X-Coins"] == 1

def test_home_delete(test_client):
    response = test_client.delete("/")
    assert response.status_code == 204
    assert response.headers["Content-Type"] == "application/json"
    assert response.headers["X-Coins"] == 1

def test_inventory_get(test_client):
    response = test_client.get("/inventory")
    assert response.status_code == 200
