from collections import defaultdict

import numpy as np

from gdpc.vector_tools import addY  # type: ignore


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


def sort_land_by_height(editor, heightmap: np.ndarray)\
        -> defaultdict[int, list[tuple[int, ...]]]:
    coords_with_height = defaultdict(list)

    for height in range(heightmap.min(), heightmap.max() + 1):
        for xz, y in np.ndenumerate(heightmap):
            block_name = editor.getBlock(addY(xz, y - 1)).id
            if y == height and "water" not in block_name:
                coords_with_height[y].append(xz)

    return coords_with_height


def cont_planes(world_slice,
                heightmap: np.ndarray) -> dict[tuple[int, ...],
                                               set[tuple[int, ...]]]:
    coords_with_height = sort_land_by_height(world_slice, heightmap)
    cont_planes = {}

    for height, coords in coords_with_height.items():
        print(f"Looking at height {height} with {len(coords)} coords")
        already_checked: set[tuple[int, ...]] = set()

        for ref_coord in coords:
            if ref_coord not in already_checked:
                # print(f"Checking {len(coords)} points for continuity with "
                #      f"{ref_coord} ({height} high)")
                continuous = {ref_coord}
                old_continuous: set[tuple[int, ...]] = set()
                new_continuous = continuous.copy()
                # coords.remove(ref_coord)

                while len(new_continuous) != 0:
                    for to_check in coords:
                        # print(f"Checking all in {coords}")
                        # print(f"{len(continuous)} continuous points found",
                        #       end='\r')
                        for already_cont in new_continuous:
                            # print(f"Comparing {to_check} to {already_cont}")
                            if points_are_neighbours(to_check, already_cont):
                                continuous.add(to_check)
                                already_checked.add(to_check)

                    new_continuous = continuous - old_continuous
                    old_continuous = continuous.copy()

                cont_planes[ref_coord] = continuous
    return cont_planes


def largest_plane(cont_planes: dict[tuple[int, ...],
                            set[tuple[int, ...]]]):
    max_size = 0
    largest: set[tuple[int, ...]] = set()

    for ref_coord, points in cont_planes.items():
        if len(points) > max_size:
            max_size = len(points)
            largest = points

    return largest


def cont_map(heightmap: np.ndarray,
             cont_planes: dict[tuple[int, ...], set[tuple[int, ...]]])\
        -> np.ndarray:
    cont_map = np.full(heightmap.shape, -10)
    for i, k in enumerate(cont_planes):
        for coord in cont_planes[k]:
            cont_map[coord[0], coord[1]] = i

    return cont_map


def plane_map(heightmap: np.ndarray, plane: set[tuple[int, ...]]):
    plane_map = np.full(heightmap.shape, -10)
    for (x, z) in plane:
        plane_map[x][z] = 10

    return plane_map


def plane_height(plane, heightmap):
    a_point = list(plane)[0]
    plane_height = heightmap[a_point[0]][a_point[1]]

    return plane_height
