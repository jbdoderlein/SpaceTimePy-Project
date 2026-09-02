import random
from dataclasses import dataclass, field

import pygame
from spacetimepy_pygame import GameState, game_loop, get_events, launch_game_loop

# Initialize pygame
pygame.init()
random.seed(42)

# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
GRAVITY = 0.6
JUMP_VELOCITY = -7
PIPE_GAP = 270
PIPE_SPEED = 3
PIPE_SPAWN_DISTANCE = 300
FRAME_RATE = 60
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")


FONT = pygame.font.SysFont("Arial", 30)

# Clock object
clock = pygame.time.Clock()


@dataclass
class FlappyState(GameState):
    bird_rect: pygame.Rect
    bird_movement: float = 0.0
    pipes: list[pygame.Rect] = field(default_factory=list)
    game_active: bool = True
    score: int = 0


state = FlappyState(
    bird_rect=pygame.Rect(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2, 40, 40)
)


def create_pipe() -> tuple[pygame.Rect, pygame.Rect]:
    """Create a new pipe pair."""
    # Random position for the gap between top and bottom pipes
    gap_y_pos = random.randint(200, SCREEN_HEIGHT - 200)

    # Bottom pipe starts at the gap position and extends to the bottom of the screen
    bottom_pipe = pygame.Rect(
        SCREEN_WIDTH,
        gap_y_pos + PIPE_GAP // 2,
        100,
        SCREEN_HEIGHT - gap_y_pos - PIPE_GAP // 2,
    )

    # Top pipe starts at the top of the screen and extends to the gap position
    top_pipe = pygame.Rect(SCREEN_WIDTH, 0, 100, gap_y_pos - PIPE_GAP // 2)

    return bottom_pipe, top_pipe


def move_pipes(state: FlappyState) -> None:
    pipes_to_remove: list[pygame.Rect] = []
    for pipe in state.pipes:
        pipe.x -= PIPE_SPEED
        if pipe.right < 0:  # Check if pipe is completely off-screen to the left
            pipes_to_remove.append(pipe)

    # Remove pipes that left the screen.
    for expired_pipe in pipes_to_remove:
        state.pipes.remove(expired_pipe)


def draw_pipes(state: FlappyState) -> None:
    """Draw all pipes."""
    for pipe in state.pipes:
        if pipe.y == 0:  # Top pipe
            pygame.draw.rect(SCREEN, (0, 128, 0), pipe)
        else:  # Bottom pipe
            pygame.draw.rect(SCREEN, (0, 128, 0), pipe)


def check_collision(state: FlappyState) -> bool:
    """Check for a bird collision."""
    if state.bird_rect.top <= 0 or state.bird_rect.bottom >= SCREEN_HEIGHT:
        return True

    for pipe in state.pipes:
        if state.bird_rect.colliderect(pipe):
            return True

    return False


def reset_game(state: FlappyState) -> None:
    """Reset the game state."""
    state.bird_rect.y = SCREEN_HEIGHT // 2
    state.bird_movement = 0.0
    state.pipes.clear()
    state.game_active = True
    state.score = 0


@game_loop
def display_game(state: FlappyState) -> bool:
    for event in get_events():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and state.game_active:
                state.bird_movement = JUMP_VELOCITY

            if event.key == pygame.K_SPACE and not state.game_active:
                reset_game(state)

    # Fill background
    SCREEN.fill((135, 206, 235))

    if state.game_active:
        # Bird movement
        state.bird_movement += GRAVITY
        state.bird_rect.y = int(state.bird_rect.y + state.bird_movement)

        # Draw bird
        pygame.draw.rect(SCREEN, (255, 0, 0), state.bird_rect, border_radius=10)

        # Pipe logic
        if (
            len(state.pipes) == 0
            or state.pipes[-1].x < SCREEN_WIDTH - PIPE_SPAWN_DISTANCE
        ):
            bottom_pipe, top_pipe = create_pipe()
            state.pipes.append(bottom_pipe)
            state.pipes.append(top_pipe)

        move_pipes(state)
        draw_pipes(state)

        # Check collision
        if check_collision(state):
            state.game_active = False

    else:
        # Game over screen
        game_over_text = FONT.render("Game Over!", True, (0, 0, 0))
        SCREEN.blit(
            game_over_text,
            (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 15),
        )

    # Update display
    pygame.display.update()
    clock.tick(FRAME_RATE)
    return True


if __name__ == "__main__":
    launch_game_loop(
        display_game,
        state,
        db_path="flappy.db",
        session_name="Flappy Bird",
    )
    pygame.quit()
