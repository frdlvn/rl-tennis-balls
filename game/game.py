import random
import sys

import pygame as pg
from pygame.locals import *

FPS = 15
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
CELL_SIZE = 20
assert WINDOW_WIDTH % CELL_SIZE == 0, "Window width must be a multiple of cell size."
assert WINDOW_HEIGHT % CELL_SIZE == 0, "Window height must be a multiple of cell size."
CELL_WIDTH = int(WINDOW_WIDTH / CELL_SIZE)
CELL_HEIGHT = int(WINDOW_HEIGHT / CELL_SIZE)

#         R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 155, 0)
DARK_GRAY = (40, 40, 40)
BG_COLOR = BLACK

UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"

HEAD = 0  # syntactic sugar: index of the worm's head
FPS_CLOCK: pg.time.Clock
DISPLAY_SURF: pg.Surface
BASIC_FONT: pg.font.Font


def main() -> None:
    global FPS_CLOCK, DISPLAY_SURF, BASIC_FONT

    pg.init()
    FPS_CLOCK = pg.time.Clock()
    DISPLAY_SURF = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    BASIC_FONT = pg.font.Font("freesansbold.ttf", 18)
    pg.display.set_caption("Wormy")

    show_start_screen()
    while True:
        run_game()
        show_game_over_screen()


def run_game():
    # Set a random start point.
    start_x = random.randint(5, CELL_WIDTH - 6)
    start_y = random.randint(5, CELL_HEIGHT - 6)
    worm_coords = [
        {"x": start_x, "y": start_y},
        {"x": start_x - 1, "y": start_y},
        {"x": start_x - 2, "y": start_y},
    ]
    direction = RIGHT

    # Start the apple in a random place.
    apple = get_random_location()

    while True:  # main game loop
        for event in pg.event.get():  # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # check if the worm has hit itself or the edge
        if (
            worm_coords[HEAD]["x"] == -1
            or worm_coords[HEAD]["x"] == CELL_WIDTH
            or worm_coords[HEAD]["y"] == -1
            or worm_coords[HEAD]["y"] == CELL_HEIGHT
        ):
            return  # game over
        for wormBody in worm_coords[1:]:
            if (
                wormBody["x"] == worm_coords[HEAD]["x"]
                and wormBody["y"] == worm_coords[HEAD]["y"]
            ):
                return  # game over

        # check if worm has eaten an apple
        if (
            worm_coords[HEAD]["x"] == apple["x"]
            and worm_coords[HEAD]["y"] == apple["y"]
        ):
            # don't remove worm's tail segment
            apple = get_random_location()  # set a new apple somewhere
        else:
            del worm_coords[-1]  # remove worm's tail segment

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            new_head = {"x": worm_coords[HEAD]["x"], "y": worm_coords[HEAD]["y"] - 1}
        elif direction == DOWN:
            new_head = {"x": worm_coords[HEAD]["x"], "y": worm_coords[HEAD]["y"] + 1}
        elif direction == LEFT:
            new_head = {"x": worm_coords[HEAD]["x"] - 1, "y": worm_coords[HEAD]["y"]}
        elif direction == RIGHT:
            new_head = {"x": worm_coords[HEAD]["x"] + 1, "y": worm_coords[HEAD]["y"]}
        worm_coords.insert(0, new_head)
        DISPLAY_SURF.fill(BG_COLOR)
        draw_grid()
        draw_worm(worm_coords)
        draw_apple(apple)
        draw_score(len(worm_coords) - 3)
        pg.display.update()
        FPS_CLOCK.tick(FPS)


def draw_press_key_msg():
    press_key_surf = BASIC_FONT.render("Press a key to play.", True, DARK_GRAY)
    press_key_rect = press_key_surf.get_rect()
    press_key_rect.topleft = (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 30)
    DISPLAY_SURF.blit(press_key_surf, press_key_rect)


def check_for_key_press():
    if len(pg.event.get(QUIT)) > 0:
        terminate()

    key_up_events = pg.event.get(KEYUP)
    if len(key_up_events) == 0:
        return None
    if key_up_events[0].key == K_ESCAPE:
        terminate()
    return key_up_events[0].key


def show_start_screen():
    title_font = pg.font.Font("freesansbold.ttf", 100)
    title_surf1 = title_font.render("Wormy!", True, WHITE, DARK_GREEN)
    title_surf2 = title_font.render("Wormy!", True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAY_SURF.fill(BG_COLOR)
        rotated_surf1 = pg.transform.rotate(title_surf1, degrees1)
        rotated_rect1 = rotated_surf1.get_rect()
        rotated_rect1.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        DISPLAY_SURF.blit(rotated_surf1, rotated_rect1)

        rotated_surf2 = pg.transform.rotate(title_surf2, degrees2)
        rotated_rect2 = rotated_surf2.get_rect()
        rotated_rect2.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        DISPLAY_SURF.blit(rotated_surf2, rotated_rect2)

        draw_press_key_msg()

        if check_for_key_press():
            pg.event.get()  # clear event queue
            return
        pg.display.update()
        FPS_CLOCK.tick(FPS)
        degrees1 += 3  # rotate by 3 degrees each frame
        degrees2 += 7  # rotate by 7 degrees each frame


def terminate():
    pg.quit()
    sys.exit()


def get_random_location():
    return {
        "x": random.randint(0, CELL_WIDTH - 1),
        "y": random.randint(0, CELL_HEIGHT - 1),
    }


def show_game_over_screen():
    game_over_font = pg.font.Font("freesansbold.ttf", 150)
    game_surf = game_over_font.render("Game", True, WHITE)
    over_surf = game_over_font.render("Over", True, WHITE)
    game_rect = game_surf.get_rect()
    over_rect = over_surf.get_rect()
    game_rect.midtop = (WINDOW_WIDTH / 2, 10)
    over_rect.midtop = (WINDOW_WIDTH / 2, game_rect.height + 10 + 25)

    DISPLAY_SURF.blit(game_surf, game_rect)
    DISPLAY_SURF.blit(over_surf, over_rect)
    draw_press_key_msg()
    pg.display.update()
    pg.time.wait(500)
    check_for_key_press()  # clear out any key presses in the event queue

    while True:
        if check_for_key_press():
            pg.event.get()  # clear event queue
            return


def draw_score(score):
    score_surf = BASIC_FONT.render("Score: %s" % score, True, WHITE)
    score_rect = score_surf.get_rect()
    score_rect.topleft = (WINDOW_WIDTH - 120, 10)
    DISPLAY_SURF.blit(score_surf, score_rect)


def draw_worm(worm_coords):
    for coord in worm_coords:
        x = coord["x"] * CELL_SIZE
        y = coord["y"] * CELL_SIZE
        worm_segment_rect = pg.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pg.draw.rect(DISPLAY_SURF, DARK_GREEN, worm_segment_rect)
        worm_inner_segment_rect = pg.Rect(x + 4, y + 4, CELL_SIZE - 8, CELL_SIZE - 8)
        pg.draw.rect(DISPLAY_SURF, GREEN, worm_inner_segment_rect)


def draw_apple(coord):
    x = coord["x"] * CELL_SIZE
    y = coord["y"] * CELL_SIZE
    apple_rect = pg.Rect(x, y, CELL_SIZE, CELL_SIZE)
    pg.draw.rect(DISPLAY_SURF, RED, apple_rect)


def draw_grid():
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):  # draw vertical lines
        pg.draw.line(DISPLAY_SURF, DARK_GRAY, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):  # draw horizontal lines
        pg.draw.line(DISPLAY_SURF, DARK_GRAY, (0, y), (WINDOW_WIDTH, y))


if __name__ == "__main__":
    main()
