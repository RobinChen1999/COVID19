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

import numpy as np

class StorePlot:
    def __init__(self, store, customers, time, exposure, parula_map, useDiffusion, seed, sim_id):
        self.store = store
        self.customers = customers
        self.parula_map = parula_map
        self.useDiffusion = useDiffusion
        self.seed = seed
        self.id = sim_id
        self.window = 0
        self.time = time
        self.exposure = exposure
        
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
        self.draw_customers(int(value))

    def draw_customers(self, step):
        # add every customer to the plot,and the colour denotes infected and healthy customers
        radius = 10
        startx = -2
        starty = self.height * 0.88 -3
        scalex = self.height / 101.5
        scaley = self.height / 109.5
        self.canvas.delete("customer_point")        # delete point from previous frame
        for i, c in enumerate(self.customers):
            if c.initStep <= step and step < (c.initStep + len(c.route)):
                if c.infected:
                    col = 'red'
                else:
                    col = 'yellow'
                x = startx + c.route[step-c.initStep+1][0] * scalex
                y = starty - (c.route[step-c.initStep+1][1] * scaley)
                oval = self.canvas.create_oval(x, y, x+radius, y+radius, fill=col, tags=("customer_point"))
                self.canvas.tag_bind(oval, '<Button-1>', self.on_customer_click(i))
        
    def on_customer_click(self, customer):
        x = list(range(len(self.time[:, customer])))

        # Update lines
        self.ax1.lines[0].set_data(x, self.time[:, customer])
        self.ax2.lines[0].set_data(x, self.exposure[:, customer])

        # Update scale
        self.ax1.axis((0, np.shape(self.time)[0], 0, max(np.amax(self.time) * 1.25, 1)))
        self.ax2.axis((0, np.shape(self.exposure)[0], 0, max(np.amax(self.exposure) * 1.25, 1)))

        self.customer_canvas.draw_idle()