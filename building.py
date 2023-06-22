import random

from gdpc import Block  # type: ignore
from gdpc.editor import Editor  # type: ignore
from gdpc.geometry import placeRectOutline, placeRect, placeLine  # type: ignore
from gdpc.vector_tools import Rect, addY  # type: ignore
from gdpc.editor_tools import getOptimalFacingDirection  # type: ignore
from glm import ivec2, ivec3


import rectangle_gen

FLOOR_BLOCK = "minecraft:dark_oak_planks"
FENCE_BLOCK = "minecraft:dark_oak_fence"
WALL_BLOCK = "minecraft:spruce_log"
WINDOW_BLOCK = "minecraft:glass_pane"
DOOR_BLOCK = "minecraft:birch_door"
GATE_BLOCK = "minecraft:dark_oak_fence_gate"
STAIRS_BLOCK = "minecraft:dark_oak_stairs"


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
    block = Block(FENCE_BLOCK)

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


def place_log_outline(editor: Editor, house_rect: Rect,
                      y: int):

    x_min, x_max, z_min, z_max = get_corners(house_rect)

    # z_min to z_max logs
    block = Block(WALL_BLOCK, {"axis": "z"})
    placeLine(editor, (x_min, y, z_min), (x_min, y, z_max), block)
    placeLine(editor, (x_max, y, z_min), (x_max, y, z_max), block)

    # x_min to x_max logs
    block = Block(WALL_BLOCK, {"axis": "x"})
    placeLine(editor, (x_min, y, z_min), (x_max, y, z_min), block)
    placeLine(editor, (x_min, y, z_max), (x_max, y, z_max), block)

    # corners
    block = Block(WALL_BLOCK, {"axis": "y"})
    for corner in house_rect.corners:
        editor.placeBlockGlobal(addY(corner, y), block)


def place_windows(editor: Editor, house_rect: Rect,
                  y: int):
    block = Block(WINDOW_BLOCK)

    x_min, x_max, z_min, z_max = get_corners(house_rect)
    half_dx = (x_max - x_min) // 2 + 1
    half_dz = (z_max - z_min) // 2 + 1

    for x in range(x_min + 2, x_min + half_dx, 2):
        editor.placeBlockGlobal((x, y, z_min), block)
        editor.placeBlockGlobal((x, y, z_max), block)

    for x in range(x_max - 2, x_max - half_dx, -2):
        editor.placeBlockGlobal((x, y, z_min), block)
        editor.placeBlockGlobal((x, y, z_max), block)

    for z in range(z_min + 2, z_min + half_dz, 2):
        editor.placeBlockGlobal((x_min, y, z), block)
        editor.placeBlockGlobal((x_max, y, z), block)

    for z in range(z_max - 2, z_max - half_dz, -2):
        editor.placeBlockGlobal((x_min, y, z), block)
        editor.placeBlockGlobal((x_max, y, z), block)


def place_door(editor: Editor, house_rect: Rect, facing_dirs: list[str],
               y: int) -> bool:
    secondary_dir = facing_dirs[1]

    x_min, x_max, z_min, z_max = get_corners(house_rect)
    half_dx = (x_max - x_min) // 2
    half_dz = (z_max - z_min) // 2

    print(f"Trying to place door on dir {secondary_dir}")
    if secondary_dir == 'south' or secondary_dir == 'north':
        # line from x_min to x_max at z_max or z_min
        x_options = list(range(x_min + 2, x_min + half_dx, 2))
        x_options.extend(list(range(x_max - 2, x_max - half_dx, 2)))

        wall_block = Block(WALL_BLOCK, {"axis": "x"})
    elif secondary_dir == 'east' or secondary_dir == 'west':
        # line from z_min to z_max at x_max or x_min
        z_options = list(range(z_min + 2, z_min + half_dz, 2))
        z_options.extend(list(range(z_max - 2, z_max - half_dz, 2)))

        wall_block = Block(WALL_BLOCK, {"axis": "z"})

    if secondary_dir == 'south':
        z_options = [z_max]
        facing = 'north'
        gate_offset = ivec3(0, 0, 2)
    if secondary_dir == 'north':
        z_options = [z_min]
        facing = 'south'
        gate_offset = ivec3(0, 0, -2)
    if secondary_dir == 'east':
        x_options = [x_max]
        facing = 'west'
        gate_offset = ivec3(2, 0, 0)
    if secondary_dir == 'west':
        x_options = [x_min]
        facing = 'east'
        gate_offset = ivec3(-2, 0, 0)

    door_block = Block(DOOR_BLOCK, {"facing": facing})

    print(f"x_options: {x_options}, z_options: {z_options}")
    if len(x_options) == 0 or len(z_options) == 0:
        return False

    x = random.choice(x_options)
    z = random.choice(z_options)
    door_coords = ivec3(x, y + 1, z)
    print(f"Placing door at {door_coords}")
    print(door_coords + ivec3(0, 2, 0))
    editor.placeBlockGlobal(door_coords + ivec3(0, 2, 0), wall_block)
    editor.placeBlockGlobal(door_coords, door_block)

    gate_coords = door_coords + gate_offset
    stairs_coords = gate_coords + ivec3(0, -1, 0)

    gate_block = Block(GATE_BLOCK, {"facing": facing})
    stairs_block = Block(STAIRS_BLOCK, {"facing": facing})
    editor.placeBlockGlobal(gate_coords, gate_block)
    editor.placeBlockGlobal(stairs_coords, stairs_block)

    return True


def opposite_of_dir(dir):
    if dir == 'north':
        return 'south'
    if dir == 'east':
        return 'west'
    if dir == 'west':
        return 'east'
    if dir == 'south':
        return 'north'


def build_roof(editor, house_rect, y_floor):
    # Roof
    # get short side line
    # iterate over it, placing logs one less wide on each side
    # (for both short sides)
    # until 2 (even) or 3 (odd) wide

    x_min, x_max, z_min, z_max = get_corners(house_rect)

    x_lines = [[ivec2(x_min, z_min), ivec2(x_max, z_min)], [
        ivec2(x_min, z_max), ivec2(x_max, z_max)]]
    z_lines = [[ivec2(x_min, z_min), ivec2(x_min, z_max)], [
        ivec2(x_max, z_min), ivec2(x_max, z_max)]]

    x_lines_long = [[ivec2(x_min - 1, z_min), ivec2(x_max + 1, z_min)], [
        ivec2(x_min - 1, z_max), ivec2(x_max + 1, z_max)]]
    z_lines_long = [[ivec2(x_min, z_min - 1), ivec2(x_min, z_max + 1)], [
        ivec2(x_max, z_min - 1), ivec2(x_max, z_max + 1)]]

    if house_rect.size[0] < house_rect.size[1]:
        dir = 'east'
        axis = 'x'
        short_lines = x_lines
        long_lines = z_lines_long
        roof_width = x_max - x_min
        reduction_step = ivec3(1, 0, 0)
        cur_width_red = ivec3(1, 0, 0)
        cur_length_red = ivec3(-1, 0, 0)
    if house_rect.size[0] >= house_rect.size[1]:
        dir = 'north'
        axis = 'z'
        short_lines = z_lines
        long_lines = x_lines_long
        roof_width = z_max - z_min
        reduction_step = ivec3(0, 0, 1)
        cur_width_red = ivec3(0, 0, 1)
        cur_length_red = ivec3(0, 0, -1)

    roof_wall_block = Block(WALL_BLOCK, {"axis": axis})

    y_roof = y_floor + 5
    roof_height = roof_width // 2 - 2
    if roof_height < 2:
        roof_height = 2

    for cur_y in range(y_roof, y_roof + roof_height):
        for line in short_lines:
            placeLine(editor,
                      addY(line[0], cur_y) + cur_width_red,
                      addY(line[1], cur_y) - cur_width_red,
                      roof_wall_block)
        cur_width_red += reduction_step

    # iterate over short side width + y, starting at y_floor + 5
    # place line of stairs, first birch then dark oak until at y of top
    # place oak blocks at same level as top stairs
    for cur_y in range(y_roof - 1, y_roof + roof_height + 1):
        # first line: toward z_max
        line = long_lines[0]
        roof_block = Block(STAIRS_BLOCK, {"facing": opposite_of_dir(dir)})
        placeLine(editor,
                  addY(line[0], cur_y) + cur_length_red,
                  addY(line[1], cur_y) + cur_length_red,
                  roof_block)

        # second line: toward z_min
        line = long_lines[1]
        roof_block = Block(STAIRS_BLOCK, {"facing": dir})
        placeLine(editor,
                  addY(line[0], cur_y) - cur_length_red,
                  addY(line[1], cur_y) - cur_length_red,
                  roof_block)

        cur_length_red += reduction_step

    ceiling_block = Block(FLOOR_BLOCK)

    placeLine(editor,
              addY(long_lines[0][0], y_roof + roof_height) + cur_length_red,
              addY(long_lines[0][1], y_roof + roof_height) + cur_length_red,
              ceiling_block)

    placeLine(editor,
              addY(long_lines[1][0], y_roof + roof_height) - cur_length_red,
              addY(long_lines[1][1], y_roof + roof_height) - cur_length_red,
              ceiling_block)


def add_to_facing_dirs(facing_dirs):
    if len(facing_dirs) == 0:
        facing_dirs = ['south', 'west']
    elif len(facing_dirs) == 1:
        if facing_dirs[0] == 'south':
            facing_dirs.append('west')
        elif facing_dirs[0] == 'north':
            facing_dirs.append('west')
        else:
            facing_dirs.append('south')

    return facing_dirs


def build_interior(editor, house_rect, y_floor):
    print(house_rect)

    editor.placeBlockGlobal(
        addY(house_rect.offset + (1, 2), y_floor+1), Block("minecraft:green_bed"))
    editor.placeBlockGlobal(
        addY(house_rect.offset + (2, 1), y_floor+1), Block("minecraft:torch"))
    editor.placeBlockGlobal(
        addY(house_rect.offset + house_rect.size - (1, 1), y_floor+1),
        Block("minecraft:bookshelf"))


def build_house(editor: Editor, build_area, largest_plane, y_floor):
    IDEAL_SIZE = (12, 10)
    MARGIN = 1

    last_dim_decreased = 1
    main_rect = None
    size = (IDEAL_SIZE[0] + 1, IDEAL_SIZE[1])

    while main_rect is None:
        if size[0] < 7 or size[1] < 7:
            print("No suitable area found")
            exit(1)
        size, last_dim_decreased = decrease_size(size, last_dim_decreased)
        print(f"Trying to find fitting {size} rectangle")
        main_rect = rectangle_gen.choose_rectangle(largest_plane, size, MARGIN)

    main_rect_global = Rect(main_rect.offset, main_rect.size)
    main_rect_global.offset += (build_area.offset.x, build_area.offset.z)

    facing_dirs = getOptimalFacingDirection(editor,
                                            addY(main_rect_global.center, y_floor+1))
    facing_dirs = add_to_facing_dirs(facing_dirs)

    print(f"Placing foundation at {main_rect_global}")
    placeRect(editor, main_rect_global, y_floor,
              Block(FLOOR_BLOCK))

    print(f"House should be facing {facing_dirs}")

    place_fence(editor, main_rect_global, facing_dirs[0], y_floor)
    place_fence(editor, main_rect_global, facing_dirs[1], y_floor)

    house_rect = get_house_rect(main_rect_global, facing_dirs)
    # working with inclusive coordinates
    house_rect.size -= (1, 1)

    for y in range(y_floor + 1, y_floor + 5):
        place_log_outline(editor, house_rect, y)

    for y in range(y_floor + 2, y_floor + 4):
        place_windows(editor, house_rect, y)

    if not place_door(editor, house_rect, facing_dirs, y_floor):
        facing_dirs2 = facing_dirs.copy()
        facing_dirs2[1] = facing_dirs[0]
        place_door(editor, house_rect, facing_dirs2, y_floor)

    build_roof(editor, house_rect, y_floor)
    build_interior(editor, house_rect, y_floor)
