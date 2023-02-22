from collections import defaultdict

import numpy as np


def points_are_neighbours(point1: tuple[int, ...], point2: tuple[int, ...]):
    if point1[0] == point2[0]:
        if abs(point1[1] - point2[1]) == 1:
            return True
        else:
            return False

    if point1[1] == point2[1]:
        if abs(point1[0] - point2[0]) == 1:
            return True
        else:
            return False


def sort_coords_by_height(heightmap: np.ndarray):
    coords_with_height: defaultdict[int, list[tuple[int, ...]]]\
        = defaultdict(list)

    for height in range(heightmap.min(), heightmap.max() + 1):
        for xz, y in np.ndenumerate(heightmap):
            if y == height:
                coords_with_height[y].append(xz)

    return coords_with_height


def cont_planes(heightmap: np.ndarray):
    coords_with_height = sort_coords_by_height(heightmap)
    continuous_fields: dict[tuple[int, ...],
                            list[tuple[int, ...]]] = {}

    for height, coords in coords_with_height.items():
        for ref_coord in coords:
            print(f"Checking points continuous with {ref_coord}")
            continuous = [ref_coord]
            coords_with_height[height].remove(ref_coord)

            for to_check in coords:
                for already_cont in continuous:
                    if points_are_neighbours(to_check, already_cont):
                        continuous.append(to_check)
                        coords_with_height[height].remove(to_check)

            continuous_fields[ref_coord] = continuous

    cont_map = np.zeros(heightmap.shape)
    for i, k in enumerate(continuous_fields):
        for coord in continuous_fields[k]:
            cont_map[coord[0], coord[1]] = i

    return cont_map
