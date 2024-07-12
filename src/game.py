import pygame
from src.player import Player
from src.ball import Ball
import math
import random


class FootballGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('2D Football Game')
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
        self.controlled_player = self.players[0]
        self.last_direction = (0, 0)
        self.grace_period = 0  # Frames of grace period

    def check_ball_possession(self):
        if self.grace_period > 0:
            self.grace_period -= 1
            return

        for player in self.players:
            if (player.x - self.ball.x) ** 2 + (player.y - self.ball.y) ** 2 < 100:
                if self.ball_carrier != player:
                    if self.ball_carrier is None:
                        self.ball_carrier = player
                        self.controlled_player = player
                    else:
                        if self.ball_carrier.team == player.team:
                            # Give control to the player that did not have the ball
                            self.ball_carrier = player
                            self.controlled_player = player
                        else:
                            # 50% chance to retain or give away possession
                            if random.random() < 0.5:
                                self.ball_carrier = player
                            # In either case, switch control to the new ball carrier
                            self.controlled_player = self.ball_carrier
                    self.grace_period = 10  # Set grace period to 10 frames
                    break

    def move_ball_with_carrier(self):
        if self.ball_carrier:
            self.ball.x = self.ball_carrier.x
            self.ball.y = self.ball_carrier.y

    def pass_ball(self):
        if self.ball_carrier and self.last_direction != (0, 0):
            # Pass ball in the last direction
            self.ball.x += self.last_direction[0] * 50
            self.ball.y += self.last_direction[1] * 50
            self.ball_carrier = None
            self.controlled_player = self.find_closest_player()
            self.grace_period = 10  # Set grace period to avoid immediate change

    def find_closest_player(self):
        min_distance = float('inf')
        closest_player = None
        for player in self.players:
            distance = math.sqrt((player.x - self.ball.x) ** 2 + (player.y - self.ball.y) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_player = player
        return closest_player

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            direction = (0, 0)
            if keys[pygame.K_LEFT]:
                self.controlled_player.move(-1, 0)
                direction = (-1, 0)
            if keys[pygame.K_RIGHT]:
                self.controlled_player.move(1, 0)
                direction = (1, 0)
            if keys[pygame.K_UP]:
                self.controlled_player.move(0, -1)
                direction = (0, -1)
            if keys[pygame.K_DOWN]:
                self.controlled_player.move(0, 1)
                direction = (0, 1)

            if direction != (0, 0):
                self.last_direction = direction

            if keys[pygame.K_q]:
                self.pass_ball()

            self.check_ball_possession()
            self.move_ball_with_carrier()

            self.screen.fill((0, 128, 0))
            for player in self.players:
                player.draw(self.screen)
            self.ball.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
