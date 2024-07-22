import pygame
from src.player import Player
from src.ball import Ball
import math
import random


class FootballGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Learning Football')
        self.clock = pygame.time.Clock()
        self.running = True
        self.players = [
            Player(100, 300, 'red'),
            Player(200, 300, 'red'),
            Player(300, 300, 'red'),
            Player(500, 300, 'blue'),
            Player(600, 300, 'blue'),
            Player(700, 300, 'blue')
        ]
        self.ball = Ball(400, 300)
        self.ball_carrier = None
        self.controlled_player = self.players[2]
        self.last_direction = (0, 0)
        self.grace_period = 0  # Frames of grace period
        self.pass_in_progress = False
        self.pass_target = None
        self.pass_step = (0, 0)
        self.pass_cooldown = 0  # Frames of cooldown after passing
        self.last_pass_player = None  # Initialize last_pass_player
        self.last_possession_team = None  # Track the last team to have possession
        self.random_movement_direction = {player: (0, 0) for player in self.players}
        self.random_movement_timer = {player: 0 for player in self.players}
        self.forced_pass_player = None  # Player forced to pass before moving again
        self.blue_score = 0
        self.red_score = 0
        self.restrict_pass_direction = False  # Restrict pass direction during kickoff
        self.pass_speed = 5  # Adjust as needed
        self.shoot_speed = 10  # Adjust as needed
        self.accuracy_factor = 0.1  # Adjust as needed

    def check_ball_possession(self):
        if self.grace_period > 0 or self.pass_in_progress:
            self.grace_period -= 1
            return

        for player in self.players:
            if player == self.last_pass_player and self.pass_cooldown > 0:
                continue
            if (player.x - self.ball.x) ** 2 + (player.y - self.ball.y) ** 2 < 200:  # Increased possession radius
                if self.ball_carrier != player:
                    if self.ball_carrier is None:
                        self.ball_carrier = player
                        self.controlled_player = player
                    else:
                        if self.ball_carrier.team == player.team:
                            self.ball_carrier = player
                            self.controlled_player = player
                        else:
                            if random.random() < 0.5:
                                self.ball_carrier = player
                            self.controlled_player = self.ball_carrier
                    self.grace_period = 10
                    self.last_possession_team = self.ball_carrier.team  # Update last possession team
                    break

        # Ensure the forced pass player maintains possession
        if self.forced_pass_player:
            self.ball_carrier = self.forced_pass_player
            self.controlled_player = self.forced_pass_player
            self.last_possession_team = self.forced_pass_player.team  # Update last possession team

    def move_ball_with_carrier(self):
        if self.ball_carrier and not self.pass_in_progress:
            self.ball.x = self.ball_carrier.x
            self.ball.y = self.ball_carrier.y

            # Check if the ball carrier moves out of bounds
            if self.ball.x < 50 or self.ball.x > 750 or self.ball.y < 50 or self.ball.y > 550:
                self.handle_ball_out_of_bounds()

    def kick_ball(self, target_position, is_shot=False):
        if self.ball_carrier:
            if self.forced_pass_player and is_shot:
                return  # Player in forced pass position can only pass

            speed = self.shoot_speed if is_shot else self.pass_speed

            # Calculate inaccuracy based on distance with cubic scaling
            dx = target_position[0] - self.ball.x
            dy = target_position[1] - self.ball.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if is_shot:
                # Cubic scaling for error
                error_factor = self.accuracy_factor * (distance / 100) ** 3
                self.error_x = error_factor
                self.error_y = error_factor
            else:
                self.error_x = 0
                self.error_y = 0

            self.intended_target = target_position
            dx = target_position[0] - self.ball.x
            dy = target_position[1] - self.ball.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            self.pass_step = (dx / distance * speed, dy / distance * speed)
            self.pass_target = target_position
            self.last_pass_player = self.ball_carrier
            self.ball_carrier = None
            self.pass_in_progress = True
            self.pass_cooldown = 10  # Set cooldown period after passing
            self.forced_pass_player = None

    def update_kick(self):
        if self.pass_in_progress:
            self.ball.x += self.pass_step[0]
            self.ball.y += self.pass_step[1]

            for player in self.players:
                if player == self.last_pass_player and self.pass_cooldown > 0:
                    continue
                if (player.x - self.ball.x) ** 2 + (player.y - self.ball.y) ** 2 < 200:  # Increased possession radius
                    self.ball_carrier = player
                    self.controlled_player = player
                    self.pass_in_progress = False
                    self.grace_period = 10
                    self.ball.x = player.x
                    self.ball.y = player.y
                    self.pass_cooldown = 0  # Reset cooldown when possession changes
                    return

            if abs(self.ball.x - self.pass_target[0]) < abs(self.pass_step[0]) and abs(
                    self.ball.y - self.pass_target[1]) < abs(self.pass_step[1]):
                self.pass_in_progress = False
                self.grace_period = 10
                self.ball.x, self.ball.y = self.pass_target
                self.controlled_player = self.find_closest_player()
                self.pass_cooldown = 0  # Reset cooldown when pass completes

            # Check if the ball leaves the pitch
            if self.ball.x < 50 or self.ball.x > 750 or self.ball.y < 50 or self.ball.y > 550:
                self.handle_ball_out_of_bounds()

    def handle_ball_out_of_bounds(self):
        self.pass_in_progress = False
        self.grace_period = 10
        self.ball_carrier = None

        if self.last_possession_team:
            opposite_team = 'red' if self.last_possession_team == 'blue' else 'blue'
        else:
            opposite_team = 'red' if self.controlled_player.team == 'blue' else 'blue'

        # Check for goals
        if self.ball.x < 50 and 260 <= self.ball.y <= 340:  # Left goal (goal for blue)
            self.blue_score += 1
            self.reset_after_goal('blue')
            return
        elif self.ball.x > 750 and 260 <= self.ball.y <= 340:  # Right goal (goal for red)
            self.red_score += 1
            self.reset_after_goal('red')
            return

        # Determine the new spot based on which boundary the ball left
        if self.ball.y < 50:  # Top boundary
            self.controlled_player = self.find_closest_player_by_team(opposite_team)
            self.controlled_player.x, self.controlled_player.y = self.ball.x, 50
            self.ball.x = self.controlled_player.x
            self.ball.y = self.controlled_player.y + random.randint(20, 50)
        elif self.ball.y > 550:  # Bottom boundary
            self.controlled_player = self.find_closest_player_by_team(opposite_team)
            self.controlled_player.x, self.controlled_player.y = self.ball.x, 550
            self.ball.x = self.controlled_player.x
            self.ball.y = self.controlled_player.y - random.randint(20, 50)
        elif self.ball.x < 50:  # Left boundary (red side)
            if self.last_possession_team == 'red':  # Red team kicked out
                # Blue team gets a corner kick
                self.controlled_player = self.find_closest_player_by_team('blue')
                self.controlled_player.x, self.controlled_player.y = 50, 50 if self.ball.y < 300 else 550
            else:  # Blue team kicked out
                # Red team gets a goal kick
                self.controlled_player = self.find_closest_player_by_team('red')
                self.controlled_player.x, self.controlled_player.y = 80, 300  # Goal kick spot
            self.ball.x = self.controlled_player.x
            self.ball.y = self.controlled_player.y
        elif self.ball.x > 750:  # Right boundary (blue side)
            if self.last_possession_team == 'blue':  # Blue team kicked out
                # Red team gets a corner kick
                self.controlled_player = self.find_closest_player_by_team('red')
                self.controlled_player.x, self.controlled_player.y = 750, 50 if self.ball.y < 300 else 550
            else:  # Red team kicked out
                # Blue team gets a goal kick
                self.controlled_player = self.find_closest_player_by_team('blue')
                self.controlled_player.x, self.controlled_player.y = 700, 300  # Goal kick spot
            self.ball.x = self.controlled_player.x
            self.ball.y = self.controlled_player.y

        self.ball_carrier = self.controlled_player
        self.forced_pass_player = self.controlled_player

        # Ensure the player has possession and cannot lose it until they make a pass
        self.grace_period = 10  # Set grace period to prevent immediate collisions
        self.last_possession_team = self.controlled_player.team  # Update last possession team

    def find_closest_player(self):
        min_distance = float('inf')
        closest_player = None
        for player in self.players:
            distance = math.sqrt((player.x - self.ball.x) ** 2 + (player.y - self.ball.y) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_player = player
        return closest_player

    def find_closest_player_by_team(self, team):
        min_distance = float('inf')
        closest_player = None
        for player in self.players:
            if player.team == team:
                distance = math.sqrt((player.x - self.ball.x) ** 2 + (player.y - self.ball.y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    closest_player = player
        return closest_player

    def move_randomly(self, player):
        if player == self.forced_pass_player:
            return

        if self.random_movement_timer[player] <= 0:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            self.random_movement_direction[player] = random.choice(directions)
            self.random_movement_timer[player] = random.randint(15, 30)  # Change direction every 0.25 to 0.5 second
        else:
            self.random_movement_timer[player] -= 1

        player.move(self.random_movement_direction[player][0] * 2,
                    self.random_movement_direction[player][1] * 2)  # Increased step size

    def draw_pitch(self):
        # Green background
        self.screen.fill((0, 128, 0))

        # Pitch boundaries
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(50, 50, 700, 500), 5)

        # Center line
        pygame.draw.line(self.screen, (255, 255, 255), (400, 50), (400, 550), 5)

        # Center circle
        pygame.draw.circle(self.screen, (255, 255, 255), (400, 300), 50, 5)

        # Center spot
        pygame.draw.circle(self.screen, (255, 255, 255), (400, 300), 5)

        # Penalty areas
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(50, 200, 100, 200), 5)
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(650, 200, 100, 200), 5)

        # Goals
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(50, 250, 20, 100), 5)
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(730, 250, 20, 100), 5)

        # Netting behind goals (aligned with boundary, smaller on Y axis, larger on X axis, with border)
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(35, 260, 15, 80), 1)  # Left netting border
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(750, 260, 15, 80), 1)  # Right netting border

        for y in range(260, 340, 10):
            pygame.draw.line(self.screen, (255, 255, 255), (35, y), (50, y), 1)  # Left netting horizontal lines
            pygame.draw.line(self.screen, (255, 255, 255), (750, y), (765, y), 1)  # Right netting horizontal lines

        for x in range(35, 50, 2):
            pygame.draw.line(self.screen, (255, 255, 255), (x, 260), (x, 340), 1)  # Left netting vertical lines
        for x in range(750, 765, 2):
            pygame.draw.line(self.screen, (255, 255, 255), (x, 260), (x, 340), 1)  # Right netting vertical lines

        # Corner arcs (thicker and extending further out)
        pygame.draw.arc(self.screen, (255, 255, 255), (15, 15, 70, 70), math.radians(270), math.radians(360),
                        5)  # Top left
        pygame.draw.arc(self.screen, (255, 255, 255), (715, 15, 70, 70), math.radians(180), math.radians(270),
                        5)  # Top right
        pygame.draw.arc(self.screen, (255, 255, 255), (15, 515, 70, 70), math.radians(0), math.radians(90),
                        5)  # Bottom left
        pygame.draw.arc(self.screen, (255, 255, 255), (715, 515, 70, 70), math.radians(90), math.radians(180),
                        5)  # Bottom right

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.pass_in_progress:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.kick_ball((mouse_x, mouse_y), is_shot=False)  # Left mouse button for pass
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.pass_in_progress and self.controlled_player != self.forced_pass_player:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        self.kick_ball((mouse_x, mouse_y), is_shot=True)  # Space bar for shooting

            keys = pygame.key.get_pressed()
            direction = (0, 0)
            if keys[pygame.K_a] and self.controlled_player != self.forced_pass_player:
                self.controlled_player.move(-2, 0)  # Increased step size
                direction = (-2, 0)
            if keys[pygame.K_d] and self.controlled_player != self.forced_pass_player:
                self.controlled_player.move(2, 0)  # Increased step size
                direction = (2, 0)
            if keys[pygame.K_w] and self.controlled_player != self.forced_pass_player:
                self.controlled_player.move(0, -2)  # Increased step size
                direction = (0, -2)
            if keys[pygame.K_s] and self.controlled_player != self.forced_pass_player:
                self.controlled_player.move(0, 2)  # Increased step size
                direction = (0, 2)

            if direction != (0, 0):
                self.last_direction = direction

            if self.pass_cooldown > 0:
                self.pass_cooldown -= 1

            self.check_ball_possession()
            self.move_ball_with_carrier()
            self.update_kick()

            for player in self.players:
                if player != self.controlled_player:
                    self.move_randomly(player)

            self.draw_pitch()
            self.draw_scoreboard()  # Draw the scoreboard
            self.draw_trajectory()  # Draw the intended trajectory and possible spread

            for player in self.players:
                player.draw(self.screen)
            self.ball.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def reset_after_goal(self, scoring_team):
        self.ball.x, self.ball.y = 400, 300  # Reset ball to center
        if scoring_team == 'red':
            self.controlled_player = self.find_closest_player_by_team('blue')  # Blue team gets possession
            self.last_possession_team = 'blue'
        else:
            self.controlled_player = self.find_closest_player_by_team('red')  # Red team gets possession
            self.last_possession_team = 'red'

        self.ball_carrier = self.controlled_player
        self.forced_pass_player = self.controlled_player  # Force pass
        self.controlled_player.x, self.controlled_player.y = 400, 300  # Place player in the center
        self.grace_period = 10  # Set grace period to prevent immediate collisions
        self.restrict_pass_direction = True  # Restrict pass direction

    def draw_scoreboard(self):
        font = pygame.font.Font(None, 36)
        score_text = f"Red: {self.red_score}  Blue: {self.blue_score}"
        text = font.render(score_text, True, (255, 255, 255))
        self.screen.blit(text, (300, 10))

    def draw_trajectory(self):
        if self.pass_in_progress and self.intended_target:
            # Draw the intended trajectory (dotted line)
            start_pos = (self.ball.x, self.ball.y)
            end_pos = self.intended_target
            pygame.draw.line(self.screen, (0, 0, 0), start_pos, end_pos, 1)  # Solid line

            # Draw the possible spread (range curves)
            if self.error_x and self.error_y:
                for i in range(1, 6):
                    factor = i / 5
                    spread_left = (
                    self.intended_target[0] - self.error_x * factor, self.intended_target[1] - self.error_y * factor)
                    spread_right = (
                    self.intended_target[0] + self.error_x * factor, self.intended_target[1] + self.error_y * factor)
                    pygame.draw.line(self.screen, (0, 0, 0), start_pos, spread_left, 1)  # Left range line
                    pygame.draw.line(self.screen, (0, 0, 0), start_pos, spread_right, 1)  # Right range line




