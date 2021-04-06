from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Store import *
from Customer import *

import tkinter as tk
from tkinter import ttk
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
    def __init__(self, store, gui, customers, time, exposure, norm_exposure, parula_map, useDiffusion, seed, sim_id):
        self.store = store
        self.gui = gui
        self.customers = customers
        self.parula_map = parula_map
        self.useDiffusion = useDiffusion
        self.seed = seed
        self.id = sim_id
        self.window = 0
        self.time = time
        self.exposure = exposure
        self.norm_exposure = norm_exposure
        self.customer_list = []
        self.radius = 10
        self.step = 0
        
    def init_canvas(self, window, height, axis1, axis2, canvas):
        self.height = height
        self.window = window
        self.ax1 = axis1
        self.ax2 = axis2
        self.customer_canvas = canvas
        self.canvas = tk.Canvas(window, height=self.height, width=self.height)
        self.canvas.pack()
        self.store_fig = self.canvas.create_image(0, 0, anchor="nw")
        self.update_figure(0)

    def update_figure(self, value):
        image = Image.open('simFigures/simFigure_%d_%s_%07d.png'%(self.id, self.seed, int(value)))
        self.step_img = ImageTk.PhotoImage(image.resize((int(self.height),int(self.height))))
        self.canvas.itemconfig(self.store_fig, image=self.step_img)
        self.customer_list.clear()
        self.draw_customers(int(value))

    def draw_customers(self, step):
        self.step = step
        # add every customer to the plot,and the colour denotes infected and healthy customers
        startx = -2
        starty = self.height * 0.88 -3
        scalex = self.height / 101.5
        scaley = self.height / 109.5
        self.canvas.delete("customer_point")        # delete point from previous frame
        for i, c in enumerate(self.customers):
            if c.initStep <= self.step and self.step < (c.initStep + len(c.route)):
                x = startx + c.route[self.step-c.initStep+1][0] * scalex
                y = starty - (c.route[self.step-c.initStep+1][1] * scaley)
                if c.infected:
                    shape = self.canvas.create_polygon([x - 10, y-10, x+10, y+10], outline="black",
                              fill="red", tags=("customer_point"))
                else:
                    col = matplotlib.colors.to_hex([1, 1 - self.norm_exposure[self.step, i], 0])
                    shape = self.canvas.create_oval(x, y, x+self.radius, y+self.radius, fill=col, tags=("customer_point"))
                self.customer_list.append((i, shape))
                self.canvas.tag_bind(shape, '<Button-1>', self.on_customer_click)
        
    def on_customer_click(self, customer):
        oval = customer.widget.find_withtag('current&&customer_point')[0]
        for c, j in self.customer_list:
            if j == oval:              
                x = list(range(len(self.time[:, c])))

                # Update lines
                self.ax1.lines[0].set_data(x, self.time[:, c])
                self.ax2.lines[0].set_data(x, self.exposure[:, c])

                self.gui.update_customer_markers(self.step, self.time, self.exposure)
        