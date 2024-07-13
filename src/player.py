import pygame


class Player:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        # Ensure the player stays within the screen bounds
        if 0 <= new_x <= 800:
            self.x = new_x
        if 0 <= new_y <= 600:
            self.y = new_y

    def draw(self, screen):
        color = (255, 0, 0) if self.team == 'red' else (0, 0, 255)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 10)
