from __future__ import annotations
from courier_utils import Vec2D, Order, Courier
from courier_utils import print_dict

import pygame
import random
import math
import time
# Комментарий по программе
#
# Вес берется по граммам
#

# Переменные для pygame

WIDTH: int = 400  # ширина игрового окна
HEIGHT: int = 400  # высота игрового окна
SAFE_ZONE: float = 0.1  # безопасная зона приложения
USEFUL_WIDTH: int = int(WIDTH * (1-SAFE_ZONE))  # 360
USEFUL_HEIGHT: int = int(HEIGHT * (1-SAFE_ZONE))
FPS: int = 30  # частота кадров в секунду

orders: list[Order] = []
couriers: list[Courier] = []
MAX_FIELD_SIZE: tuple[int, int] = (200, 200)
COURIERS_COUNT: int = 5
ORDERS_COUNT: int = 100


def create_courier(
    x: int | None = None,
    y: int | None = None,
    max_weight: int | None = None
) -> None:
    if x is None:
        x = random.randint(MAX_FIELD_SIZE[0]//-2, MAX_FIELD_SIZE[0]//2)
    if y is None:
        y = random.randint(MAX_FIELD_SIZE[0]//-2, MAX_FIELD_SIZE[0]//2)
    if max_weight is None:
        max_weight = random.randint(100, 3000)

    position: Vec2D = Vec2D(x, y)
    couriers.append(Courier(position, max_weight=max_weight))


def create_order(
    x: int | None = None,
    y: int | None = None,
    weight: int | None = None
) -> None:
    if x is None:
        x = random.randint(MAX_FIELD_SIZE[0]//-2, MAX_FIELD_SIZE[0]//2)
    if y is None:
        y = random.randint(MAX_FIELD_SIZE[0]//-2, MAX_FIELD_SIZE[0]//2)
    if weight is None:
        weight = random.randint(100, 3000)

    position: Vec2D = Vec2D(x, y)
    orders.append(Order(position, weight))



def recalc_vec(position: float) -> int:
    return int((WIDTH//2)+(USEFUL_WIDTH/MAX_FIELD_SIZE[0])*position)


if __name__ == '__main__':
    for _ in range(COURIERS_COUNT):
        create_courier(max_weight=10000)
    for _ in range(ORDERS_COUNT):
        create_order()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Курьеры ебать")
    running: bool = True
    clock = pygame.time.Clock()
    while running:
        millis: int = clock.tick(FPS)
        screen.fill((255, 255, 255))
        for order in orders:
            pygame.draw.circle(screen, (10, 10, 10), (recalc_vec(
                order.position.x), recalc_vec(order.position.y)), 3)

        for courier in couriers:
            courier.take_orders(orders)

        for courier in couriers:
            status: Order | None = courier.move(millis)
            if (isinstance(status, Order)):
                orders.remove(status)  #Костыль, нужно переделать

            prev_pos: list[float] = [courier.position.x, courier.position.y]
            pygame.draw.rect(screen, (200, 10, 10), (recalc_vec(
                prev_pos[0])-5, recalc_vec(prev_pos[1])-5, 10, 10))
            for order in courier.orders:
                pygame.draw.line(screen, (150, 0, 0), (recalc_vec(prev_pos[0]), recalc_vec(
                    prev_pos[1])), (recalc_vec(order.position.x), recalc_vec(order.position.y)), 2)
                prev_pos = [order.position.x, order.position.y]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    running = False
                if event.key == pygame.K_r:
                    first_time: float = time.time()*1000
                    for order in orders:
                        if (isinstance(order.order_for_courier, Courier)):
                            order.order_for_courier.remove_order(order)
                    second_time: float = time.time()*1000
                    orders.clear()
                    for _ in range(ORDERS_COUNT):
                        create_order()
                    print(second_time-first_time, time.time()*1000-second_time)
        pygame.display.flip()

    print(orders, sep='\n')
    print("\n\n")
    print(couriers, sep='\n')
