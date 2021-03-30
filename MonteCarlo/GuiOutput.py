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


class GuiOutput:
    window_width = 1600
    window_height = 800

    def __init__(self, output_window, frm_parameters, simulation_params, sim_id, nr_customers):
        self.simulating = True
        self.max_steps = simulation_params["max_steps"]
        self.seed = simulation_params["seed"]
        self.id = sim_id
        self.window = output_window
        self.frm_parameters = frm_parameters
        self.draw_output_window()
        self.update_output(
            "Running simulation until all {} customers are finished\n or step limit of {} has been reached.".format(
                nr_customers, self.max_steps))

        # Start load_figures in new thread so GUI doesn't block
        self.t = threading.Thread(target=self.load_figures)
        self.t.setDaemon(True)
        self.t.start()

        
    # updates output window after simulation is done
    def update_on_sim_finished(self, store_plot):
        self.txt_output.config(cursor='arrow')
        # self.txt_output.pack()
        self.update_output("Simulation finished!")
        self.lbl_sim.destroy()

        self.store_plot = store_plot
        self.store_plot.init_canvas(window=self.frm_sim, height=self.canvas_height)

        steps = int(self.max_steps) - 1
        length = max(int((self.window_width / 2) / steps), 10)
        ttk.Style().configure('my.Horizontal.TScale', sliderlength=length, tickinterval=1)
        self.slider = ttk.Scale(self.frm_sim, from_=0, to=steps, length=int(self.canvas_height),
                                style='my.Horizontal.TScale', orient=tk.HORIZONTAL, command=self.slider_handler)
        self.slider.pack()
        btn_export = ttk.Button(self.frm_sim, text="Export video", command=lambda: self.save_file())
        btn_export.pack()

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

    # when output window closes
    def close_window(self):
        # clear images with current seed out of simFigures folder
        figureList = glob.glob('simFigures/simFigure_%d_%s_*' % (self.id, self.seed) + '.png')
        for f in figureList:
            os.remove(f)

        # remove data files of current seed
        dataFiles = glob.glob('*%d_%s.dat' % (self.id, self.seed))
        for d in dataFiles:
            os.remove(d)

        # remove video of current seed
        try:
            os.remove('video_%d_%s.mkv' % (self.id, self.seed))
        except Exception as e:
            print('Failed to delete video')

        self.window.destroy()

    # Output
    def draw_output_window(self):
        self.output_line_nr = 0

        # Simulation frame
        self.frm_sim = ttk.Frame(self.window, height=self.window_height / 2, width=self.window_width / 2)
        self.canvas_height = self.window_height / 3 * 2

        lbl_id_sim = ttk.Label(self.frm_sim, text="Simulation")
        lbl_id_sim.pack()

        # Aerosol meter
        frm_aerosol = ttk.Frame(self.window)
        for i in range(4):
            aerosol_label = ttk.Label(frm_aerosol, text=("10^"+str(2-i)))
            aerosol_label.grid(row=0, column=i*5, sticky='c')
        img = Image.open("aerosols_meter_horizontal.png")
        # img_meter = ImageTk.PhotoImage(img)
        img_meter = ImageTk.PhotoImage(img.resize((int(self.canvas_height),int(img.size[1]/2))))
        aerosol_meter = ttk.Label(frm_aerosol, image=img_meter)
        aerosol_meter.image = img_meter
        aerosol_meter.grid(row=1, column=0, columnspan=4*4) #pack(side=tk.TOP, anchor="ne")
        frm_aerosol.grid(row=0, column=1)

        self.lbl_sim = ttk.Label(self.frm_sim, cursor='watch')
        self.lbl_sim.pack()

        # Output frame
        frm_output = ttk.Frame(self.frm_parameters, height=self.window_height / 2, width=self.window_width / 2)

        lbl_id_parameters = ttk.Label(frm_output, text="Output")
        lbl_id_parameters.pack()

        self.txt_output = tk.Text(
            frm_output, height=15, width=40, cursor='watch')
        self.txt_output.config(wrap='none', state='disabled')
        self.txt_output.pack()

        self.txt_step_output = tk.Text(frm_output, height=4, width=40)
        self.txt_step_output.config(wrap='none', state='disabled')
        self.txt_step_output.pack(pady=20)

        self.frm_graphs = ttk.Frame(self.window)
        self.frm_graphs.grid(row=1, column=2, sticky='n') #pack(fill=None, expand=False)

        lbl_graph = ttk.Label(self.frm_graphs, text="Customer Exposure Graph [i]")
        lbl_graph.pack()

        plt.ion()
        fig_graphs = plt.Figure(figsize=(6, 4), dpi=100)

        self.ax_customer = fig_graphs.add_subplot(111)
        self.ax_customer.set_xlabel('Step')
        self.ax_customer.set_ylabel('Customers')

        self.ax_exposure = self.ax_customer.twinx()
        self.ax_exposure.set_ylabel('Exposure')

        self.ax_customer.axis((0, 1, 0, 1))
        self.ax_exposure.axis((0, 1, 0, 1))

        self.ax_customer.plot([], [], color='blue', label='Nr. of Customers')
        self.ax_customer.plot([], [], color='red', label='Nr. of Infected Customers')
        self.ax_exposure.plot([], [], color='green', label='Exposure')

        self.ax_customer.legend(loc="upper left")
        self.ax_exposure.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(fig_graphs, self.frm_graphs)
        self.canvas.callbacks.connect('button_press_event', self.graph_on_click)
        self.canvas.draw()

        self.canvas.get_tk_widget().pack(fill=tk.BOTH)

        self.frm_sim.grid(row=1, column=1, sticky="nw") #pack(fill=tk.BOTH, side=tk.BOTTOM, anchor="w", expand=True)
        frm_output.pack() #grid(row=2, column=0) #pack(fill=tk.BOTH, side=tk.RIGHT, expand=True)

        # self.window.protocol("WM_DELETE_WINDOW", self.close_window) #now hanlded in Gui, quz only one window

    def update_output(self, line):
        if self.txt_output == 0:
            raise Exception("Output text is undefined")
        else:
            # Construct output line
            output_line = ""

            if line == "-":
                if self.txt_output.get("end-1c linestart") != "-":
                    output_line += "\n" + "-" * 20
            else:
                if self.txt_output.get("1.0", tk.END) != "\n":
                    output_line += "\n"

                # output_line += str(self.output_line_nr) + ": " + line
                output_line += line

            # Update output
            self.txt_output.config(state='normal')
            self.txt_output.insert(tk.END, output_line)
            self.txt_output.see('end -1 lines')
            self.txt_output.config(state='disabled')

            self.output_line_nr += 1

    def update_displayed_step(self, step, customers_in_store=-1, emitting_customers_in_store=-1,
                              exposure=-1):
        if self.txt_step_output == 0:
            raise Exception("Step output text is undefined")
        else:
            # Get data from axis when simulation has finished
            if any(x == -1 for x in [customers_in_store, emitting_customers_in_store, exposure]):
                customers_in_store = self.ax_customer.lines[0].get_ydata()[step]
                emitting_customers_in_store = self.ax_customer.lines[1].get_ydata()[step]
                exposure = self.ax_exposure.lines[0].get_ydata()[step]

            output = " Step: {}\n" \
                     "  Customers in store:            {:.0f}\n" \
                     "  Infected customers:            {:.0f}\n" \
                     "  Exposure on healthy customers: {:.3f}".format(step, customers_in_store,
                                                                      emitting_customers_in_store, exposure)

            self.txt_step_output.config(state='normal')
            self.txt_step_output.delete('1.0', tk.END)
            self.txt_step_output.insert(tk.END, output)
            self.txt_step_output.config(state='disabled')

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

    def graph_on_click(self, event):
        # Check if click is inside plot
        if event.inaxes is not None:
            value = round(event.xdata)
            self.slider.set(str(value))
            self.update_step(value)
