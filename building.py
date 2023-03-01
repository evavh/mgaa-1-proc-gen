from gdpc import Block  # type: ignore
from gdpc.editor import Editor  # type: ignore
from gdpc.geometry import placeRectOutline, placeRect  # type: ignore
from gdpc.vector_tools import Rect, addY  # type: ignore
from gdpc.editor_tools import getOptimalFacingDirection  # type: ignore


import rectangle_gen


def build_room(editor: Editor, build_offset, rect: Rect, y: int):
    rect.offset += (build_offset.x, build_offset.z)
    print(f"Placing outline at {rect}, height {y}")
    placeRectOutline(editor, rect, y, Block("minecraft:oak_planks"))


def decrease_size(size: tuple[int, int], last_dim_decreased: int):
    if last_dim_decreased == 0:
        return (size[0], size[1] - 1), 1
    else:
        return (size[0] - 1, size[1]), 0


def build_house(editor: Editor, build_area, largest_plane, y):
    IDEAL_SIZE = (10, 8)
    MARGIN = 2

    last_dim_decreased = 1
    main_rect = None
    size = (IDEAL_SIZE[0] + 1, IDEAL_SIZE[1])

    while main_rect is None:
        size, last_dim_decreased = decrease_size(size, last_dim_decreased)
        print(f"Trying to find fitting {size} rectangle")
        main_rect = rectangle_gen.choose_rectangle(largest_plane, size, MARGIN)

    main_rect.offset += (build_area.offset.x, build_area.offset.z)
    facing_dir = getOptimalFacingDirection(editor,
                                           addY(main_rect.center, y))

    print(f"Placing foundation at {main_rect}")
    print(f"House should be facing {facing_dir}")
    placeRect(editor, main_rect, y, Block("minecraft:dark_oak_planks"))
