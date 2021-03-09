import tkinter as tk
import numpy as np

class StoreLayout:
    def __init__(self, frame):
        self.canvas_scale = 500
        self.step = int(self.canvas_scale / 10)
        self.canvas = tk.Canvas (frame, bg="blue", width=self.canvas_scale, height=self.canvas_scale)
        self.canvas.bind('<Button-1>', self.onCanvasClick)
        self.canvas.pack()

    # draws all elements in the canvas
    def draw_store_layout(self):
        self.create_grid()
        self.draw_grid_lines()        

    # draws black lines to show the grid
    def draw_grid_lines(self):
        for i in range(self.step, self.canvas_scale, self.step):
            # horizontal line
            self.canvas.create_line(0, i, self.canvas_scale, i)
            # vertical line
            self.canvas.create_line(i, 0, i, self.canvas_scale)

    # creates a matrix of rectangle objects grid[row][column]
    def create_grid(self):
        self.grid = []
        for row in range(0, self.step):
            x0 = row * self.step
            x1 = x0 + self.step
            column = []
            for col in range(0, self.step):
                y0 = col * self.step
                y1 = y0 + self.step
                column.append(self.canvas.create_rectangle(x0, y0, x1, y1, fill="green"))
            self.grid.append(column)

    # changes colour of rectangle object from grid
    def draw_shelf(self, row, col):
        self.canvas.itemconfigure(self.grid[row][col], fill="pink")

    # onClick event on canvas
    def onCanvasClick(self, event):
        row = int(event.x / self.step)
        col = int(event.y / self.step)
        self.draw_shelf(row=row, col=col)


