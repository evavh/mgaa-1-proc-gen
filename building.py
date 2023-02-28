from gdpc import Block  # type: ignore
from gdpc.editor import Editor  # type: ignore
from gdpc.geometry import placeRectOutline  # type: ignore
from gdpc.vector_tools import Rect  # type: ignore


def build_room(editor: Editor, build_offset, rect: Rect, y: int):
    rect.offset += (build_offset.x, build_offset.z)
    print(f"Placing outline at {rect}, height {y}")
    placeRectOutline(editor, rect, y, Block("minecraft:oak_planks"))
