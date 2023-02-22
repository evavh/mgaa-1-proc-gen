#!/usr/bin/env python3

import sys

import numpy as np
from matplotlib import pyplot as plt  # type: ignore

from gdpc import Editor, Box  # type: ignore
from gdpc.exceptions import (  # type: ignore
    InterfaceConnectionError, BuildAreaNotSetError)

import plane_detection


def plot_hm(heightmap: np.ndarray, filename: str):
    plt.imshow(heightmap)
    plt.colorbar()
    plt.savefig("plots/" + filename)
    plt.clf()


if __name__ == '__main__':
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

    print("Loading world slice...")
    world_slice = editor.loadWorldSlice(build_area.toRect())
    print("World slice loaded!")

    heightmap = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    cont_planes = plane_detection.cont_planes(heightmap)

    cont_map = plane_detection.cont_map(heightmap, cont_planes)
    plot_hm(cont_map, "cont_map.png")
    plot_hm(heightmap, "heightmap.png")
