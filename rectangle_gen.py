import random

from gdpc.vector_tools import Rect  # type: ignore


def random_rectangle(points: set[tuple[int, ...]],
                     size_range: tuple[int, int]) -> Rect:
    x_size = random.randint(size_range[0], size_range[1])
    z_size = random.randint(size_range[0], size_range[1])

    offset = random.choice(list(points))

    return Rect(offset, (x_size, z_size))


def is_rect_in_plane(rect: Rect, plane: set[tuple[int, ...]],
                     margin: int) -> bool:
    rect.offset -= (margin, margin)
    rect.size += (margin*2, margin*2)
    for point in rect.inner:
        if tuple(point) not in plane:
            return False

    return True


def choose_rectangle(plane: set[tuple[int, ...]],
                     size_range: tuple[int, int]) -> Rect:
    rect = random_rectangle(plane, size_range)
    print(f"Generated rectangle {rect}")
    while not is_rect_in_plane(rect, plane, margin=1):
        rect = random_rectangle(plane, size_range)
        print(f"Generated rectangle {rect}")

    return rect
