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


def place_fence(editor: Editor, rect_global: Rect, dir: str, y: int):
    x_min, x_max, z_min, z_max = get_corners(rect_global)
    block = Block("minecraft:dark_oak_fence")

    print(f"Placing {dir} fence at {get_corners(rect_global)} {y + 1}")

    if dir == 'south':
        # line from x_min to x_max at z_max
        placeLine(editor, (x_min, y + 1, z_max - 1),
                  (x_max - 1, y + 1, z_max - 1), block)
        # x_min, z_max - 1 and x_max, z_max - 1
        editor.placeBlockGlobal((x_min, y + 1, z_max - 2), block)
        editor.placeBlockGlobal((x_max - 1, y + 1, z_max - 2), block)
    elif dir == 'north':
        # line from x_min to x_max at z_min
        placeLine(editor, (x_min, y + 1, z_min),
                  (x_max - 1, y + 1, z_min), block)
        # x_min, z_min + 1 and x_max, z_min + 1
        editor.placeBlockGlobal((x_min, y + 1, z_min + 1), block)
        editor.placeBlockGlobal((x_max - 1, y + 1, z_min + 1), block)
    elif dir == 'east':
        # line from z_min to z_max at x_max
        placeLine(editor, (x_max - 1, y + 1, z_min),
                  (x_max - 1, y + 1, z_max - 1), block)
        # x_max - 1, z_min and x_max - 1, z_max
        editor.placeBlockGlobal((x_max - 2, y + 1, z_min), block)
        editor.placeBlockGlobal((x_max - 2, y + 1, z_max - 1), block)
    elif dir == 'west':
        # line from z_min to z_max at x_min
        placeLine(editor, (x_min, y + 1, z_min),
                  (x_min, y + 1, z_max - 1), block)
        # x_min + 1, z_min and x_min + 1, z_max
        editor.placeBlockGlobal((x_min + 1, y + 1, z_min), block)
        editor.placeBlockGlobal((x_min + 1, y + 1, z_max - 1), block)


def get_house_rect(main_rect_global: Rect, facing_dirs: list[str]) -> Rect:
    house_rect = Rect(main_rect_global.offset, main_rect_global.size)

    house_rect.size -= (2, 2)
    # directions where there are fences
    for dir in facing_dirs[:2]:
        print(f"Adjusting for dir {dir}")
        if dir == 'north':
            house_rect.offset += (0, 2)
        if dir == 'west':
            house_rect.offset += (2, 0)

    return house_rect


def place_log_outline(editor: Editor, main_rect_global: Rect,
                      facing_dirs: list[str],
                      y: int):
    BLOCK_TYPE = "minecraft:spruce_log"

    house_rect = get_house_rect(main_rect_global, facing_dirs)
    house_rect.size -= (1, 1)
    x_min, x_max, z_min, z_max = get_corners(house_rect)

    # z_min to z_max logs
    block = Block(BLOCK_TYPE, {"axis": "z"})
    placeLine(editor, (x_min, y, z_min), (x_min, y, z_max), block)
    placeLine(editor, (x_max, y, z_min), (x_max, y, z_max), block)

    # x_min to x_max logs
    block = Block(BLOCK_TYPE, {"axis": "x"})
    placeLine(editor, (x_min, y, z_min), (x_max, y, z_min), block)
    placeLine(editor, (x_min, y, z_max), (x_max, y, z_max), block)

    # corners
    block = Block(BLOCK_TYPE, {"axis": "y"})
    for corner in house_rect.corners:
        editor.placeBlockGlobal(addY(corner, y), block)


def add_to_facing_dirs(facing_dirs):
    if len(facing_dirs) == 0:
        facing_dirs=['south', 'west']
    elif len(facing_dirs) == 1:
        if facing_dirs[0] == 'south':
            facing_dirs[1] == 'west'
        elif facing_dirs[0] == 'north':
            facing_dirs[1] == 'west'
        else:
            facing_dirs[1] == 'south'

    return facing_dirs


def build_house(editor: Editor, build_area, largest_plane, y):
    IDEAL_SIZE=(10, 8)
    MARGIN=1

    last_dim_decreased=1
    main_rect=None
    size=(IDEAL_SIZE[0] + 1, IDEAL_SIZE[1])

    while main_rect is None:
        size, last_dim_decreased=decrease_size(size, last_dim_decreased)
        print(f"Trying to find fitting {size} rectangle")
        main_rect=rectangle_gen.choose_rectangle(largest_plane, size, MARGIN)

    main_rect_global=Rect(main_rect.offset, main_rect.size)
    main_rect_global.offset += (build_area.offset.x, build_area.offset.z)

    facing_dirs=getOptimalFacingDirection(editor,
                                            addY(main_rect_global.center, y+1))
    facing_dirs=add_to_facing_dirs(facing_dirs)

    print(f"Placing foundation at {main_rect_global}")
    placeRect(editor, main_rect_global, y,
              Block("minecraft:dark_oak_planks"))

    print(f"House should be facing {facing_dirs}")

    place_fence(editor, main_rect_global, facing_dirs[0], y)
    place_fence(editor, main_rect_global, facing_dirs[1], y)

    for y in range(y + 1, y + 4):
        place_log_outline(editor, main_rect_global, facing_dirs, y)
