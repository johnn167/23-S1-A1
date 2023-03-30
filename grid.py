from __future__ import annotations
from layer_store import *
from referential_array import ArrayR


class Grid(LayerStore):
    DRAW_STYLE_SET = "SET"
    DRAW_STYLE_ADD = "ADD"
    DRAW_STYLE_SEQUENCE = "SEQUENCE"
    DRAW_STYLE_OPTIONS = (
        DRAW_STYLE_SET,
        DRAW_STYLE_ADD,
        DRAW_STYLE_SEQUENCE
    )

    DEFAULT_BRUSH_SIZE = 2
    MAX_BRUSH = 5
    MIN_BRUSH = 0
    MIN_CAPACITY = 1

    def __init__(self, draw_style, x, y) -> None:
        """
        Initialise the grid object.
        - draw_style:
            The style with which colours will be drawn.
            Should be one of DRAW_STYLE_OPTIONS
            This draw style determines the LayerStore used on each grid square.
        - x, y: The dimensions of the grid.

        Should also intialise the brush size to the DEFAULT provided as a class variable.
        """

        LayerStore.__init__(self)
        self.grid = ArrayR(max(self.MIN_CAPACITY, x))
        for i in range(len(self.grid)):
            self.grid[i] = ArrayR(max(self.MIN_CAPACITY, y))

        if draw_style == self.DRAW_STYLE_SET:
            layer_store = SetLayerStore()
        elif draw_style == self.DRAW_STYLE_ADD:
            layer_store = AdditiveLayerStore()
        elif draw_style == self.DRAW_STYLE_SEQUENCE:
            layer_store = SequenceLayerStore()

        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                self.grid[i][j] = layer_store()

        self.brush_size = self.DEFAULT_BRUSH_SIZE

    def __getitem__(self, index: tuple):
        x, y = index
        return self.grid[x][y]

    def increase_brush_size(self):
        """
        Increases the size of the brush by 1,
        if the brush size is already MAX_BRUSH,
        then do nothing.
        """
        if self.brush_size < self.MAX_BRUSH:
            self.brush_size += 1
        # raise NotImplementedError()

    def decrease_brush_size(self):
        """
        Decreases the size of the brush by 1,
        if the brush size is already MIN_BRUSH,
        then do nothing.
        """
        if self.brush_size > self.MIN_BRUSH:
            self.brush_size -= 1
        # raise NotImplementedError()

    def special(self):
        """
        Activate the special affect on all grid squares.
        """
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                self.grid[i][j].special()


affected_grid_square: tuple[int, int]
grid: Grid
sq = grid[self.affected_grid_square[0]][self.affected_grid_square[1]]
