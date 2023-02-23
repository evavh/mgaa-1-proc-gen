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
    cont_planes: dict[tuple[int, ...],
                      list[tuple[int, ...]]] = {}

    for height, coords in coords_with_height.items():
        print(f"Looking at height {height} with {len(coords)} coords")
        already_checked = []

        for ref_coord in coords:
            if ref_coord not in already_checked:
                print(f"Checking {len(coords)} points for continuity with "
                      f"{ref_coord} ({height} high)")
                continuous = [ref_coord]
                # coords.remove(ref_coord)

                for to_check in coords:
                    # print(f"Checking all in {coords}")
                    print(f"{len(continuous)} continuous points found",
                          end='\r')
                    for already_cont in continuous:
                        # print(f"Comparing {to_check} to {already_cont}")
                        if points_are_neighbours(to_check, already_cont):
                            continuous.append(to_check)
                            already_checked.append(to_check)

                cont_planes[ref_coord] = list(set(continuous))
    return cont_planes


def cont_map(heightmap: np.ndarray,
             cont_planes: dict[tuple[int, ...], list[tuple[int, ...]]]):
    cont_map = np.zeros(heightmap.shape)
    for i, k in enumerate(cont_planes):
        for coord in cont_planes[k]:
            cont_map[coord[0], coord[1]] = i

    return cont_map
