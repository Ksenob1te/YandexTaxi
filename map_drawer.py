import math
import random
import time
from static import *
import networkx as nx

import pygame
from shapely.geometry import Polygon, MultiPolygon, LineString

# -------------------------------------------------------------------
# 1) GLOBALS & LOADING DATA
# -------------------------------------------------------------------
lons = []
lats = []

node_positions = {node: (data["x"], data["y"]) for node, data in graph.nodes(data=True)}
for (lon, lat) in node_positions.values():
    lons.append(lon)
    lats.append(lat)


def collect_polygon_coords(gdf):
    for idx, row in gdf.iterrows():
        geom = row["geometry"]
        if geom is None:
            continue
        if isinstance(geom, Polygon):
            for (lon, lat) in geom.exterior.coords:
                lons.append(lon)
                lats.append(lat)
        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                for (lon, lat) in poly.exterior.coords:
                    lons.append(lon)
                    lats.append(lat)


collect_polygon_coords(buildings)
collect_polygon_coords(green_areas)

min_lon, max_lon = min(lons), max(lons)
min_lat, max_lat = min(lats), max(lats)


# -------------------------------------------------------------------
# 2) BIG SURFACE & COORDINATE MAPPING
# -------------------------------------------------------------------
def lonlat_to_bigmap_xy(lon, lat):
    frac_x = (lon - min_lon) / (max_lon - min_lon)
    frac_y = (lat - min_lat) / (max_lat - min_lat)
    x = int(frac_x * BIG_MAP_WIDTH)
    y = int((1.0 - frac_y) * BIG_MAP_HEIGHT)
    return (x, y)


# -------------------------------------------------------------------
# 3) FIXING INVALID POLYGONS
# -------------------------------------------------------------------
def fix_polygon(geom):
    if geom is None:
        return geom
    if not geom.is_valid:
        geom = geom.buffer(0)
    return geom


# -------------------------------------------------------------------
# 4) HAND-DRAWN & CROSS-HATCH UTILS
# -------------------------------------------------------------------
def draw_sketch_line(surface, color, start, end, iterations=2, roughness=1):
    for _ in range(random.randint(1, iterations)):
        sx = start[0] + random.randint(-roughness, roughness)
        sy = start[1] + random.randint(-roughness, roughness)
        ex = end[0] + random.randint(-roughness, roughness)
        ey = end[1] + random.randint(-roughness, roughness)
        pygame.draw.aaline(surface, color, (sx, sy), (ex, ey))


def draw_hatch_lines(surface, poly, hatch_spacing, hatch_angle, color):
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
        if poly.is_valid:
            inter = poly.intersection(line)
            if not inter.is_empty:
                if inter.geom_type == "LineString":
                    coords = list(inter.coords)
                    if len(coords) >= 2:
                        pygame.draw.aaline(
                            surface, color,
                            (int(coords[0][0]), int(coords[0][1])),
                            (int(coords[-1][0]), int(coords[-1][1]))
                        )
                elif inter.geom_type == "MultiLineString":
                    for seg in inter.geoms:
                        coords = list(seg.coords)
                        if len(coords) >= 2:
                            pygame.draw.aaline(
                                surface, color,
                                (int(coords[0][0]), int(coords[0][1])),
                                (int(coords[-1][0]), int(coords[-1][1]))
                            )
        c += hatch_spacing


def draw_crosshatch(surface, poly, spacing=10, color=BUILDING_OUTLINE):
    draw_hatch_lines(surface, poly, spacing, 45, color)
    draw_hatch_lines(surface, poly, spacing, -45, color)


def draw_sketch_crosshatch_polygon(surface, outline_color, screen_coords,
                                   hatch_color=None, roughness=1, iterations=2):
    if hatch_color is None:
        hatch_color = outline_color

    raw_poly = Polygon(screen_coords)
    raw_poly = fix_polygon(raw_poly)
    if not raw_poly or not raw_poly.is_valid:
        return

    draw_crosshatch(surface, raw_poly, spacing=10, color=hatch_color)

    for i in range(len(screen_coords)):
        start_pt = screen_coords[i]
        end_pt = screen_coords[(i + 1) % len(screen_coords)]
        draw_sketch_line(surface, outline_color, start_pt, end_pt,
                         iterations=iterations, roughness=roughness)


# -------------------------------------------------------------------
# 5) RENDER THE ENTIRE MAP (BIG SURFACE) ONCE
# -------------------------------------------------------------------
def render_entire_map():
    big_map_surf = pygame.Surface((BIG_MAP_WIDTH, BIG_MAP_HEIGHT), pygame.SRCALPHA)
    big_map_surf.fill(WHITE)

    # Green areas
    for idx, row in green_areas.iterrows():
        geom = row["geometry"]
        if geom is None:
            continue
        geom = fix_polygon(geom)
        if not geom.is_valid:
            continue
        if isinstance(geom, Polygon):
            coords = list(geom.exterior.coords)
            scr_coords = [lonlat_to_bigmap_xy(lon, lat) for (lon, lat) in coords]
            draw_sketch_crosshatch_polygon(
                big_map_surf, GREEN_OUTLINE, scr_coords, hatch_color=GREEN_HATCH, roughness=0
            )
        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                poly = fix_polygon(poly)
                if not poly.is_valid:
                    continue
                coords = list(poly.exterior.coords)
                scr_coords = [lonlat_to_bigmap_xy(lon, lat) for (lon, lat) in coords]
                draw_sketch_crosshatch_polygon(
                    big_map_surf, GREEN_OUTLINE, scr_coords, hatch_color=GREEN_HATCH, roughness=0
                )

    # Buildings
    for idx, row in buildings.iterrows():
        geom = row["geometry"]
        if geom is None:
            continue
        geom = fix_polygon(geom)
        if not geom.is_valid:
            continue
        if isinstance(geom, Polygon):
            coords = list(geom.exterior.coords)
            scr_coords = [lonlat_to_bigmap_xy(lon, lat) for (lon, lat) in coords]
            draw_sketch_crosshatch_polygon(
                big_map_surf, BUILDING_OUTLINE, scr_coords, hatch_color=BUILDING_HATCH, roughness=0
            )
        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                poly = fix_polygon(poly)
                if not poly.is_valid:
                    continue
                coords = list(poly.exterior.coords)
                scr_coords = [lonlat_to_bigmap_xy(lon, lat) for (lon, lat) in coords]
                draw_sketch_crosshatch_polygon(
                    big_map_surf, BUILDING_OUTLINE, scr_coords, hatch_color=BUILDING_HATCH, roughness=0
                )

    # Roads
    for (u, v) in graph.edges():
        lon1, lat1 = node_positions[u]
        lon2, lat2 = node_positions[v]
        start_pos = lonlat_to_bigmap_xy(lon1, lat1)
        end_pos = lonlat_to_bigmap_xy(lon2, lat2)
        draw_sketch_line(big_map_surf, ROAD_COLOR, start_pos, end_pos,
                         iterations=10, roughness=1)

    return big_map_surf


def create_path():
    def draw_path(_screen, _path_nodes, color=(255, 0, 0, 80), thickness=4):
        for i in range(len(_path_nodes) - 1):
            u = _path_nodes[i]
            v = _path_nodes[i + 1]
            lon_u, lat_u = node_positions[u]
            lon_v, lat_v = node_positions[v]
            start_pos = lonlat_to_bigmap_xy(lon_u, lat_u)
            end_pos = lonlat_to_bigmap_xy(lon_v, lat_v)
            pygame.draw.line(_screen, color, start_pos, end_pos, thickness)

    path_surf = pygame.Surface((BIG_MAP_WIDTH, BIG_MAP_HEIGHT), pygame.SRCALPHA)
    path_surf.fill((0, 0, 0, 0))

    start_node, end_node = random.sample(list(graph.nodes), 2)
    print(f"Random start_node = {start_node}, end_node = {end_node}")

    path_nodes = nx.shortest_path(graph, start_node, end_node, weight="length")
    print(f"Path length (nodes): {len(path_nodes)}")

    draw_path(path_surf, path_nodes, color=(255, 214, 51, 80), thickness=8)
    start_node_lon, start_node_lat = node_positions[start_node]
    pan_x, pan_y = lonlat_to_bigmap_xy(start_node_lon, start_node_lat)
    path_cords = [lonlat_to_bigmap_xy(*node_positions[node]) for node in path_nodes]
    return path_surf, -pan_x + WIDTH // 2, -pan_y + HEIGHT // 2, path_cords
