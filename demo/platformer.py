from dataclasses import dataclass, field

import pygame
from spacetimepy_pygame import (
    GameState,
    game_loop,
    get_events,
    get_pressed_keys,
    launch_game_loop,
)

pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FRAME_RATE = 60
PLAYER_SPEED = 6
JUMP_VELOCITY = -15
GRAVITY = 1.2
MAX_FALL_SPEED = 16

SKY = (135, 206, 235)
WHITE = (250, 250, 250)
BLACK = (25, 25, 30)
BROWN = (125, 76, 45)
GREEN = (73, 160, 75)
BLUE = (55, 100, 210)
YELLOW = (255, 210, 40)
RED = (210, 55, 55)

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SpaceTimePy Platformer")
FONT = pygame.font.SysFont("Arial", 28)
SMALL_FONT = pygame.font.SysFont("Arial", 20)
clock = pygame.time.Clock()

PLATFORMS = (
    pygame.Rect(0, 560, 900, 40),
    pygame.Rect(150, 480, 170, 22),
    #pygame.Rect(380, 400, 170, 22),
    pygame.Rect(620, 320, 170, 22),
    #pygame.Rect(400, 240, 170, 22),
    pygame.Rect(170, 160, 170, 22),
    pygame.Rect(20, 80, 120, 22),
)

COIN_POSITIONS = (
    (225, 445),
    (455, 365),
    (695, 285),
    (475, 205),
    (245, 125),
)

PLAYER_START = (45, 510)
PLAYER_SIZE = (36, 50)
GOAL = pygame.Rect(68, 25, 30, 55)


def make_coins() -> list[pygame.Rect]:
    """Create all coin rectangles."""
    return [pygame.Rect(x, y, 24, 24) for x, y in COIN_POSITIONS]


@dataclass
class PlatformerState(GameState):
    player: pygame.Rect
    velocity_y: int = 0
    on_ground: bool = False
    coins: list[pygame.Rect] = field(default_factory=make_coins)
    score: int = 0
    game_won: bool = False


state = PlatformerState(player=pygame.Rect(*PLAYER_START, *PLAYER_SIZE))


def reset_game(state: PlatformerState) -> None:
    """Reset all mutable game data."""
    state.player.topleft = PLAYER_START
    state.velocity_y = 0
    state.on_ground = False
    state.coins = make_coins()
    state.score = 0
    state.game_won = False


def move_player(state: PlatformerState) -> None:
    """Move the player and resolve platform collisions."""
    keys = get_pressed_keys()
    direction_x = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        direction_x -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        direction_x += 1

    if (
        keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]
    ) and state.on_ground:
        state.velocity_y = JUMP_VELOCITY
        state.on_ground = False

    state.player.x += direction_x * PLAYER_SPEED
    for platform in PLATFORMS:
        if not state.player.colliderect(platform):
            continue
        if direction_x > 0:
            state.player.right = platform.left
        elif direction_x < 0:
            state.player.left = platform.right

    state.player.left = max(0, state.player.left)
    state.player.right = min(SCREEN_WIDTH, state.player.right)

    state.velocity_y = min(state.velocity_y + GRAVITY, MAX_FALL_SPEED)
    state.player.y += state.velocity_y
    state.on_ground = False

    for platform in PLATFORMS:
        if not state.player.colliderect(platform):
            continue
        if state.velocity_y > 0:
            state.player.bottom = platform.top
            state.velocity_y = 0
            state.on_ground = True
        elif state.velocity_y < 0:
            state.player.top = platform.bottom
            state.velocity_y = 0


def collect_coins(state: PlatformerState) -> None:
    """Remove each coin that the player touches."""
    collected = [coin for coin in state.coins if state.player.colliderect(coin)]
    for coin in collected:
        state.coins.remove(coin)
        state.score += 1


def draw_platforms() -> None:
    """Draw the ground and all floating platforms."""
    for platform in PLATFORMS:
        pygame.draw.rect(SCREEN, BROWN, platform, border_radius=5)
        grass = pygame.Rect(platform.x, platform.y, platform.width, 7)
        pygame.draw.rect(SCREEN, GREEN, grass, border_radius=4)


def draw_goal(is_open: bool) -> None:
    """Draw the exit flag."""
    pygame.draw.line(SCREEN, BLACK, GOAL.bottomleft, GOAL.topleft, 4)
    flag_color = GREEN if is_open else RED
    flag_points = (GOAL.topleft, (GOAL.right, GOAL.y + 12), (GOAL.left, GOAL.y + 25))
    pygame.draw.polygon(SCREEN, flag_color, flag_points)


def draw_player(player: pygame.Rect) -> None:
    """Draw the player and its face."""
    pygame.draw.rect(SCREEN, BLUE, player, border_radius=8)
    eye_y = player.y + 15
    pygame.draw.circle(SCREEN, WHITE, (player.x + 11, eye_y), 4)
    pygame.draw.circle(SCREEN, WHITE, (player.right - 11, eye_y), 4)
    pygame.draw.circle(SCREEN, BLACK, (player.x + 11, eye_y), 2)
    pygame.draw.circle(SCREEN, BLACK, (player.right - 11, eye_y), 2)


def draw_scene(state: PlatformerState) -> None:
    """Draw one game frame."""
    SCREEN.fill(SKY)
    pygame.draw.circle(SCREEN, (255, 240, 150), (815, 75), 42)
    draw_platforms()
    draw_goal(not state.coins)

    for coin in state.coins:
        pygame.draw.circle(SCREEN, YELLOW, coin.center, 11)
        pygame.draw.circle(SCREEN, BLACK, coin.center, 11, 2)

    draw_player(state.player)

    score_text = FONT.render(
        f"Coins: {state.score}/{len(COIN_POSITIONS)}", True, BLACK
    )
    SCREEN.blit(score_text, (16, SCREEN_HEIGHT - 37))

    help_text = SMALL_FONT.render(
        "Move: A/D or arrows    Jump: W, Up, or Space    Reset: R",
        True,
        BLACK,
    )
    SCREEN.blit(help_text, (300, SCREEN_HEIGHT - 31))

    if state.game_won:
        message = FONT.render("You win! Press R to play again.", True, BLACK)
        box = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        pygame.draw.rect(SCREEN, WHITE, box.inflate(30, 24), border_radius=8)
        SCREEN.blit(message, box)


@game_loop(ignored_names=("SMALL_FONT",))
def display_game(state: PlatformerState) -> bool:
    """Process input and draw one recorded game frame."""
    for event in get_events():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_r:
                reset_game(state)

    if not state.game_won:
        move_player(state)
        collect_coins(state)
        if not state.coins and state.player.colliderect(GOAL):
            state.game_won = True

    draw_scene(state)
    pygame.display.flip()
    clock.tick(FRAME_RATE)
    return True


if __name__ == "__main__":
    launch_game_loop(
        display_game,
        state,
        db_path="platformer.db",
        session_name="Simple Platformer",
    )
    pygame.quit()
