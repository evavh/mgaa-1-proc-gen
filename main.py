#!/usr/bin/env python3

import sys
from collections import defaultdict

from gdpc import Editor, Block, Box  # type: ignore
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError  # type: ignore
from gdpc import geometry
from gdpc.vector_tools import addY

import numpy as np
from matplotlib import pyplot as plt  # type: ignore


def plot_hm(heightmap: np.ndarray, filename):
    plt.imshow(heightmap)
    plt.colorbar()
    plt.savefig(filename)
    plt.clf()


def points_are_neighbours(point1, point2):
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


editor = Editor()

try:
    editor.checkConnection()
except InterfaceConnectionError:
    print("Error: Could not connect to the GDMC HTTP interface at"
          f" {editor.host}!\n")
    sys.exit(1)

try:
    build_area = editor.getBuildArea()
except BuildAreaNotSetError:
    # for seed -3875250700933304645, plains only, creative
    build_area = Box((-357, 0, -248), (101, 256, 101))

center = build_area.center
center.y = 64
build_rect = build_area.toRect()

print("Loading world slice...")
world_slice = editor.loadWorldSlice(build_area.toRect())
print("World slice loaded!")

heightmap = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
coords_with_height: defaultdict[int, list[tuple[int, ...]]] = defaultdict(list)
for height in range(heightmap.min(), heightmap.max() + 1):
    for xz, y in np.ndenumerate(heightmap):
        if y == height:
            coords_with_height[y].append(xz)

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

print(continuous_fields)

cont_map = np.zeros(heightmap.shape)
for i, k in enumerate(continuous_fields):
    for coord in continuous_fields[k]:
        cont_map[coord[0], coord[1]] = i

plot_hm(cont_map, "cont_map.png")
plot_hm(heightmap, "heightmap.png")
