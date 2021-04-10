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
        self.step = 0
        self.radius = 10
        self.startx = -3
        self.selected_customer = None
        
    def init_canvas(self, window, height, axis1, axis2, canvas):
        self.height = height
        self.window = window
        self.starty = self.height * 0.985
        self.scalex = self.height / 100
        self.scaley = self.height / 100
        self.ax1 = axis1
        self.ax2 = axis2
        self.customer_canvas = canvas
        self.canvas = tk.Canvas(window, height=self.height, width=self.height)
        self.canvas.pack()
        self.store_fig = self.canvas.create_image(int(height/2), int(height/2) )
        self.update_figure(0)

    def update_figure(self, value):
        image = Image.open('simFigures/simFigure_%d_%s_%07d.png'%(self.id, self.seed, int(value)))
        self.step_img = ImageTk.PhotoImage(image.resize((int(self.height),int(self.height))))
        self.canvas.itemconfig(self.store_fig, image=self.step_img)
        self.customer_list.clear()
        self.draw_customers(int(value))
        self.draw_shoppinglist()

    def draw_customers(self, step):
        self.step = step
        # add every customer to the plot,and the colour denotes infected and healthy customers
        self.canvas.delete("customer_point")        # delete point from previous frame
        for i, c in enumerate(self.customers):
            if c.initStep <= self.step and self.step < (c.initStep + len(c.route)):
                x = self.startx + c.route[self.step-c.initStep][0] * self.scalex
                y = self.starty - (c.route[self.step-c.initStep][1] * self.scaley)
                if c.infected:
                    r = self.radius/2
                    shape = self.canvas.create_polygon([x+r, y, x+2*r, y+r, x+r, y+2*r, x, y+r], outline="black", activewidth=1, activeoutline="white",
                              fill="red", tags=("customer_point"))
                else:
                    col = matplotlib.colors.to_hex([1, 1 - self.norm_exposure[self.step, i], 0])
                    shape = self.canvas.create_oval(x, y, x+self.radius, y+self.radius, fill=col, activewidth=1, activeoutline="white", tags=("customer_point"))
                
                if i == self.selected_customer:
                    self.canvas.itemconfig(shape, width=2, outline="white")

                self.customer_list.append((i, shape))
                self.canvas.tag_bind(shape, '<Button-1>', self.on_customer_click)
        
    def draw_shoppinglist(self):
        self.canvas.delete("shopping_items")        # delete shopping items from previous selected customer
        if self.selected_customer != None:
            customer = self.customers[self.selected_customer]
            for item in customer.completeShoppingList:
                radius = 5
                x = self.startx + self.radius - radius + item[0] * self.scalex
                y = self.starty + self.radius - radius - item[1] * self.scaley
                col="green"
                try:
                    if item[2] <= self.step:
                        col="pink"
                except:
                    # item is not found withing the step limit
                    pass
                                    
                shape = self.canvas.create_rectangle(x, y, x+radius, y+radius, fill=col, tags=("shopping_items"))



    def on_customer_click(self, customer):
        oval = customer.widget.find_withtag('current&&customer_point')[0]
        for c, j in self.customer_list:
            if j == oval:

                # if there was a previously selected customer, reset visuals to normal
                self.canvas.itemconfig("customer_point", width=1, outline="black") 
                
               
                if self.selected_customer == c:
                    self.selected_customer = None       # deselect the customer if clicked again
                else:
                    self.selected_customer = c          # set new selected customer
                    self.canvas.itemconfig(j, width=1, outline="white")

                x = list(range(len(self.time[:, c])))

                # Update lines
                self.ax1.lines[0].set_data(x, self.time[:, c])
                self.ax2.lines[0].set_data(x, self.exposure[:, c])

                self.gui.update_customer_markers(self.step, self.time, self.exposure)
                self.draw_shoppinglist()
        