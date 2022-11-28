class Courier:
    order = []
    x:int
    y:int
    maxWeight:int
    def _init_(self, x, y, weight) -> None:
        self.x = x
        self.y = y
        self.maxWeight = weight