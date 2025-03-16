import osmnx as ox
import pygame
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, LineString
import math
import random
import time
from static import *

# -------------------------------
# 1. LOAD MAP DATA, BUILDINGS, AND GREEN AREAS
# -------------------------------
graph = ox.load_graphml("moscow_roads_tverskoy.graphml")
buildings = gpd.read_file("moscow_buildings_tverskoy.geojson")
green_areas = gpd.read_file("moscow_green_tverskoy.geojson")

node_positions = {node: (data['x'], data['y']) for node, data in graph.nodes(data=True)}
# -------------------------------
# 2. SETUP PYGAME
# -------------------------------

start_cord = list(node_positions.values())[-1]
scale = 100000


def latlon_to_screen(lon, lat, offset_x=0, offset_y=0):
    x = (lon - start_cord[0]) * scale + offset_x
    y = (start_cord[1] - lat) * scale + offset_y
    return int(x), int(y)


def is_on_screen(points):
    xs = [pt[0] for pt in points]
    ys = [pt[1] for pt in points]
    if max(xs) < 0 or min(xs) > WIDTH or max(ys) < 0 or min(ys) > HEIGHT:
        return False
    return True


# -------------------------------
# 3. HAND-DRAWN AND CROSS-HATCH FUNCTIONS
# -------------------------------

def draw_sketch_line(surface, color, start, end, thickness=1, roughness=3, iterations=2):
    for _ in range(iterations):
        sx = start[0] + random.randint(-roughness, roughness)
        sy = start[1] + random.randint(-roughness, roughness)
        ex = end[0] + random.randint(-roughness, roughness)
        ey = end[1] + random.randint(-roughness, roughness)
        pygame.draw.aaline(surface, color, (sx, sy), (ex, ey), thickness)


def draw_hatch_lines(surface, poly, hatch_spacing, hatch_angle, color, thickness=1):
    theta = math.radians(hatch_angle)
    nx = -math.sin(theta)
    ny = math.cos(theta)
    min_x, min_y, max_x, max_y = poly.bounds
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
        if not poly.is_valid:
            continue
        inter = poly.intersection(line)
        if not inter.is_empty:
            if inter.geom_type == 'LineString':
                coords = list(inter.coords)
                if len(coords) >= 2:
                    pygame.draw.aaline(surface, color, (int(coords[0][0]), int(coords[0][1])),
                                       (int(coords[-1][0]), int(coords[-1][1])), thickness)
            elif inter.geom_type == 'MultiLineString':
                for seg in inter.geoms:
                    coords = list(seg.coords)
                    if len(coords) >= 2:
                        pygame.draw.aaline(surface, color, (int(coords[0][0]), int(coords[0][1])),
                                           (int(coords[-1][0]), int(coords[-1][1])), thickness)
        c += hatch_spacing


def draw_crosshatch(surface, poly, spacing=10, color=(100, 100, 100), thickness=1):
    draw_hatch_lines(surface, poly, hatch_spacing=spacing, hatch_angle=45, color=color, thickness=thickness)
    draw_hatch_lines(surface, poly, hatch_spacing=spacing, hatch_angle=-45, color=color, thickness=thickness)


def draw_sketch_crosshatch_polygon(surface, outline_color, points,
                                   outline_thickness=1, roughness=3, iterations=2,
                                   hatch_spacing=10, hatch_color=None):
    if hatch_color is None:
        hatch_color = outline_color
    poly = Polygon(points)
    draw_crosshatch(surface, poly, spacing=hatch_spacing, color=hatch_color, thickness=1)
    for i in range(len(points)):
        start_pt = points[i]
        end_pt = points[(i + 1) % len(points)]
        draw_sketch_line(surface, outline_color, start_pt, end_pt,
                         thickness=outline_thickness, roughness=roughness, iterations=iterations)


# -------------------------------
# 4. DRAW MAP FUNCTION (GREEN AREAS, BUILDINGS, AND ROADS)
# -------------------------------
def draw_map(screen, offset_x=0, offset_y=0):
    start_time = time.perf_counter()
    for idx, row in green_areas.iterrows():
        geom = row['geometry']
        if geom is None:
            continue
        if isinstance(geom, Polygon):
            coords = list(geom.exterior.coords)
            screen_coords = [latlon_to_screen(*pt, offset_x=offset_x, offset_y=offset_y) for pt in coords]
            if is_on_screen(screen_coords):
                draw_sketch_crosshatch_polygon(screen,
                                               GREEN_OUTLINE,
                                               screen_coords,
                                               outline_thickness=1,
                                               roughness=2,
                                               iterations=2,
                                               hatch_spacing=10,
                                               hatch_color=GREEN_HATCH)
        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                coords = list(poly.exterior.coords)
                screen_coords = [latlon_to_screen(*pt, offset_x=offset_x, offset_y=offset_y) for pt in coords]
                if is_on_screen(screen_coords):
                    draw_sketch_crosshatch_polygon(screen,
                                                   GREEN_OUTLINE,
                                                   screen_coords,
                                                   outline_thickness=1,
                                                   roughness=2,
                                                   iterations=2,
                                                   hatch_spacing=10,
                                                   hatch_color=GREEN_HATCH)
    end_time = time.perf_counter()
    print(f"Green area time: {end_time - start_time:.4f} seconds")

    start_time = time.perf_counter()
    for idx, row in buildings.iterrows():
        geom = row['geometry']
        if geom is None:
            continue
        if isinstance(geom, Polygon):
            coords = list(geom.exterior.coords)
            screen_coords = [latlon_to_screen(*pt, offset_x=offset_x, offset_y=offset_y) for pt in coords]
            if is_on_screen(screen_coords):
                draw_sketch_crosshatch_polygon(screen,
                                               BUILDING_OUTLINE,
                                               screen_coords,
                                               outline_thickness=1,
                                               roughness=2,
                                               iterations=2,
                                               hatch_spacing=10,
                                               hatch_color=BUILDING_HATCH)
        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                coords = list(poly.exterior.coords)
                screen_coords = [latlon_to_screen(*pt, offset_x=offset_x, offset_y=offset_y) for pt in coords]
                if is_on_screen(screen_coords):
                    draw_sketch_crosshatch_polygon(screen,
                                                   BUILDING_OUTLINE,
                                                   screen_coords,
                                                   outline_thickness=1,
                                                   roughness=2,
                                                   iterations=2,
                                                   hatch_spacing=10,
                                                   hatch_color=BUILDING_HATCH)
    end_time = time.perf_counter()
    print(f"Building area time: {end_time - start_time:.4f} seconds")

    start_time = time.perf_counter()
    for u, v in graph.edges():
        start_pos = latlon_to_screen(*node_positions[u], offset_x=offset_x, offset_y=offset_y)
        end_pos = latlon_to_screen(*node_positions[v], offset_x=offset_x, offset_y=offset_y)
        if is_on_screen([start_pos, end_pos]):
            draw_sketch_line(screen,
                             ROAD_COLOR,
                             start_pos, end_pos,
                             thickness=2,
                             roughness=2,
                             iterations=2)
    end_time = time.perf_counter()
    print(f"Roads time: {end_time - start_time:.4f} seconds")

