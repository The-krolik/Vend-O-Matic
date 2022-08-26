from flask import Flask
from flask import jsonify
from flask import request


class VendingMachine:
    
    MAX_STOCKED = 5         # This cannot every be less than 0
    NUMBER_OF_DRINKS = 3    # This cannot ever be leq 0
    DRINK_PRICE = 2         # This cannot ever be less than 0

    def __init__(self) -> None:
        self._accepted_coins = 0
        self._inventory = [self.MAX_STOCKED] * self.NUMBER_OF_DRINKS
    
    @property
    def accepted_coins(self):
        return self._accepted_coins

    @accepted_coins.setter
    def accepted_coins(self, val):
        raise AttributeError("Cannot manually set number of accepted coins")

    @property
    def inventory(self):
        return self._inventory

    @inventory.setter
    def inventory(self, val):
        raise AttributeError("Cannot manually set inventory values")

    def accept_coin(self):
        self._accepted_coins += 1

    def dispense_coins(self):
        dispensed_coins = self._accepted_coins
        self._accepted_coins = 0
        return dispensed_coins

    def dispense_drink(self, selected_drink):
        if self._accepted_coins < self.DRINK_PRICE:
            raise ValueError("Not enough coins")
        elif self._inventory[selected_drink] <= 0:
            raise ValueError("Selected drink is out of stock")

        self._inventory[selected_drink] -= 1
        self._accepted_coins -= self.DRINK_PRICE
        return self.dispense_coins()


def create_app():
    app = Flask("vendomatic")
    #vm = VendingMachine()

    @app.route("/", methods=["PUT", "DELETE"])
    def home():
        if request.method == "PUT":
            return "", 204, {"Content-Type": "application/json"}
        elif request.method == "DELETE":
            return "", 204, {"Content-Type": "application/json"}


    @app.get("/inventory")
    def get_inventory():
        response = flask.Response("inventory response")
        response.status_code = 200
        return response

    return app
