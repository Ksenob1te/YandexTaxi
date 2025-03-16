import math
import pygame
import random
from static import *


class User:
    surface = None
    circle_index = 0
    circle_progress = 0.0
    circle_speed = 1
    user_radius = 100

    circle_x, circle_y = 0, 0

    def __init__(self, circle_progress=0.0, circle_speed=1):
        self.circle_index = 1
        self.circle_progress = circle_progress
        self.circle_speed = circle_speed
        self.surface = pygame.Surface((BIG_MAP_WIDTH, BIG_MAP_HEIGHT), pygame.SRCALPHA)

    @staticmethod
    def interpolate(start, end, progress, speed):
        x1, y1 = start
        x2, y2 = end
        segment_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        if segment_length == 0:
            adjusted_progress = 1.0
        else:
            adjusted_progress = progress + speed / segment_length

        if adjusted_progress >= 1.0:
            adjusted_progress = 1.0

        new_x = x1 + (x2 - x1) * adjusted_progress
        new_y = y1 + (y2 - y1) * adjusted_progress
        return new_x, new_y, adjusted_progress

    def draw_circle_area(self, color, radius, roughness=2, iterations=3, segments=32):
        for _ in range(iterations):
            points = []
            for i in range(segments):
                angle = 2 * math.pi * i / segments
                r = radius + random.randint(-roughness, roughness)
                x = self.circle_x + r * math.cos(angle)
                y = self.circle_y + r * math.sin(angle)
                points.append((x, y))
            for i in range(segments):
                p1 = points[i]
                p2 = points[(i + 1) % segments]
                pygame.draw.aaline(self.surface, color, p1, p2)

    def draw_user(self, path_positions):
        self.surface.fill((0, 0, 0, 0))
        self.draw_circle_area((0, 0, 0, 255), self.user_radius)
        if self.circle_index < len(path_positions) - 1:
            start_pos = path_positions[self.circle_index]
            end_pos = path_positions[self.circle_index + 1]
            self.circle_x, self.circle_y, self.circle_progress = User.interpolate(start_pos, end_pos,
                                                                                  self.circle_progress,
                                                                                  self.circle_speed)

            if self.circle_progress >= 1.0:
                self.circle_progress = 0.0
                self.circle_index += 1
        else:
            self.circle_x, self.circle_y = path_positions[-1]

        pygame.draw.circle(self.surface, (0, 0, 0, 0), (self.circle_x, self.circle_y), 10)
        self.draw_circle_area((187, 150, 0), 6, roughness=1, iterations=4, segments=12)
        # pygame.draw.circle(self.surface, (187, 150, 0), (self.circle_x, self.circle_y), 6)
        pygame.draw.circle(self.surface, (255, 204, 0), (self.circle_x, self.circle_y), 5)

    def draw_empty_circle(self, surface, radius):
        pygame.draw.circle(surface, (0, 0, 0, 0), (self.circle_x, self.circle_y), radius)
