from gdpc import Block  # type: ignore
from gdpc.editor import Editor  # type: ignore
from gdpc.geometry import placeRectOutline, placeRect, placeLine  # type: ignore
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


def get_corners(rect: Rect):
    x_corners = []
    z_corners = []

    for corner in rect.corners:
        print(corner)
        x_corners.append(corner[0])
        z_corners.append(corner[1])

    x_min = min(x_corners)
    x_max = max(x_corners)
    z_min = min(z_corners)
    z_max = max(z_corners)

    return x_min, x_max, z_min, z_max


def place_fence(editor: Editor, rect: Rect, dir: str, y: int):
    x_min, x_max, z_min, z_max = get_corners(rect)
    block = Block("minecraft:dark_oak_fence")

    print(f"Placing {dir} fence at {get_corners(rect)} {y}")

    if dir == 'south':
        # line from x_min to x_max at z_max
        placeLine(editor, (x_min, y + 1, z_max), (x_max, y + 1, z_max), block)
        # x_min, z_max - 1 and x_max, z_max - 1
        editor.placeBlock((x_min, y + 1, z_max - 1), block)
        editor.placeBlock((x_max, y + 1, z_max - 1), block)
        return
    elif dir == 'north':
        # line from x_min to x_max at z_min
        placeLine(editor, (x_min, y + 1, z_min), (x_max, y + 1, z_min), block)
        # x_min, z_min + 1 and x_max, z_min + 1
        editor.placeBlock((x_min, y + 1, z_min + 1), block)
        editor.placeBlock((x_max, y + 1, z_min + 1), block)
        return
    elif dir == 'east':
        # line from z_min to z_max at x_max
        placeLine(editor, (x_max, y + 1, z_min), (x_max, y + 1, z_max), block)
        # x_max - 1, z_min and x_max - 1, z_max
        editor.placeBlock((x_max - 1, y + 1, z_min), block)
        editor.placeBlock((x_max - 1, y + 1, z_max), block)
        return
    elif dir == 'west':
        # line from z_min to z_max at x_min
        placeLine(editor, (x_min, y + 1, z_min), (x_min, y + 1, z_max), block)
        # x_min + 1, z_min and x_min + 1, z_max
        editor.placeBlock((x_min + 1, y + 1, z_min), block)
        editor.placeBlock((x_min + 1, y + 1, z_max), block)
        return


def add_to_facing_dirs(facing_dirs):
    if len(facing_dirs) == 0:
        facing_dirs = ['south', 'west']
    elif len(facing_dirs) == 1:
        if facing_dirs[0] == 'south':
            facing_dirs[1] == 'west'
        elif facing_dirs[0] == 'north':
            facing_dirs[1] == 'west'
        else:
            facing_dirs[1] == 'south'

    return facing_dirs


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

    main_rect_global = Rect(main_rect.offset, main_rect.size)
    main_rect_global.offset += (build_area.offset.x, build_area.offset.z)

    facing_dirs = getOptimalFacingDirection(editor,
                                            addY(main_rect.center, y+1))
    facing_dirs = add_to_facing_dirs(facing_dirs)

    print(f"Placing foundation at {main_rect_global}")
    # placeRect(editor, main_rect_global, y, Block("minecraft:dark_oak_planks"))

    print(f"House should be facing {facing_dirs}")

    place_fence(editor, main_rect, facing_dirs[0], y)
    place_fence(editor, main_rect, facing_dirs[1], y)
