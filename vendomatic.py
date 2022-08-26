from flask import Flask
from flask import request
from flask import Response
import json


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
            return -1
        elif self.inventory[selected_drink] <= 0:
            return -2

        self.inventory[selected_drink] -= 1
        self.dispensed_drinks += 1
        self.accepted_coins -= self.DRINK_PRICE
        return self.return_coins()


def create_app():
    app = Flask("vendomatic")
    vm = VendingMachine()

    @app.route("/", methods=["PUT", "DELETE"])
    def home():
        if request.method == "PUT" and "coin" in request.json:
            if request.json["coin"] == 1:
                vm.accept_coin()
                return "", 204, {"X-Coins": vm.accepted_coins}
        elif request.method == "DELETE":
            returned_coins = vm.return_coins()
            return "", 204, {"X-Coins": returned_coins}
        else:
            return "", 404


    @app.route("/inventory", methods=["GET"])
    def inventory():
        return json.dumps(vm.inventory), 200, {"Content-Type": "application/json"}

    @app.route("/inventory/<int:index>", methods=["GET", "PUT"])
    def inventory_id(index):
        if request.method == "GET":
            return str(vm.inventory[index]), 200
        elif request.method == "PUT":
            returned_coins = vm.dispense_drink(index)    
            if returned_coins >= 0:
                return {"quantity": vm.dispensed_drinks}, 200, {"X-Coins": returned_coins, "X-Inventory-Remaining": vm.inventory[index]}
            elif returned_coins == -1:
                return "", 403, {"X-Coins": vm.accepted_coins}
            elif returned_coins == -2:
                return "", 404, {"X-Coins": vm.accepted_coins}
        else:
            return "", 404

    return app
