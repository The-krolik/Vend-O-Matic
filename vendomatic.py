from flask import Flask
from flask import request
from flask import Response


class VendingMachine:

    MAX_STOCKED = 5  # This cannot every be less than 0
    NUMBER_OF_DRINKS = 3  # This cannot ever be leq 0
    DRINK_PRICE = 2  # This cannot ever be less than 0

    def __init__(self) -> None:
        self.accepted_coins = 0
        self.inventory = [self.MAX_STOCKED] * self.NUMBER_OF_DRINKS

    def accept_coin(self) -> int:
        self.accepted_coins += 1

    def return_coins(self) -> int:
        returned_coins = self.accepted_coins
        self.accepted_coins = 0
        return returned_coins

    def dispense_drink(self, selected_drink) -> int:
        if self.accepted_coins < self.DRINK_PRICE:
            return -1
        elif self.inventory[selected_drink] <= 0:
            return -2

        self.inventory[selected_drink] -= 1
        self.accepted_coins -= self.DRINK_PRICE
        return self.return_coins()


def create_app():
    app = Flask(__name__)
    vm = VendingMachine()

    @app.route("/", methods=["PUT", "DELETE"])
    def home():
        if request.method == "PUT":
            if "coin" in request.json and request.json["coin"] == 1:
                vm.accept_coin()
                return "", 204, {"X-Coins": vm.accepted_coins}
        elif request.method == "DELETE":
            returned_coins = vm.return_coins()
            return "", 204, {"X-Coins": returned_coins}

        return "", 400

    @app.route("/inventory", methods=["GET"])
    def inventory():
        return vm.inventory, 200, {"Content-Type": "application/json"}

    @app.route("/inventory/<int:index>", methods=["GET", "PUT"])
    def inventory_id(index):
        if request.method == "GET":
            return str(vm.inventory[index]), 200, {"Content-Type": "application/json"}
        elif request.method == "PUT":
            returned_coins = vm.dispense_drink(index)
            if returned_coins >= 0:
                return (
                    {"quantity": 1},
                    200,
                    {
                        "X-Coins": returned_coins,
                        "X-Inventory-Remaining": vm.inventory[index],
                        "Content-Type": "application/json",
                    },
                )
            elif returned_coins == -1:
                return "", 403, {"X-Coins": vm.accepted_coins}
            elif returned_coins == -2:
                return "", 404, {"X-Coins": vm.accepted_coins}

        return "", 400

    return app
