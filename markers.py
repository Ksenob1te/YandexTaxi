import math
import random
import pygame
from shapely.geometry import Polygon, LineString
from static import *


class Marker:
    marker_x, marker_y = 0, 0
    surface = None
    polygon = None
    dot_array = []
    active = []

    def __init__(self, marker_x, marker_y, color=(0, 0, 255), name="Marker"):
        self.color = color
        self.name = name
        self.marker_x = marker_x
        self.marker_y = marker_y
        if Marker.surface is None:
            Marker.surface = pygame.Surface((BIG_MAP_WIDTH, BIG_MAP_HEIGHT), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))

    def draw_hatch_lines(self, hatch_spacing, hatch_angle, color):
        import math
        theta = math.radians(hatch_angle)
        nx = -math.sin(theta)
        ny = math.cos(theta)
        min_x, min_y, max_x, max_y = self.polygon.bounds
        corners = [(min_x, min_y), (min_x, max_y), (max_x, min_y), (max_x, max_y)]
        c_values = [nx * x + ny * y for (x, y) in corners]
        c_min, c_max = min(c_values), max(c_values)

        center = ((min_x + max_x) / 2, (min_y + max_y) / 2)
        dx = math.cos(theta)
        dy = math.sin(theta)
        L = math.sqrt((max_x - min_x) ** 2 + (max_y - min_y) ** 2) * 1.5

        c = c_min - hatch_spacing
        while c < c_max + hatch_spacing:
            center_proj = nx * center[0] + ny * center[1]
            d = c - center_proj
            p0 = (center[0] + d * nx, center[1] + d * ny)
            p1 = (p0[0] - L * dx, p0[1] - L * dy)
            p2 = (p0[0] + L * dx, p0[1] + L * dy)
            line = LineString([p1, p2])
            if self.polygon.is_valid:
                inter = self.polygon.intersection(line)
                if not inter.is_empty:
                    if inter.geom_type == "LineString":
                        coords = list(inter.coords)
                        if len(coords) >= 2:
                            pygame.draw.line(Marker.surface, color,
                                             (coords[0][0], coords[0][1]),
                                             (coords[-1][0], coords[-1][1]), width=2)
                    elif inter.geom_type == "MultiLineString":
                        for seg in inter.geoms:
                            coords = list(seg.coords)
                            if len(coords) >= 2:
                                pygame.draw.line(Marker.surface, color,
                                                 (coords[0][0], coords[0][1]),
                                                 (coords[-1][0], coords[-1][1]), width=2)
            c += hatch_spacing

    def crosshatch_polygon(self, color=(100, 100, 100), spacing=8):
        self.draw_hatch_lines(spacing, 45, color)
        self.draw_hatch_lines(spacing, -45, color)

    def draw_sketch_outline(self, color=(0, 0, 0),
                            roughness=1, iterations=2):
        for i in range(len(self.dot_array)):
            start = self.dot_array[i]
            end = self.dot_array[(i + 1) % len(self.dot_array)]
            for _ in range(iterations):
                sx = start[0] + random.randint(-roughness, roughness)
                sy = start[1] + random.randint(-roughness, roughness)
                ex = end[0] + random.randint(-roughness, roughness)
                ey = end[1] + random.randint(-roughness, roughness)
                pygame.draw.aaline(Marker.surface, color, (sx, sy), (ex, ey))

    def build_marker_shape(self, radius=20, tip_height=30, segments=12):
        shape_points = []
        for i in range(segments + 1):
            angle = math.pi + (i * (math.pi / segments))
            x = self.marker_x + radius * math.cos(angle)
            y = self.marker_y + radius * math.sin(angle)
            shape_points.append((x, y))

        bottom_tip = (self.marker_x, self.marker_y + tip_height)
        shape_points.append(bottom_tip)
        return shape_points

    def draw_marker(self, radius=20, tip_height=30, refresh=False):
        # pygame.draw.circle(Marker.surface, (255, 204, 0), (self.marker_x, self.marker_y), 5)
        if self.polygon is None or refresh:
            self.dot_array = self.build_marker_shape(radius=radius,
                                                     tip_height=tip_height,
                                                     segments=12)
            self.polygon = Polygon(self.dot_array)
        self.crosshatch_polygon(color=self.color, spacing=6)
        self.draw_sketch_outline(color=(102, 82, 0), roughness=2, iterations=2)

    def update_marker(self, user_x, user_y, user_radius):
        dx = user_x - self.marker_x
        dy = user_y - self.marker_y
        dist = math.hypot(dx, dy)
        if dist < user_radius * 1.25:
            min_x, min_y, max_x, max_y = self.polygon.bounds
            pygame.draw.rect(self.surface, (0, 0, 0, 0),
                             (min_x - 5, min_y - 5, max_x - min_x + 10, max_y - min_y + 10))
            self.draw_marker(radius=22, tip_height=33, refresh=True)
            if self not in Marker.active:
                Marker.active.append(self)
        else:
            if self in Marker.active:
                min_x, min_y, max_x, max_y = self.polygon.bounds
                pygame.draw.rect(self.surface, (0, 0, 0, 0),
                                 (min_x - 5, min_y - 5, max_x - min_x + 10, max_y - min_y + 10))
                self.draw_marker(refresh=True)
                Marker.active.remove(self)


def generate_random_markers(num_markers=400, min_dist=100):
    markers = []
    attempts = 0
    max_attempts = 10000

    while len(markers) < num_markers and attempts < max_attempts:
        x = random.randint(0, BIG_MAP_WIDTH)
        y = random.randint(0, BIG_MAP_HEIGHT)

        too_close = False
        for m in markers:
            dx = x - m.marker_x
            dy = y - m.marker_y
            dist = math.hypot(dx, dy)
            if dist < min_dist:
                too_close = True
                break

        if not too_close:
            markers.append(Marker(x, y, color=(187, 150, 0)))

        attempts += 1

    if len(markers) < num_markers:
        print(f"Warning: Only placed {len(markers)} markers "
              f"before hitting {max_attempts} attempts.")

    return markers
