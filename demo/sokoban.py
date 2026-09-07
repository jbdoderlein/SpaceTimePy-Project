from dataclasses import dataclass, field

import pygame
from spacetimepy_pygame import GameState, game_loop, get_events, launch_game_loop

pygame.init()

TILE_SIZE = 64
LEVEL_WIDTH = 9
LEVEL_HEIGHT = 7
HUD_HEIGHT = 100
SCREEN_WIDTH = LEVEL_WIDTH * TILE_SIZE
SCREEN_HEIGHT = LEVEL_HEIGHT * TILE_SIZE + HUD_HEIGHT
FRAME_RATE = 60

BACKGROUND = (32, 37, 47)
FLOOR_LIGHT = (221, 213, 194)
FLOOR_DARK = (207, 197, 177)
WALL = (74, 86, 105)
WALL_EDGE = (45, 53, 67)
BOX = (174, 111, 57)
BOX_EDGE = (105, 63, 34)
BOX_ON_GOAL = (80, 150, 92)
GOAL = (210, 76, 76)
PLAYER = (58, 111, 205)
WHITE = (245, 245, 245)
BLACK = (27, 27, 30)

LEVEL = (
    "#########",
    "#       #",
    "# . . . #",
    "# $ $ $ #",
    "#   #   #",
    "#   @   #",
    "#########",
)

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SpaceTimePy Sokoban")
FONT = pygame.font.SysFont("Arial", 28)
SMALL_FONT = pygame.font.SysFont("Arial", 20)
clock = pygame.time.Clock()


def find_tiles(symbol: str) -> frozenset[tuple[int, int]]:
    """Find all level tiles that contain one symbol."""
    return frozenset(
        (x, y)
        for y, row in enumerate(LEVEL)
        for x, tile in enumerate(row)
        if tile == symbol
    )


WALLS = find_tiles("#")
GOALS = find_tiles(".")
INITIAL_BOXES = tuple(sorted(find_tiles("$")))
INITIAL_PLAYER = next(iter(find_tiles("@")))


@dataclass
class SokobanState(GameState):
    player: tuple[int, int] = INITIAL_PLAYER
    boxes: list[tuple[int, int]] = field(default_factory=lambda: list(INITIAL_BOXES))
    moves: int = 0
    pushes: int = 0
    game_won: bool = False


state = SokobanState()


def reset_game(state: SokobanState) -> None:
    """Reset the level and all counters."""
    state.player = INITIAL_PLAYER
    state.boxes = list(INITIAL_BOXES)
    state.moves = 0
    state.pushes = 0
    state.game_won = False


def move_player(state: SokobanState, direction: tuple[int, int]) -> None:
    """Move the player one tile if the path is clear."""
    target = (state.player[0] + direction[0], state.player[1] + direction[1])
    if target in WALLS:
        return

    if target in state.boxes:
        box_target = (target[0] + direction[0], target[1] + direction[1])
        if box_target in WALLS or box_target in state.boxes:
            return
        box_index = state.boxes.index(target)
        state.boxes[box_index] = box_target
        state.pushes += 1

    state.player = target
    state.moves += 1
    state.game_won = all(box in GOALS for box in state.boxes)


def tile_rect(position: tuple[int, int]) -> pygame.Rect:
    """Create the screen rectangle for one tile."""
    return pygame.Rect(
        position[0] * TILE_SIZE,
        position[1] * TILE_SIZE,
        TILE_SIZE,
        TILE_SIZE,
    )


def draw_level(state: SokobanState) -> None:
    """Draw the floor, walls, goals, boxes, and player."""
    for y in range(LEVEL_HEIGHT):
        for x in range(LEVEL_WIDTH):
            rect = tile_rect((x, y))
            floor_color = FLOOR_LIGHT if (x + y) % 2 == 0 else FLOOR_DARK
            pygame.draw.rect(SCREEN, floor_color, rect)

    for wall in WALLS:
        rect = tile_rect(wall)
        pygame.draw.rect(SCREEN, WALL, rect.inflate(-4, -4), border_radius=7)
        pygame.draw.rect(SCREEN, WALL_EDGE, rect.inflate(-4, -4), 3, border_radius=7)

    for goal in GOALS:
        pygame.draw.circle(SCREEN, GOAL, tile_rect(goal).center, 13)
        pygame.draw.circle(SCREEN, WHITE, tile_rect(goal).center, 7)

    for box in state.boxes:
        rect = tile_rect(box).inflate(-14, -14)
        color = BOX_ON_GOAL if box in GOALS else BOX
        pygame.draw.rect(SCREEN, color, rect, border_radius=5)
        pygame.draw.rect(SCREEN, BOX_EDGE, rect, 4, border_radius=5)
        pygame.draw.line(SCREEN, BOX_EDGE, rect.topleft, rect.bottomright, 3)
        pygame.draw.line(SCREEN, BOX_EDGE, rect.topright, rect.bottomleft, 3)

    player_center = tile_rect(state.player).center
    pygame.draw.circle(SCREEN, PLAYER, player_center, 23)
    pygame.draw.circle(SCREEN, BLACK, player_center, 23, 3)
    pygame.draw.circle(SCREEN, WHITE, (player_center[0] - 8, player_center[1] - 6), 5)
    pygame.draw.circle(SCREEN, WHITE, (player_center[0] + 8, player_center[1] - 6), 5)
    pygame.draw.circle(SCREEN, BLACK, (player_center[0] - 8, player_center[1] - 6), 2)
    pygame.draw.circle(SCREEN, BLACK, (player_center[0] + 8, player_center[1] - 6), 2)


def draw_hud(state: SokobanState) -> None:
    """Draw counters and game instructions."""
    hud_top = LEVEL_HEIGHT * TILE_SIZE
    pygame.draw.rect(SCREEN, BACKGROUND, (0, hud_top, SCREEN_WIDTH, HUD_HEIGHT))

    counters = FONT.render(
        f"Moves: {state.moves}    Pushes: {state.pushes}", True, WHITE
    )
    SCREEN.blit(counters, (18, hud_top + 12))

    instructions = SMALL_FONT.render(
        "Move: arrows or WASD    Reset: R    Exit: Esc",
        True,
        WHITE,
    )
    SCREEN.blit(instructions, (18, hud_top + 56))


def draw_game(state: SokobanState) -> None:
    """Draw one game frame."""
    SCREEN.fill(BACKGROUND)
    draw_level(state)
    draw_hud(state)

    if state.game_won:
        message = FONT.render("Level complete! Press R to restart.", True, BLACK)
        message_rect = message.get_rect(
            center=(SCREEN_WIDTH // 2, LEVEL_HEIGHT * TILE_SIZE // 2)
        )
        pygame.draw.rect(
            SCREEN,
            WHITE,
            message_rect.inflate(28, 22),
            border_radius=8,
        )
        SCREEN.blit(message, message_rect)


KEY_DIRECTIONS = {
    pygame.K_LEFT: (-1, 0),
    pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_d: (1, 0),
    pygame.K_UP: (0, -1),
    pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_s: (0, 1),
}


@game_loop(ignored_names=("SMALL_FONT",))
def display_game(state: SokobanState) -> bool:
    """Process input and draw one recorded game frame."""
    for event in get_events():
        if event.type == pygame.QUIT:
            return False
        if event.type != pygame.KEYDOWN:
            continue
        if event.key == pygame.K_ESCAPE:
            return False
        if event.key == pygame.K_r:
            reset_game(state)
        elif event.key in KEY_DIRECTIONS and not state.game_won:
            move_player(state, KEY_DIRECTIONS[event.key])

    draw_game(state)
    pygame.display.flip()
    clock.tick(FRAME_RATE)
    return True


if __name__ == "__main__":
    launch_game_loop(
        display_game,
        state,
        db_path="sokoban.db",
        session_name="Small Sokoban",
    )
    pygame.quit()
