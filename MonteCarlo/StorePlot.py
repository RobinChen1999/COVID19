from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Store import *
from Customer import *

import tkinter as tk
from PIL import Image, ImageTk

from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.tri as tri
from numpy import linspace, meshgrid
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import ListedColormap
from matplotlib import colors as cls
from matplotlib import ticker
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


class StorePlot:
    def __init__(self, store, customers, parula_map, useDiffusion, seed):
        self.store = store
        self.customers = customers
        self.parula_map = parula_map
        self.useDiffusion = useDiffusion
        self.seed = seed

    # def init_canvas(self, canvas, store_fig,height):
    #     self.canvas = canvas
    #     self.height = height
    #     self.store_fig = store_fig
    #     self.draw_customers(step=0)
        
    def init_canvas(self, window, height):
        self.height = height
        self.canvas = tk.Canvas(window, height=self.height, width=self.height)
        self.canvas.pack()
        self.store_fig = self.canvas.create_image(0, 0, anchor="nw")
        self.update_figure(value=0)
        self.draw_customers(step=0)

    def update_figure(self, value):
        image = Image.open('simFigures/simFigure_%s_%07d.png'%(self.seed, int(value)))
        self.step_img = ImageTk.PhotoImage(image.resize((int(self.height),int(self.height))))
        self.canvas.itemconfig(self.store_fig, image=self.step_img)
        self.draw_customers(step=int(value))

    def draw_customers(self, step):
        # add every cutomer to the plot,and the colour denotes infected and healthy customers
        radius = 10
        startx = -2
        starty = self.height * 0.92 - 2
        scale = self.height / 101.5
        self.canvas.delete("customer_point")        # delete point from previous frame
        for i, c in enumerate(self.customers):
            if c.initStep <= step and step < (c.initStep + len(c.route)):
                if c.infected:
                    col = 'red'
                else:
                    col = 'yellow'
                x = startx + c.route[step-c.initStep+1][0] * scale
                # fig_bounds = self.canvas.bbox(self.store_fig)  # returns a tuple like (x1, y1, x2, y2)
                # img_height = fig_bounds[3] * 0.9
                y = starty - (c.route[step-c.initStep+1][1] * scale)
                oval = self.canvas.create_oval(x, y, x+radius, y+radius, fill=col, tags=("customer_point"))
                
