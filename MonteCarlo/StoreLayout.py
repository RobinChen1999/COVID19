import tkinter as tk
import io
from PIL import Image, ImageGrab

class StoreLayout:
    color_floor = "white"
    color_shelf = "black"
    canvas_scale = 500
    step = int(canvas_scale / 10)

    def __init__(self, frame):
        self.canvas = tk.Canvas (frame, width=self.canvas_scale, height=self.canvas_scale)
        self.canvas.bind('<Button-1>', self.onCanvasClick)
        self.canvas.pack()

        # radio buttons to select tool
        self.tool_selec = tk.IntVar()
        toolErase = tk.Radiobutton(frame, text="Remove shelf", variable=self.tool_selec, value=0)
        toolErase.pack()
        toolDraw = tk.Radiobutton(frame, text="Draw shelf", variable=self.tool_selec, value=1)
        toolDraw.pack()
        toolDraw.select()
        

    

    # draws all elements in the canvas
    def draw_store_layout(self):
        self.create_grid()
        # self.draw_shelf(2, 9, "yellow")       

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
                column.append(self.canvas.create_rectangle(x0, y0, x1, y1, fill=self.color_floor, width=0))
            self.grid.append(column)

    # changes colour of rectangle object from grid
    def draw_shelf(self, row, col, color):
        self.canvas.itemconfigure(self.grid[row][col], fill=color)

    # onClick event on canvas
    def onCanvasClick(self, event):
        row = int(event.x / self.step)
        col = int(event.y / self.step)
        if self.tool_selec.get() == 0:
            self.draw_shelf(row=row, col=col, color=self.color_floor)
        elif self.tool_selec.get() == 1:
            self.draw_shelf(row=row, col=col, color=self.color_shelf)

    def saveCanvas(self):
        fileName = "storeMap"
        preMadeLayout = "ExampleSuperMarket.png"
        # POGING 1
        # ps = self.canvas.postscript(colormode = 'color')
        # img = Image.open(io.BytesIO(ps.encode('utf-8')))
        # img.save(fileName + '.png')

        # POGING 2
        # save postscipt image 
        # self.canvas.postscript(file = fileName + '.ps', colormode='color') 
        # # use PIL to convert to PNG 
        # img = Image.open(fileName + '.ps') 
        # img.save(fileName + '.pbm') 

        # POGING 3
        # x=self.canvas.winfo_rootx() + self.canvas.winfo_x()
        # y=self.canvas.winfo_rooty() + self.canvas.winfo_x()
        # x1=x + self.canvas_scale
        # y1=y + self.canvas_scale
        # ImageGrab.grab().crop((x,y,x1,y1)).save(fileName + ".pbm")

        # POSING 4
        # HWND = self.canvas.winfo_id()  # get the handle of the canvas
        # rect = win32gui.GetWindowRect(HWND)  # get the coordinate of the canvas
        # ImageGrab.grab(rect).save(fileName + ".png")  # get image of the current location

        return str(preMadeLayout)


