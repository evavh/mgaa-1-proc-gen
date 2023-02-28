import random

from gdpc.vector_tools import Rect  # type: ignore


def random_rectangle(points: set[tuple[int, ...]]) -> Rect:
    x_size = random.randint(6, 8)
    z_size = random.randint(6, 8)

    offset = random.choice(list(points))

    return Rect(offset, (x_size, z_size))


def is_rect_in_plane(rect: Rect, plane: set[tuple[int, ...]]) -> bool:
    for point in rect.inner:
        if tuple(point) not in plane:
            return False

    return True


def choose_rectangle(plane: set[tuple[int, ...]]) -> Rect:
    rect = random_rectangle(plane)
    print(f"Generated rectangle {rect}")
    while not is_rect_in_plane(rect, plane):
        rect = random_rectangle(plane)
        print(f"Generated rectangle {rect}")

    return rect
