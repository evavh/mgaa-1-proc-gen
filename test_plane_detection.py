import numpy as np
from plane_detection import points_are_neighbours, cont_planes


def test_neighbours_same_point():
    assert not points_are_neighbours((100, 30), (100, 30))


def test_neighbours_x_one_off():
    assert points_are_neighbours((101, 30), (100, 30))


def test_neighbours_y_one_off():
    assert points_are_neighbours((100, 30), (100, 31))


def test_neighbours_x_two_off():
    assert not points_are_neighbours((102, 30), (100, 30))


def test_cont_map_of_small_hm():
    heightmap = np.array([[3, 3, 3],
                          [3, 3, 2],
                          [1, 3, 2]])
    print('\n', heightmap)
    print(cont_planes(heightmap))
