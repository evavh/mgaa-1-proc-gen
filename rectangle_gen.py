import random

from gdpc.vector_tools import Rect  # type: ignore


def random_rectangles(points: set[tuple[int, ...]],
                      size: tuple[int, int]) -> list[Rect]:
    random.shuffle(list(points))
    rectangles = [Rect((0, 0), (1, 1))] * (len(points) * 2)
    for i, offset in enumerate(points):
        rectangles[2 * i] = Rect(offset, size)
        rectangles[2 * i + 1] = Rect(offset, (size[1], size[0]))

    return rectangles


def is_rect_in_plane(rect: Rect, plane: set[tuple[int, ...]],
                     margin: int) -> bool:
    offset = rect.offset - (margin, margin)
    size = rect.size + (margin*2, margin*2)
    to_try = Rect(offset, size)
    for point in to_try.inner:
        if tuple(point) not in plane:
            return False

    return True


def choose_rectangle(plane: set[tuple[int, ...]],
                     size: tuple[int, int]) -> Rect:
    rects = random_rectangles(plane, size)
    for rect in rects:
        if is_rect_in_plane(rect, plane, margin=1):
            return rect

    raise Exception(f"No valid rectangle of size {size} found")
