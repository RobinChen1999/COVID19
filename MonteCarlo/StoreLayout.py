import tkinter as tk

class StoreLayout:
    def __init__(self, frame):
        self.canvas_scale = 500
        self.step = int(self.canvas_scale / 10)
        self.canvas = tk.Canvas (frame, bg="blue", width=self.canvas_scale, height=self.canvas_scale)
        self.canvas.pack()

    def draw_store_layout(self):
        self.draw_grid()
        self.draw_shelf(3, 4)
        

    def draw_grid(self):
        for i in range(self.step, self.canvas_scale, self.step):
            # horizontal line
            self.canvas.create_line(0, i, self.canvas_scale, i)
            # vertical line
            self.canvas.create_line(i, 0, i, self.canvas_scale)

    def draw_shelf(self, col, row):
        x0 = col * self.step
        y0 = row * self.step
        x1 = x0 + self.step
        y1 = y0 + self.step
        self.canvas.create_rectangle(x0, y0, x1, y1, fill="black")

