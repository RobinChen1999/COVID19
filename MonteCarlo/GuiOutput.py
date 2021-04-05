import tkinter as tk
from tkinter import ttk
import threading
import glob
import os
from PIL import Image, ImageTk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tkinter.filedialog import asksaveasfile
from pathlib import Path

import numpy as np

class GuiOutput:
    window_width = 1600
    window_height = 800
    plt.rcParams["figure.figsize"] = 4,3

    def __init__(self, output_window, frm_parameters, frm_buttons, simulation_params, sim_id, nr_customers):
        self.simulating = True
        self.max_steps = simulation_params["max_steps"]
        self.seed = simulation_params["seed"]
        self.id = sim_id
        self.window = output_window
        self.frm_parameters = frm_parameters
        self.frm_buttons = frm_buttons
        self.draw_output_window()

        self.fig = 0
        # self.ax_time = 0
        # self.ax_customer_exposure = 0
        # self.customer_canvas = 0
        self.time = 0
        self.exposure = 0
        self.customer_graph_visible = False

        # Start load_figures in new thread so GUI doesn't block
        self.t = threading.Thread(target=self.load_figures)
        self.t.setDaemon(True)
        self.t.start()

        
    # updates output window after simulation is done
    def update_on_sim_finished(self, store_plot):
        self.lbl_status.config(text="Simulation finished!")
        self.lbl_sim.destroy()

        self.store_plot = store_plot
        self.store_plot.init_canvas(self.frm_sim, self.canvas_height, self.ax_time, self.ax_customer_exposure, self.customer_canvas)

        steps = int(self.max_steps) - 1
        length = max(int((self.window_width / 2) / steps), 10)
        ttk.Style().configure('my.Horizontal.TScale', sliderlength=length, tickinterval=1)
        self.slider = ttk.Scale(self.frm_sim, from_=0, to=steps, length=int(self.canvas_height),
                                style='my.Horizontal.TScale', orient=tk.HORIZONTAL, command=self.slider_handler)
        self.slider.pack()
        btn_export = ttk.Button(self.frm_buttons, text="Export video", command=lambda: self.save_file())
        btn_export.pack()

    # initialize the graph for customer details
    def init_customer_graph(self):
        
        plt.ion()
        self.fig = plt.Figure(dpi=100)
        self.fig.subplots_adjust(left=0.14, bottom=0.15, right=0.85)

        self.ax_time = self.fig.add_subplot(111)
        self.ax_time.set_xlabel('Step')
        self.ax_time.set_ylabel('Time')

        self.ax_customer_exposure = self.ax_time.twinx()
        self.ax_customer_exposure.set_ylabel('Exposure')

        self.ax_time.axis((0, int(self.max_steps) - 1, 0, 1))
        self.ax_customer_exposure.axis((0, int(self.max_steps) - 1, 0, 1))

        self.ax_time.plot([], [], color='grey', label='Time spent in store')
        self.ax_customer_exposure.plot([], [], color='green', label='Exposure')

        self.ax_time.legend(loc="upper left", prop={'size': 8})
        self.ax_customer_exposure.legend(loc="upper right", prop={'size': 8})

        self.customer_canvas = FigureCanvasTkAgg(self.fig, self.frm_graphs)
        self.customer_canvas.callbacks.connect('button_press_event', self.graph_on_click)

    # opens a 'save-as' window to save the video
    def save_file(self):
        download_folder = str(os.path.join(Path.home(), "Downloads"))
        file = asksaveasfile(initialdir=download_folder, initialfile="simulation_%d_%s.mkv" % (self.id, self.seed),
                             mode="wb", title="Save Simulation",
                             defaultextension=".mkv", filetypes=(("mkv files", ".mkv"), ("all files", ".*")))
        if file is None:
            return None
        vid_to_save = open("video_%d_%s.mkv" % (self.id, self.seed), "rb").read()
        file.write(vid_to_save)
        file.close()

    # Handle slider response
    def slider_handler(self, value):
        value = float(value)
        if int(value) != value:
            self.slider.set(round(value))
            self.update_step(round(value))

    def update_step(self, value):
        self.store_plot.update_figure(str(value))
        self.update_displayed_step(value)
        self.update_markers(value)
        if self.customer_graph_visible:
            self.update_customer_markers(value, self.time, self.exposure)

    # load the already simulated figures
    def load_figures(self):
        while self.simulating:
            # when simulation has at least 2 figures
            figureList = glob.glob('simFigures/simFigure_%d_%s_*' % (self.id, self.seed) + '.png')
            if len(figureList) > 1:
                latest_figure = figureList[-2]  # get second last element
                img = Image.open(latest_figure)
                self.frm_img = ImageTk.PhotoImage(img.resize((int(self.canvas_height), int(self.canvas_height))))
                try:
                    self.lbl_sim.config(image=self.frm_img)
                    self.lbl_sim.image = self.frm_img
                except:
                    pass  # when label is destroyed before while-loop ends

    # Output
    def draw_output_window(self):

        def create_tool_tip(widget,row, text):
            desc = ttk.Label(widget, text="?")
            desc.grid(row=row,column=1, sticky="e")
            tool_tip = ToolTip(desc)

            def enter(event):
                tool_tip.showtip(text)

            def leave(event):
                tool_tip.hidetip()

            desc.bind('<Enter>', enter)
            desc.bind('<Leave>', leave)

        self.output_line_nr = 0

        # Simulation frame
        self.frm_sim = ttk.Frame(self.window, height=self.window_height, width=self.window_width / 2)
        self.canvas_height = self.window_height / 2

        lbl_id_sim = ttk.Label(self.frm_sim, text="Simulation")
        lbl_id_sim.pack()

        # Aerosol meter
        frm_aerosol = ttk.Frame(self.window)
        for i in range(4):
            aerosol_label = ttk.Label(frm_aerosol, text=("10^"+str(2-i)))
            aerosol_label.grid(row=0, column=i*5)
        img = Image.open("aerosols_meter_horizontal.png")
        img_meter = ImageTk.PhotoImage(img.resize((int(self.canvas_height),int(img.size[1]/2))))
        aerosol_meter = ttk.Label(frm_aerosol, image=img_meter)
        aerosol_meter.image = img_meter
        aerosol_meter.grid(row=1, column=0, columnspan=4*4)
        frm_aerosol.grid(row=0, column=1, padx=10)

        self.lbl_sim = ttk.Label(self.frm_sim, cursor='watch')
        self.lbl_sim.pack()

        # Output frame
        self.frm_output = ttk.LabelFrame(self.frm_parameters, text="Output")
        self.frm_output.pack(fill=tk.BOTH)
        i = 0
        lbl_stick = 'w'
        value_stick = 'e'
        self.lbl_status = ttk.Label(self.frm_output, text="Initializing simulation...")
        self.lbl_status.grid(row=i, column=0, columnspan=2, sticky='e', pady=10)
        i+=1
        self.output_line_nr = i
        self.update_output("-")

        lbl_step = ttk.Label(self.frm_output, text="Step:")
        lbl_step.grid(row=i, column=0, sticky=lbl_stick)
        self.lbl_step_value = ttk.Label(self.frm_output)
        self.lbl_step_value.grid(row=i, column=1, sticky=value_stick)
        i+=1
        lbl_customers = ttk.Label(self.frm_output, text="Customers in store:")
        lbl_customers.grid(row=i, column=0, sticky=lbl_stick)
        self.lbl_customers_value = ttk.Label(self.frm_output)
        self.lbl_customers_value.grid(row=i, column=1, sticky=value_stick)
        i+=1
        lbl_infected = ttk.Label(self.frm_output, text="Infected customers in store:")
        lbl_infected.grid(row=i, column=0, sticky=lbl_stick)
        self.lbl_infected_value = ttk.Label(self.frm_output)
        self.lbl_infected_value.grid(row=i, column=1, sticky=value_stick)
        i+=1
        lbl_exposure = ttk.Label(self.frm_output, text="Exposure on healthy customers:")
        lbl_exposure.grid(row=i, column=0, sticky=lbl_stick)
        self.lbl_exposure_value = ttk.Label(self.frm_output)
        self.lbl_exposure_value.grid(row=i, column=1, sticky=value_stick)

        self.output_line_nr = i+1

        ### cough event ###
        self.frm_event = ttk.LabelFrame(self.frm_parameters, text="Cough event")
        self.frm_event.pack(fill=tk.BOTH)
        self.cough_line_nr = 0

        # Graph frame
        self.frm_graphs = ttk.Frame(self.window)
        self.frm_graphs.grid(row=1, column=2, sticky='n')

        lbl_graph = ttk.Label(self.frm_graphs, text="Customer Exposure Graph")
        lbl_graph.grid(row=0,column=0, pady=10)
        create_tool_tip(self.frm_graphs, 0, "Click in the graphs to jump to its corresponding step in the simulation")

        plt.ion()
        fig_graphs = plt.Figure(dpi=100)
        fig_graphs.subplots_adjust(left=0.14, bottom=0.15, right=0.85)

        self.ax_customer = fig_graphs.add_subplot(111)
        self.ax_customer.set_xlabel('Step')
        self.ax_customer.set_ylabel('Customers')

        self.ax_exposure = self.ax_customer.twinx()
        self.ax_exposure.set_ylabel('Exposure')

        self.ax_customer.axis((0, 1, 0, 1))
        self.ax_exposure.axis((0, 1, 0, 1))

        self.ax_customer.plot([], [], color='blue', label='Nr. of Customers')
        self.ax_customer.plot([], [], color='red', label='Nr. of Infected Customers')
        self.ax_exposure.plot([], [], color='green', label='Total Exposure')

        self.ax_customer.legend(loc="upper left", prop={'size': 8})
        self.ax_exposure.legend(loc="upper right", prop={'size': 8})

        self.canvas = FigureCanvasTkAgg(fig_graphs, self.frm_graphs)
        self.canvas.callbacks.connect('button_press_event', self.graph_on_click)
        self.canvas.draw()

        self.canvas.get_tk_widget().grid(row=1,column=0,columnspan=2, padx=10, pady=10)

        # Customer detail graph
        lbl_customer_graph = ttk.Label(self.frm_graphs, text="Individual Customer Graph")
        lbl_customer_graph.grid(row=3,column=0, pady=10)
        create_tool_tip(self.frm_graphs, 3, "Click on a customer in the simulation to show their specific details in the graph")

        self.init_customer_graph()
        self.customer_canvas.draw()
        self.customer_canvas.get_tk_widget().grid(row=4,column=0,columnspan=2)

        self.frm_sim.grid(row=1, column=1, sticky="nw", padx=10)

    def update_output(self, line):
        if self.frm_output == 0:
            raise Exception("Output text is undefined")
        else:
            lbl = ttk.Label(self.frm_output, text=line)
            lbl.grid(row=self.output_line_nr, column=0, columnspan=2, sticky='w')
            self.output_line_nr += 1

    def output_cough_event(self, step, x, y):
        lbl_step = ttk.Label(self.frm_event, text="Step {}:".format(step))
        lbl_step.grid(row=self.cough_line_nr, column=0, sticky='w')
        lbl_event = ttk.Label(self.frm_event, text="Customer coughed at ({},{})".format(x, y))
        lbl_event.grid(row=self.cough_line_nr, column=1, sticky='w', padx=10)

        # mouse event
        def enter(event):
            lbl_step.config(relief=tk.RAISED)

        def click(event):
            if not self.simulating:
                self.slider.set(str(step))
                self.update_step(step)
            

        def leave(event):
            lbl_step.config(relief=tk.FLAT)

        lbl_step.bind('<Enter>', enter)
        lbl_step.bind('<Leave>', leave)
        lbl_step.bind('<Button-1>', click)

        self.cough_line_nr+=1

    def update_displayed_step(self, step, customers_in_store=-1, emitting_customers_in_store=-1,
                              exposure=-1):
        if self.lbl_step_value == 0:
            raise Exception("Step output text is undefined")
        else:
            # Get data from axis when simulation has finished
            if any(x == -1 for x in [customers_in_store, emitting_customers_in_store, exposure]):
                customers_in_store = self.ax_customer.lines[0].get_ydata()[step]
                emitting_customers_in_store = self.ax_customer.lines[1].get_ydata()[step]
                exposure = self.ax_exposure.lines[0].get_ydata()[step]

            self.lbl_step_value.configure(text=step)
            self.lbl_customers_value.configure(text=customers_in_store)
            self.lbl_infected_value.configure(text=emitting_customers_in_store)
            self.lbl_exposure_value.configure(text=exposure)

    def update_graph(self, step, customers_in_store, infected_customers, exposure):
        # Get only relevant data
        y_customers_in_store = customers_in_store[:(step + 1)]
        y_infected_customers = infected_customers[:(step + 1)]
        y_exposure = exposure[:(step + 1)]
        x = list(range(len(y_customers_in_store)))

        # Update lines
        self.ax_customer.lines[0].set_data(x, y_customers_in_store)
        self.ax_customer.lines[1].set_data(x, y_infected_customers)
        self.ax_exposure.lines[0].set_data(x, y_exposure)

        # Update scale
        step = 1 if step == 0 else step
        self.ax_customer.axis((0, step, 0, max(max(y_customers_in_store), max(y_infected_customers)) * 1.25))
        self.ax_exposure.axis((0, step, 0, max(max(y_exposure) * 1.25, 1)))

        self.canvas.draw_idle()

    def update_markers(self, step):
        # Remove existing markers
        if len(self.ax_customer.lines) > 3:
            self.ax_customer.lines.pop(4)
            self.ax_customer.lines.pop(3)
            self.ax_customer.lines.pop(2)
            self.ax_exposure.lines.pop(1)

        # Draw line
        self.ax_customer.axvline(step, color="lightgrey", linestyle="dashed")

        # Draw markers
        self.ax_customer.plot(step, self.ax_customer.lines[0].get_ydata()[step], 'bo')
        self.ax_customer.plot(step, self.ax_customer.lines[1].get_ydata()[step], 'ro')
        self.ax_exposure.plot(step, self.ax_exposure.lines[0].get_ydata()[step], 'go')

        self.canvas.draw_idle()

    def update_customer_markers(self, step, time, exposure):
        self.customer_graph_visible = True
        self.time = time
        self.exposure = exposure

        # Update scale
        self.ax_time.axis((0, int(self.max_steps) - 1, 0, max(np.amax(time) * 1.25, 1)))
        self.ax_customer_exposure.axis((0, int(self.max_steps) - 1, 0, max(np.amax(exposure) * 1.25, 1)))

        # Remove existing markers
        if len(self.ax_time.lines) > 2:
            self.ax_time.lines.pop(2)
            self.ax_time.lines.pop(1)
            self.ax_customer_exposure.lines.pop(1)

        # Draw line
        self.ax_time.axvline(step, color="lightgrey", linestyle="dashed")

        # Draw markers
        self.ax_time.plot(step, self.ax_time.lines[0].get_ydata()[step], color="grey", marker="o")
        self.ax_customer_exposure.plot(step, self.ax_customer_exposure.lines[0].get_ydata()[step], 'go')

        self.customer_canvas.draw_idle()

    def graph_on_click(self, event):
        # Check if click is inside plot
        if event.inaxes is not None:
            value = round(event.xdata)
            self.slider.set(str(value))
            self.update_step(value)

class ToolTip(object):
    def __init__(self, widget):
        self.text = ""
        self.widget = widget
        self.tip_window = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        self.text = text
        "Display text in tooltip window"
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() - 100
        y = y + cy + self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        frm = ttk.Frame(tw, relief=tk.SOLID)

        lbl = ttk.Label(frm, text=self.text, justify=tk.LEFT)
        lbl.pack(padx=5, pady=5)

        frm.pack()

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()