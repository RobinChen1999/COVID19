import tkinter as tk
from tkinter import messagebox
from PIL import Image
import io


class StoreLayout:
    color_floor = "white"
    color_shelf = "black"
    canvas_width = 600
    step = int(canvas_width / 20)

    def __init__(self, frame):
        # create canvas
        self.canvas = tk.Canvas(frame, bg=self.color_floor,
                                width=self.canvas_width,
                                height=self.canvas_width)
        self.canvas.bind('<B1-Motion>', self.onCanvasDrag)
        self.canvas.bind('<Button-1>', self.onCanvasClick)
        self.canvas.grid(row=1, column=0, columnspan=2)

        # # button to show/hide the grid
        self.show_grid = tk.IntVar(value=1)

        # init col row
        self.click_row = 0
        self.click_col = 0

        # init entrance/exit
        self.nexits = 0
        self.cashierd = 0

        # draw init layout
        self.draw_initial_layout()

    # draws all elements in the canvas
    def draw_store_layout(self):
        self.draw_grid_lines()
        self.hide_grid_lines()

    # draws black lines to show the grid
    def draw_grid_lines(self):
        for i in range(self.step, self.canvas_width, self.step):
            # horizontal line
            self.canvas.create_line(0, i, self.canvas_width, i, tags=("grid_lines"))
            # vertical line
            self.canvas.create_line(i, 0, i, self.canvas_width, tags=("grid_lines"))

    def hide_grid_lines(self):
        if self.show_grid.get() == 0:
            self.canvas.itemconfigure("grid_lines", state="hidden")
        elif self.show_grid.get() == 1:
            self.canvas.itemconfigure("grid_lines", state="normal")

    def clear_shelves(self):
        result = tk.messagebox.askquestion("Warning!", "Are you sure you want to remove all shelves?")
        if result == "yes":
            self.canvas.delete('shelf')

    # changes colour of rectangle object from grid
    def draw_shelf(self, row, col):
        x0 = row * self.step
        x1 = x0 + self.step
        y0 = col * self.step
        y1 = y0 + self.step
        shelf = self.canvas.create_rectangle(x0, y0, x1, y1, fill=self.color_shelf, width=0, tags=("shelf"))

    # draws shelf when clicked on the canvas and when drawing tool selected
    def onCanvasDrag(self, event):
        new_row = int(event.x / self.step)
        new_col = int(event.y / self.step)
        if new_row != self.click_row or new_col != self.click_col:
            self.click_row = new_row
            self.click_col = new_col
            self.onCanvasClick(event=event)

    # draws shelf when clicked on the canvas and when drawing tool selected
    def onCanvasClick(self, event):
        row = int(event.x / self.step)
        col = int(event.y / self.step)
        # if there is a shelf, delete it
        if event.widget.find_withtag('current&&shelf'):
            self.canvas.delete(event.widget.find_withtag('current&&shelf')[0])
        # else, draw a shelf
        else:
            self.draw_shelf(row=row, col=col)

    # save the canvas as .png and return its file name
    def saveCanvas(self):
        fileName = "storeMap.png"
        preMadeLayout = "ExampleSuperMarket.pbm"

        # remove grid before saving
        self.show_grid.set(0)
        self.hide_grid_lines()

        # Remove entrance and exits
        self.canvas.delete("entrance")
        self.canvas.delete("exit")

        # create postscript image from canvas
        ps = self.canvas.postscript(colormode="mono")           
        img = Image.open(io.BytesIO(ps.encode('utf-8')))        # grab postscript from IO
        img = img.transpose(Image.FLIP_TOP_BOTTOM)              # flip image because it is flipped again in the simulation
        img = img.resize((20, 20), resample=Image.NEAREST)      # scale down so shelf size == pixel size
        img = img.resize((100,100),resample=Image.NEAREST)      # scale up to the size needed for input simulation
        img.save(fileName)                                      # save as .png

        # Restore entrance and exits
        self.draw_entrance_exits(self.nexits, self.cashierd)
        return str(fileName)

    def check_store_empty(self):
        if self.canvas.find_withtag("shelf"):
            return False    # store not empty
        else:
            return True     # store is empty

    def draw_entrance_exits(self, nexits, cashierd):
        self.nexits = nexits
        self.cashierd = cashierd

        img_width = 101
        width_factor = self.canvas_width / img_width

        self.canvas.create_rectangle(0, self.canvas_width - 5, 12, self.canvas_width + 5, fill="red", width=0,
                                     tags="entrance")

        self.canvas.delete("exit")

        for i in range(nexits):
            x = (img_width - cashierd * i) * width_factor
            y = img_width * width_factor
            self.canvas.create_rectangle(x - 12, y - 5, x, y + 5, fill="blue", width=0, tags="exit")

    def create_row_coords(self, initial_pos, is_horizontal, length):
        coords = [initial_pos]

        for i in range(length):
            if is_horizontal:
                coords.append((initial_pos[0] + i, initial_pos[1]))
            else:
                coords.append((initial_pos[0], initial_pos[1] + i))

        return coords

    def draw_initial_layout(self):
        self.canvas.delete('shelf')
        coords = []

        coords.extend(self.create_row_coords((1, 1), True, 8))
        coords.extend(self.create_row_coords((11, 1), True, 8))
        coords.extend(self.create_row_coords((1, 4), True, 8))
        coords.extend(self.create_row_coords((1, 7), True, 8))
        coords.extend(self.create_row_coords((1, 10), True, 8))
        coords.extend(self.create_row_coords((11, 4), False, 7))
        coords.extend(self.create_row_coords((18, 4), False, 7))
        coords.extend(self.create_row_coords((14, 4), True, 2))
        coords.extend(self.create_row_coords((14, 6), True, 2))
        coords.extend(self.create_row_coords((14, 8), True, 2))
        coords.extend(self.create_row_coords((14, 10), True, 2))
        coords.extend(self.create_row_coords((1, 13), True, 2))
        coords.extend(self.create_row_coords((1, 16), True, 2))
        coords.extend(self.create_row_coords((4, 13), False, 4))
        coords.extend(self.create_row_coords((6, 13), True, 3))
        coords.extend(self.create_row_coords((6, 16), True, 3))
        coords.extend(self.create_row_coords((11, 13), True, 8))
        coords.extend(self.create_row_coords((11, 16), True, 8))

        for coord in coords:
            self.draw_shelf(coord[0], coord[1])
