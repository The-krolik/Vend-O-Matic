from flask import Flask
from flask import jsonify
from flask import request


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
        dispensed_coins = self.accepted_coins
        self.accepted_coins = 0
        return dispensed_coins

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
        if request.method == "PUT":
            return "", 204, {"X-Coins": 1}
        elif request.method == "DELETE":
            return "", 204, {"Content-Type": "application/json"}


    @vendomatic.get("/inventory")
    def get_inventory():
        response = flask.Response("inventory response")
        response.status_code = 200
        return response

    return vendomatic
