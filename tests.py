import pytest
import vendomatic as vom


@pytest.fixture
def app():
    app = vom.create_app()
    yield app

@pytest.fixture
def vm():
    vm = vom.VendingMachine()
    yield vm

def test_machine_init(vm):
    assert vm._accepted_coins == 0
    assert len(vm._inventory) == vm.NUMBER_OF_DRINKS
    for i in range(0, len(vm._inventory)):
        assert vm._inventory[i] == vm.MAX_STOCKED

def test_setters(vm):
    new_inventory = [3] * 2
    with pytest.raises(AttributeError) as e_info:
        vm.accepted_coins = 0
    with pytest.raises(AttributeError) as e_info:
        vm.inventory = new_inventory
    with pytest.raises(AttributeError) as e_info:
        vm.inventory[0] = vm.MAX_STOCKED + 1

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
    

def test_request_example(app):
    response = app.test_client().get("/")
    assert response.text == "Hello World!"
    assert response.status_code == 300
