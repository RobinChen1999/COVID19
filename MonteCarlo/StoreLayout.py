import tkinter as tk
from tkinter import ttk
import io
from PIL import Image, ImageGrab


class StoreLayout:
    color_floor = "white"
    color_shelf = "black"
    canvas_width = 400
    step = int(canvas_width / 20)

    def __init__(self, frame):
        # create canvas
        self.canvas = tk.Canvas(frame, bg=self.color_floor,
                                width=self.canvas_width,
                                height=self.canvas_width)
        self.canvas.bind('<B1-Motion>', self.onCanvasDrag)
        self.canvas.bind('<Button-1>', self.onCanvasClick)
        self.canvas.pack()

        # button to show/hide the grid
        self.show_grid = tk.IntVar()
        self.btn_grid = ttk.Checkbutton(frame,
                                        text="Show Grid",
                                        variable=self.show_grid,
                                        onvalue=1, offvalue=0,
                                        command=self.hide_grid_lines)
        self.btn_grid.pack()

        btn_clear_shelves = ttk.Button(frame,
                                       text="Remove all shelves",
                                       command=self.clear_shelves)
        btn_clear_shelves.pack()

        # init col row
        self.click_row = 0
        self.click_col = 0

        # init entrance/exit
        self.nexits = 0
        self.cashierd = 0

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
        else:
            pass

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
        ps = self.canvas.postscript(colormode="mono", pageheight='101', pagewidth='101')
        # grab postscript from IO and 
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        img = img.transpose(Image.FLIP_TOP_BOTTOM)  # flip image
        img.save(fileName)  # save as .png

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

        self.canvas.create_rectangle(0, self.canvas_width - 5, 7, self.canvas_width, fill="red", width=0,
                                     tags="entrance")

        self.canvas.delete("exit")

        for i in range(nexits):
            x = (img_width - cashierd * i) * width_factor
            y = img_width * width_factor
            self.canvas.create_rectangle(x - 5, y - 5, x, y, fill="blue", width=0, tags="exit")
