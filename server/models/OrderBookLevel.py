class OrderBookLevel:
    def __init__(self, price, quantity):
        self.price = price
        self.quantity = quantity
    def __str__(self):
        return f"Price ${self.price}, {self.quantity} units"
        
    