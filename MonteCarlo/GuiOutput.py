import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading
import glob
import os
from pathlib import Path
from PIL import Image, ImageTk
import numpy as np


def format_time(time_in_seconds):
    seconds = round(time_in_seconds % 60)
    minutes = int(time_in_seconds / 60) % 60
    hours = int(time_in_seconds / 3600) % 60

    formatted_time = ""

    # Check if hours need to be displayed
    if hours != 0:
        # Add leading zero
        if minutes < 10:
            minutes = "0" + str(minutes)
        formatted_time += str(hours) + ":" + str(minutes)
    else:
        formatted_time += str(minutes)

    # Add leading zero
    if seconds < 10:
        seconds = "0" + str(seconds)

    formatted_time += ":" + str(seconds)

    return formatted_time


class GuiOutput:
    window_width = 1600
    window_height = 800
    plt.rcParams["figure.figsize"] = 5, 3

    def __init__(self, output_window, frm_parameters, frm_buttons, simulation_params, sim_id, nr_customers):
        self.simulating = True
        self.sim_playing = tk.BooleanVar(False)
        self.max_steps = simulation_params["max_steps"]
        self.seed = simulation_params["seed"]
        self.id = sim_id
        self.sim_terminated = tk.BooleanVar(False)
        self.window = output_window
        self.style = ttk.Style(self.window)
        self.frm_parameters = frm_parameters
        self.frm_buttons = frm_buttons
        self.draw_output_window()
        self.slider_value_old = 0
        self.nr_customers = nr_customers
        self.step = 0
        self.expected_step_limit = simulation_params["max_steps"]

        # Column weights
        self.window.grid_columnconfigure(0, minsize=350)
        self.window.grid_columnconfigure(1, weight=10)
        # self.window.grid_columnconfigure(2, minsize=200)

        self.time = 0
        self.exposure = 0
        self.customer_graph_visible = False
        self.last_updated_time = time.time()
        self.time_per_step = 1
        self.time_left = self.max_steps
        self.time_started = time.time()

        self.left_customers = []

        # Start load_figures in new thread so GUI doesn't block
        self.t = threading.Thread(target=self.load_figures)
        self.t.setDaemon(True)
        self.t.start()

        # Create a thread for playing the simulation
        # self.thread_play = threading.Thread(target=self.play_simulation, daemon=True)
        # self.thread_play.setDaemon(True)
        self.threads = []

        
    def terminate_sim(self):
        figureList = glob.glob('simFigures/simFigure_%d_%s_*' % (self.id, self.seed) + '.png')
        if len(figureList) > 1:
            self.sim_terminated.set(True)
            self.btn_terminate.destroy()
        self.window.focus()

    # updates output window after simulation is done
    def update_on_sim_finished(self, store_plot):
        self.lbl_status.config(text="Simulation Finished!")
        self.lbl_sim.destroy()
        self.btn_terminate.destroy()

        # Remove time_left counter
        self.lbl_eta.configure(text='Total simulation time:')
        self.lbl_eta_value.configure(text=format_time(time.time() - self.time_started))

        self.store_plot = store_plot
        self.store_plot.init_canvas(self.frm_sim, self.canvas_height, self.ax_time, self.ax_customer_exposure, self.customer_canvas)

        steps = int(self.max_steps) - 1
        length = max(int((self.window_width / 2) / steps), 10)
        ttk.Style().configure('my.Horizontal.TScale', sliderlength=length, tickinterval=1)
        self.slider = ttk.Scale(self.frm_sim, from_=0, to=steps, length=int(self.canvas_height),
                                style='my.Horizontal.TScale', orient=tk.HORIZONTAL, command=self.slider_handler)
        self.slider.pack(pady=3)

        self.style.configure('Play.TButton', foreground='#cccccc', font=('Helvetica', 12, 'bold'))
        self.style.configure('PrevNext.TButton', font=('Helvetica', 12, 'bold'))
        btn_width=  4
        frm_play_btns = ttk.Frame(self.frm_sim)
        btn_prev = ttk.Button(frm_play_btns, style="PrevNext.TButton", text="<<", width=btn_width, command=lambda: self.handle_play_buttons(-1))
        btn_prev.pack(side=tk.LEFT, padx=btn_width)
        self.btn_play = ttk.Button(frm_play_btns, style="Play.TButton", width=btn_width, text="►", command=lambda: self.handle_play_buttons(0))
        self.btn_play.pack(side=tk.LEFT, padx=btn_width)
        btn_next = ttk.Button(frm_play_btns, style="PrevNext.TButton", text=">>", width=btn_width, command=lambda: self.handle_play_buttons(1))
        btn_next.pack(side=tk.LEFT, padx=btn_width)
        frm_play_btns.pack()

        btn_export = ttk.Button(self.frm_buttons, text="Export Video", command=lambda: self.save_file())
        btn_export.pack(side=tk.LEFT, padx=10)

        self.update_displayed_step(0)


    # initialize the graph for customer details
    def init_customer_graph(self):
        
        plt.ion()
        self.fig = plt.Figure(dpi=100)
        self.fig.subplots_adjust(bottom=0.15)

        self.ax_time = self.fig.add_subplot(111)
        self.ax_time.set_xlabel('Step')
        self.ax_time.set_ylabel('Time')

        self.ax_customer_exposure = self.ax_time.twinx()
        self.ax_customer_exposure.set_ylabel('Exposure')

        self.ax_time.axis((0, int(self.max_steps) - 1, 0, 1))
        self.ax_customer_exposure.axis((0, int(self.max_steps) - 1, 0, 1))

        self.ax_time.plot([], [], color='grey', label='Time spent in store')
        self.ax_customer_exposure.plot([], [], color='green', label='Cumulative Exposure')

        self.ax_time.legend(loc="upper left", prop={'size': 8})
        self.ax_customer_exposure.legend(loc="upper right", prop={'size': 8})

        self.customer_canvas = FigureCanvasTkAgg(self.fig, self.frm_graphs)
        self.customer_canvas.callbacks.connect('button_press_event', self.graph_on_click)

    # opens a 'save-as' window to save the video
    def save_file(self):
        download_folder = str(os.path.join(Path.home(), "Downloads"))
        file = filedialog.asksaveasfile(initialdir=download_folder, initialfile="simulation_%d_%s.mkv" % (self.id, self.seed),
                             mode="wb", title="Save Simulation",
                             defaultextension=".mkv", filetypes=(("mkv files", ".mkv"), ("all files", ".*")))
        if file is None:
            return None
        vid_to_save = open("video_%d_%s.mkv" % (self.id, self.seed), "rb").read()
        file.write(vid_to_save)
        file.close()

    # Handle slider response
    def slider_handler(self, value):
        if not float(value) % 1 == 0:
            scl_step = round(float(value))
            self.update_step(scl_step)
            self.slider.set(scl_step)

    # handle the "Prev", "Play" and "Next" buttons
    def handle_play_buttons(self, value):
        if value == 0:      # play button clicked
            if self.sim_playing.get():
                self.sim_playing.set(False)
                self.btn_play.config(text="▶")
            else:
                self.sim_playing.set(True)
                self.btn_play.config(text="▮▮")
                t = threading.Thread(target=self.play_simulation, daemon=True).start()
        else:               # if prev = -1 or next = 1 clicked
            self.sim_playing.set(False)
            next_step = int(self.slider.get() + value)
            if 0 <= next_step and next_step < int(self.max_steps):
                self.slider.set(next_step)
                self.update_step(next_step)
            self.window.focus()
    
    def play_simulation(self):
        step = int(self.slider.get())
        speed = max(2/int(self.max_steps), 0.005)
        while self.sim_playing.get():
            step += 1
            if step >= int(self.max_steps):
                self.sim_playing.set(False)
                self.btn_play.config(text="▶")
                break
            self.slider.set(step)
            self.update_step(step)
            time.sleep(speed)
        self.window.focus()

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
            if len(figureList) > 2:
                latest_figure = figureList[-3]  # get second last element picture
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

        self.btn_terminate = ttk.Button(self.frm_buttons, text="Terminate Simulation", command=self.terminate_sim, style='Terminate.TButton')

        # Simulation frame
        self.frm_sim = ttk.Frame(self.window, padding=(0, 20, 0, 0))
        self.canvas_height = 300

        # Aerosol meter
        frm_aerosol = ttk.Frame(self.window)
        for i in range(4):
            aerosol_label = ttk.Label(frm_aerosol, text=("10^"+str(2-i)))
            aerosol_label.grid(row=0, column=i*5)
        img = Image.open("resources/aerosols_meter_horizontal.png")
        img_meter = ImageTk.PhotoImage(img.resize((int(self.canvas_height),int(img.size[1]/2))))
        aerosol_meter = ttk.Label(frm_aerosol, image=img_meter)
        aerosol_meter.image = img_meter
        aerosol_meter.grid(row=1, column=0, columnspan=4*4)
        frm_aerosol.grid(row=0, column=1, padx=10)

        self.lbl_sim = ttk.Label(self.frm_sim)
        self.lbl_sim.pack()

        # Notebook tab for output and cough event
        self.notebook_output = ttk.Notebook(self.frm_parameters, takefocus=False)
        self.notebook_output.bind("<<NotebookTabChanged>>", lambda event: self.remove_focus())
        self.notebook_output.pack(fill=tk.BOTH, pady=10)

        self.frm_output_frame = ttk.Frame(self.notebook_output)
        self.notebook_output.add(self.frm_output_frame, text='Output')

        # scrollable canvas for cough event
        container = ttk.Frame(self.notebook_output)
        self.notebook_output.add(container, text="Cough Event")

        def try_scroll(a, b, c="units", d=1):
            try: self.event_canvas.yview(a, b)
            except: pass
        
        canvas_height = 200
        self.event_canvas = tk.Canvas(container, height=canvas_height, width=100)
        
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=try_scroll)
        self.frm_event = ttk.Frame(self.event_canvas)

        # resize scrollregion every time a label is added to the frame
        self.frm_event.bind(
            "<Configure>",
            lambda e: self.event_canvas.configure(
                scrollregion=self.event_canvas.bbox("all")
            )
        )

        # bind scrolling with mousewheel
        # only scroll if the canvas is longer then displayed height
        def handle_scroll(event):
            if self.event_canvas.bbox("all")[3] >= canvas_height:          
                self.event_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        # only bind the MouseWheel when mouse is inside the container frame
        container.bind("<Enter>", lambda e: self.event_canvas.bind_all("<MouseWheel>", handle_scroll))
        container.bind("<Leave>", lambda e: self.event_canvas.unbind_all("<MouseWheel>"))

        # the canvas window that handles which part of the frame is shown 
        self.event_canvas.create_window((0, 0), window=self.frm_event, anchor="nw")
        self.event_canvas.configure(yscrollcommand=scrollbar.set)

        self.event_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # placeholder in frame without cough event
        self.lbl_no_event = ttk.Label(self.frm_event, text="There is no cough event yet.")
        self.lbl_no_event.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.cough_line_nr = None
        
        # Output frame
        self.frm_output = ttk.Frame(self.frm_output_frame)
        self.frm_output.pack(fill=tk.BOTH, padx=10, pady=5)
        self.frm_output.grid_columnconfigure(0, weight=1)
        self.frm_output.grid_columnconfigure(1, weight=1)

        i = 0
        lbl_stick = 'w'
        value_stick = 'e'
        self.lbl_status = ttk.Label(self.frm_output, text="Simulating...", anchor='center', font=('Helvetica', 11, 'bold'))
        self.lbl_status.grid(row=i, column=0, columnspan=2, sticky='we')
        i+=1

        self.lbl_status_detail = ttk.Label(self.frm_output, text='', anchor='center', font=('Helvetica', 8, 'italic'))
        self.lbl_status_detail.grid(row=i, column=0, columnspan=2, sticky='we')
        i+=1

        lbl_linebreak = ttk.Label(self.frm_output, text="")
        lbl_linebreak.grid(row=i, column=0, columnspan=2, sticky='w')
        i+=1

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

        self.lbl_eta = ttk.Label(self.frm_output, text='Estimated time left:', padding=(0, 12, 0, 0))
        self.lbl_eta.grid(row=100, column=0, sticky=lbl_stick)
        self.lbl_eta_value = ttk.Label(self.frm_output, padding=(0, 12, 0, 0))
        self.lbl_eta_value.grid(row=100, column=1, sticky=value_stick)

        self.output_line_nr = i+1

        # Graph frame
        self.frm_graphs = ttk.Frame(self.window)
        self.frm_graphs.grid(row=1, column=2, sticky='ne')

        plt.ion()
        self.fig_graphs = plt.Figure(dpi=100)
        # self.fig_graphs.subplots_adjust(left=0.14, bottom=0.15, right=0.85)
        self.fig_graphs.subplots_adjust(bottom=0.15)

        self.ax_customer = self.fig_graphs.add_subplot(111)
        self.ax_customer.set_xlabel('Step')
        self.ax_customer.set_ylabel('Customers')

        self.ax_exposure = self.ax_customer.twinx()
        self.ax_exposure.set_ylabel('Exposure')

        self.ax_customer.axis((0, 1, 0, 1))
        self.ax_exposure.axis((0, 1, 0, 1))

        self.ax_customer.plot([], [], color='blue', label='Nr. of Customers')
        self.ax_customer.plot([], [], color='red', label='Nr. of Infected Customers')
        self.ax_exposure.plot([], [], color='green', label='Exposure')

        self.ax_customer.legend(loc="upper left", prop={'size': 7})
        self.ax_exposure.legend(loc="upper right", prop={'size': 7})

        self.canvas = FigureCanvasTkAgg(self.fig_graphs, self.frm_graphs)
        self.canvas.callbacks.connect('button_press_event', self.graph_on_click)
        self.canvas.draw()

        self.canvas.get_tk_widget().pack(padx=10, pady=10)

        self.init_customer_graph()
        self.customer_canvas.draw()
        self.customer_canvas.get_tk_widget().pack()

        self.frm_sim.grid(row=1, column=1, sticky="nwe")

        self.update_plot_theme(self.style.theme_use())

    def update_output(self, line, value=""):
        if self.frm_output == 0:
            raise Exception("Output text is undefined")
        else:
            lbl = ttk.Label(self.frm_output, text=line)
            lbl2 = ttk.Label(self.frm_output, text=value)

            if value != "":
                lbl.grid(row=self.output_line_nr, column=0, sticky='w')
                lbl2.grid(row=self.output_line_nr, column=1, sticky='e')
            else:
                lbl.grid(row=self.output_line_nr, column=0, columnspan=2, sticky='w')
            self.output_line_nr += 1

    def output_cough_event(self, step, x, y):
        pady = 1
        # on first cough event, destroy placeholder label
        if self.cough_line_nr == None:
            self.lbl_no_event.destroy()
            self.cough_line_nr = 0
            pady = 6
        # add cough event
        lbl_step = ttk.Label(self.frm_event, text="Step {}:".format(step))
        lbl_step.grid(row=self.cough_line_nr, column=0, sticky='w', padx=10, pady=[pady,0])
        lbl_event = ttk.Label(self.frm_event, text="Customer coughed at ({},{})".format(x, y))
        lbl_event.grid(row=self.cough_line_nr, column=1, sticky='w', padx=20, pady=[pady,0])
        # change tab label
        name = "Cough Event (" + str(self.cough_line_nr+1) + ")"
        self.notebook_output.tab(1, text=name)

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
        # Update image size
        self.canvas_height = 0.85 * self.frm_sim.winfo_width()

        self.step = step

        if self.lbl_step_value == 0:
            raise Exception("Step output text is undefined")
        else:
            # Get data from axis when simulation has finished
            if any(x == -1 for x in [customers_in_store, emitting_customers_in_store, exposure]):
                customers_in_store = self.ax_customer.lines[0].get_ydata()[step]
                emitting_customers_in_store = self.ax_customer.lines[1].get_ydata()[step]
                exposure = self.ax_exposure.lines[0].get_ydata()[step]

            self.lbl_step_value.configure(text=step)
            self.lbl_customers_value.configure(text=int(customers_in_store))
            self.lbl_infected_value.configure(text=int(emitting_customers_in_store))
            self.lbl_exposure_value.configure(text='%.3f' % exposure)

            # Update estimated time left every {update_speed} steps
            if self.simulating:
                update_speed = 5
                if step % update_speed == 0:
                    time_diff = time.time() - self.last_updated_time
                    self.time_per_step = time_diff / update_speed
                    time_left = (int(self.expected_step_limit) - step) * self.time_per_step
                    self.time_left = time_left

                    self.last_updated_time = time.time()
                else:
                    time_left = self.time_left - (step % update_speed) * self.time_per_step
                self.lbl_eta_value.configure(text=format_time(time_left))


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

    def update_plot_theme(self, theme):
        c_light = (239/255, 240/255, 241/255)
        h_light = "#373c41"
        c_dark = (55/255, 60/255, 65/255)
        h_dark = "#eff0f1"

        if theme == "breeze-dark":
            color_background = c_dark
            color_axes = c_light
            bg_hex = h_light
        else:
            color_background = c_light
            color_axes = c_dark
            bg_hex = h_dark

        # cough event canvas
        self.event_canvas.config(bg=bg_hex)

        # Background
        self.fig_graphs.set_facecolor(color_background)
        self.ax_customer.set_facecolor(color_background)

        self.fig.set_facecolor(color_background)
        self.ax_time.set_facecolor(color_background)

        # Axes upper plot
        for side in ['top', 'right', 'bottom', 'left']:
            self.ax_exposure.spines[side].set_color(color_axes)
        self.ax_exposure.yaxis.label.set_color(color_axes)
        self.ax_exposure.tick_params(axis='y', colors=color_axes)
        self.ax_customer.xaxis.label.set_color(color_axes)
        self.ax_customer.yaxis.label.set_color(color_axes)
        self.ax_customer.tick_params(axis='x', colors=color_axes)
        self.ax_customer.tick_params(axis='y', colors=color_axes)

        # Axes customer plot
        for side in ['top', 'right', 'bottom', 'left']:
            self.ax_customer_exposure.spines[side].set_color(color_axes)
        self.ax_customer_exposure.yaxis.label.set_color(color_axes)
        self.ax_customer_exposure.tick_params(axis='y', colors=color_axes)
        self.ax_time.xaxis.label.set_color(color_axes)
        self.ax_time.yaxis.label.set_color(color_axes)
        self.ax_time.tick_params(axis='x', colors=color_axes)
        self.ax_time.tick_params(axis='y', colors=color_axes)

        # Title
        self.fig_graphs.suptitle('All Customers', color=color_axes)
        self.fig.suptitle('Clicked Customer', color=color_axes)

        self.canvas.draw_idle()
        self.customer_canvas.draw_idle()

    def update_status_detail(self, text):
        self.lbl_status_detail.config(text=text)

        if text == 'Calculating step':
            self.btn_terminate.pack(side=tk.LEFT, padx=10)

    def update_expected_shopping_time_left(self, leaving_customer, all_customers_in_store):
        self.left_customers.append(leaving_customer)

        total_time = 0
        total_items = 0
        min_time = 99999

        for customer in self.left_customers:
            if customer[0] < min_time:
                min_time = customer[0]

        for customer in self.left_customers:
            total_time += customer[0] - min_time
            total_items += customer[1]

        if total_time <= 0:
            total_time = 99999

        avg_time_per_item = total_time / total_items

        total_items_needed_in_store = 0
        for customer in all_customers_in_store:
            total_items_needed_in_store += len(customer.shoppingList)

        params = eval(os.environ["Params"])

        total_items_needed_unknown = (int(self.nr_customers) - len(self.left_customers) - len(all_customers_in_store)) * params["MAXSHOPPINGLIST"] * 0.5

        total_items_left = total_items_needed_in_store + total_items_needed_unknown

        expected_steps_left = total_items_left * avg_time_per_item

        # Update expected step limit
        if expected_steps_left > 0 and round(self.step + expected_steps_left) < int(self.max_steps):
            self.expected_step_limit = round(self.step + expected_steps_left)

    def remove_focus(self):
        self.window.focus()

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