from flask import Flask
from flask import request
from flask import Response


class VendingMachine:
    
    MAX_STOCKED = 5         # This cannot every be less than 0
    NUMBER_OF_DRINKS = 3    # This cannot ever be leq 0
    DRINK_PRICE = 2         # This cannot ever be less than 0

    def __init__(self) -> None:
        self.accepted_coins = 0
        self.inventory = [self.MAX_STOCKED] * self.NUMBER_OF_DRINKS
        self.dispensed_drinks = 0
    
    def accept_coin(self):
        self.accepted_coins += 1

    def return_coins(self):
        returned_coins = self.accepted_coins
        self.accepted_coins = 0
        return returned_coins

    def dispense_drink(self, selected_drink):
        if self.accepted_coins < self.DRINK_PRICE:
            raise ValueError("Not enough coins")
        elif self.inventory[selected_drink] <= 0:
            raise ValueError("Selected drink is out of stock")

        self.inventory[selected_drink] -= 1
        self.dispensed_drinks += 1
        self.accepted_coins -= self.DRINK_PRICE
        return self.return_coins()


def create_vendomatic():
    vendomatic = Flask("vendomatic")
    vm = VendingMachine()

    @vendomatic.route("/", methods=["PUT", "DELETE"])
    def home():
        if request.method == "PUT" and request.json["coin"] == 1:
            vm.accept_coin()
            return "", 204, {"X-Coins": vm.accepted_coins}
        elif request.method == "DELETE":
            returned_coins = vm.return_coins()
            return "", 204, {"X-Coins": returned_coins}
        else:
            return "", 404


    @vendomatic.route("/inventory", methods=["GET"])
    def inventory():
        return vm.inventory, 200

    @vendomatic.route("/inventory/<int:id>", methods=["GET", "PUT"])
    def inventory_id():
        return "", 999

    return vendomatic
