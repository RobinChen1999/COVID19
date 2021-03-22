import tkinter as tk
import io
from PIL import Image, ImageGrab

class StoreLayout:
    color_floor = "white"
    color_shelf = "black"
    canvas_width = 200
    step = int(canvas_width / 10)

    def __init__(self, frame):
        # create canvas
        self.canvas = tk.Canvas (frame, bg=self.color_floor, 
                                    width=self.canvas_width, 
                                    height=self.canvas_width)
        self.canvas.bind('<B1-Motion>', self.onCanvasDrag)
        self.canvas.bind('<Button-1>', self.onCanvasClick)
        self.canvas.pack()

        # button to show/hide the grid
        self.show_grid = tk.IntVar()
        self.btn_grid = tk.Checkbutton(frame,
                                text="Show Grid", 
                                variable=self.show_grid, 
                                onvalue=1, offvalue=0, 
                                command=self.hide_grid_lines)
        self.btn_grid.pack()

        # init col row
        self.click_row = 0
        self.click_col = 0

        
        
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
        self.btn_grid.deselect()
        self.hide_grid_lines()
        
        # create postscript image from canvas
        ps = self.canvas.postscript(colormode="mono", pageheight='101', pagewidth='101')
        # grab postscript from IO and 
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        img = img.transpose(Image.FLIP_TOP_BOTTOM)              # flip image
        img.save(fileName)                                      # save as .png

        return str(fileName)


