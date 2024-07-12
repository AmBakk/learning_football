import pygame


class Player:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.speed = 5
        self.team = team  # 'red' or 'blue'

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, screen):
        color = (255, 0, 0) if self.team == 'red' else (0, 0, 255)
        pygame.draw.circle(screen, color, (self.x, self.y), 10)
