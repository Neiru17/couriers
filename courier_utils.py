from __future__ import annotations
from math import sqrt


def print_dict(dict: dict) -> None:
    print("{")
    for key, value in dict.items():
        print(f'  {key}:\t{value}')
    print("}")


class PickupState:
    CAN: int = 1
    NO_CAN: int = 2
    ANOTHER_COURIER: int = 3


class Vec2D:
    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.__x: float = float(x)
        self.__y: float = float(y)

    @property
    def x(self) -> float:
        return self.__x

    @x.setter
    def x(self, value) -> None:
        try:
            self.__x = float(value)
        except ValueError:
            raise ValueError('"x" must be a number') from None

    @property
    def y(self) -> float:
        return self.__y

    @y.setter
    def y(self, value) -> None:
        try:
            self.__y = float(value)
        except ValueError:
            raise ValueError('"y" must be a number') from None

    def distance_squared(self, vec: Vec2D) -> float:
        """Возвращает расстояние между точек без корня (для более легкой сортировки)"""
        return (self.x-vec.x)**2+(self.y-vec.y)**2

    def distance(self, vec: Vec2D) -> float:
        """Возвращает расстояние между точек"""
        return sqrt(self.distance_squared(vec))

    def __repr__(self) -> str:
        return f'Vec2D({self.__x}, {self.__y})'

    def __str__(self) -> str:
        return f'({self.__x}, {self.__y})'


class Order:
    __GLOBAL_ID: int = 0

    def __init__(self, position: Vec2D, weight) -> None:
        self.__position: Vec2D = position
        self.__weight: int = weight
        self.__order_for_courier: Courier | None = None
        self.__id: int = self.__GLOBAL_ID
        self.__class__.__GLOBAL_ID += 1

    @property
    def weight(self) -> int:
        return self.__weight

    @property
    def id(self) -> int:
        return self.__id

    @property
    def position(self) -> Vec2D:
        return self.__position

    @position.setter
    def position(self, value: Vec2D) -> None:
        if (type(value) != Vec2D):
            raise ValueError('"position" must be of type "Vec2D"') from None
        self.__position = value

    @property
    def order_for_courier(self) -> Courier | None:
        return self.__order_for_courier

    @order_for_courier.setter
    def order_for_courier(self, value) -> None:
        if (not isinstance(value, Courier | None)):
            raise ValueError(
                '"order_for_courier" must be of type "Courier"') from None
        self.__order_for_courier = value

    def __repr__(self) -> str:
        return f'Order({self.__position}, {self.__weight})'


class Courier:
    __GLOBAL_ID: int = 0

    def __init__(self, position: Vec2D = Vec2D(), unload: Vec2D = Vec2D(), max_weight: int = -1, max_count: int = -1, move_in_second=50) -> None:
        self.__position: Vec2D = position
        self.__max_weight: int = max_weight
        self.__max_count: int = max_count
        self.__point_unload: Vec2D = unload

        self.__weight: int = 0
        self.__speed: int = move_in_second
        self.__orders: list[Order] = []
        self.__id: int = self.__GLOBAL_ID
        self.__class__.__GLOBAL_ID += 1

    @property
    def max_weight(self) -> int:
        return self.__max_weight

    @max_weight.setter
    def max_weight(self, value) -> None:
        try:
            self.__max_weight = int(value)
        except ValueError:
            raise ValueError('"weight" must be a number') from None

    @property
    def id(self) -> int:
        return self.__id

    @property
    def orders(self) -> list[Order]:
        return self.__orders

    @property
    def position(self) -> Vec2D:
        return self.__position

    @position.setter
    def position(self, value: Vec2D) -> None:
        if (type(value) != Vec2D):
            raise ValueError('"position" must be of type "Vec2D"') from None
        self.__position = value

    def move(self, millis: int) -> Order | None:
        if (len(self.__orders) <= 0):
            if (self.__weight == 0):
                return None
            time: float = self.get_time(self.__point_unload)
            if (time <= 0):
                self.__position.x = self.__point_unload.x
                self.__position.y = self.__point_unload.y
                self.clear_orders()
                return None
            multiply: float = (millis/1000)/time
            if (multiply >= 1):
                self.__position.x = self.__point_unload.x
                self.__position.y = self.__point_unload.y
                self.clear_orders()
                return None
            self.__position.x += (self.__point_unload.x-self.__position.x)*multiply
            self.__position.y += (self.__point_unload.y-self.__position.y)*multiply
            return None

        order: Order = self.__orders[0]
        order_pos: Vec2D = order.position
        time = self.get_time(order_pos)
        if (time <= 0):
            self.__position.x = order_pos.x
            self.__position.y = order_pos.y
            return self.__orders.pop(0)
        multiply = (millis/1000)/time
        if (multiply >= 1):
            self.__position.x = order_pos.x
            self.__position.y = order_pos.y
            return self.__orders.pop(0)
        self.__position.x += (order_pos.x-self.__position.x)*multiply
        self.__position.y += (order_pos.y-self.__position.y)*multiply
        return None

    def get_time(self, vec: Vec2D) -> float:
        """Возвращает время в секундах"""
        return self.__position.distance(vec)/self.__speed

    def take_orders(self, orders: list[Order]) -> None:
        sorted_orders: list[Order] = sorted(
            orders,
            key=lambda item: self.position.distance_squared(item.position)
        )
        for order in sorted_orders:
            state: int = self.can_take_order(order)
            if (state == PickupState.CAN):
                self.add_order(order)
            elif (state == PickupState.ANOTHER_COURIER):
                if (type(order.order_for_courier) == Courier and order.order_for_courier.id != self.__id):
                    other_courier: Courier = order.order_for_courier
                    other_courier.remove_order(order)
                    self.add_order(order)
                    other_courier.take_orders(orders)
                else:
                    self.add_order(order)

    def can_take_order(self, order: Order) -> int:
        if (self.__max_count != -1 and self.__max_count <= len(self.__orders)):
            return PickupState.NO_CAN
        if (self.__max_weight != -1 and (self.__max_weight-self.__weight) < order.weight):
            return PickupState.NO_CAN

        if (type(order.order_for_courier) == Courier):
            if (order.order_for_courier.id == self.__id):
                return PickupState.NO_CAN

            other_courier: Courier = order.order_for_courier
            self_path_cost: float = self.__position.distance_squared(
                order.position)
            other_path_cost: float = other_courier.position.distance_squared(
                order.position)

            if (self_path_cost >= other_path_cost):
                return PickupState.NO_CAN
            return PickupState.ANOTHER_COURIER
        return PickupState.CAN

    def add_order(self, order: Order) -> None:
        if (not isinstance(order, Order)):
            raise ValueError('"order" myst be of type "Order"') from None
        if (order not in self.__orders):
            self.__orders.append(order)
            self.__weight += order.weight
        order.order_for_courier = self

    def remove_order(self, order: Order) -> None:
        order.order_for_courier = None
        try:
            self.__orders.remove(order)
            self.__weight -= order.weight
        except ValueError:
            pass

    def clear_orders(self) -> None:
        for order in self.__orders:
            if (type(order.order_for_courier) == Courier and order.order_for_courier.id == self.__id):
                order.order_for_courier = None
        self.__weight = 0
        self.__orders.clear()

    def __repr__(self) -> str:
        return f'Courier(id={self.__id}, position={self.__position}, weight={self.__weight}, max_weight={self.__max_weight}, orders={self.__orders})'
