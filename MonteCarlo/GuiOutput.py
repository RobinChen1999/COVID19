import tkinter as tk
import threading
import glob
import os
from PIL import Image, ImageTk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tkinter.filedialog import asksaveasfile


class GuiOutput:
    window_width = 1600
    window_height = 800

    def __init__(self, simulation_params):
        self.draw_output_window()
        self.simulating = True
        self.update_output("Running simulation with the following parameters:")
        self.max_steps = simulation_params["max_steps"]
        self.seed = simulation_params["seed"]

        # Start load_figures in new thread so GUI doesn't block
        t = threading.Thread(target=self.load_figures)
        t.setDaemon(True)
        t.start()

    # updates output window after simulation is done
    def update_on_sim_finished(self, store_plot):
        self.txt_output.config(cursor='arrow')
        self.txt_output.pack()
        self.update_output("Simulation finished!")
        self.lbl_sim.destroy()

        self.store_plot = store_plot
        self.store_plot.init_canvas(window=self.frm_sim, height=self.canvas_height)

        steps = int(self.max_steps) - 1
        length = max(int((self.window_width / 2) / steps), 10)
        slider = tk.Scale(self.frm_sim, from_=0, to=steps, length=int(self.canvas_height), sliderlength=length,
                          orient=tk.HORIZONTAL, command=self.slider_handler)
        slider.pack()
        btn_export = tk.Button(self.frm_sim, text="Export video", command=lambda: self.save_file())
        btn_export.pack()

    # Handle slider response
    def slider_handler(self, value):
        self.store_plot.update_figure(value)
        self.update_displayed_step(int(value))
        self.update_markers(int(value))

    # opens a 'save-as' window to save the video
    def save_file(self):
        file = asksaveasfile(mode="wb", title="Save Figure", defaultextension=".mkv",
                             filetypes=(("mkv files", ".mkv"), ("all files", ".*")))
        if file is None:
            return None
        vid_to_save = open("video.mkv", "rb").read()
        file.write(vid_to_save)
        file.close()

    # load the already simulated figures
    def load_figures(self):
        while self.simulating:
            # when simFigures has at least 2 figures
            if len(os.listdir('simFigures')) > 1:
                figureList = glob.glob('simFigures/simFigure_%s_*' % self.seed + '.png')
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
        self.output_line_nr = 0

        window = tk.Toplevel()
        window.state('zoomed')

        # Simulation frame
        self.frm_sim = tk.Frame(window, height=self.window_height / 2, width=self.window_width / 2, bg="red")

        lbl_id_sim = tk.Label(self.frm_sim, text="Simulation Frame")
        lbl_id_sim.pack()

        self.lbl_sim = tk.Label(self.frm_sim, cursor='watch')
        self.lbl_sim.pack()

        self.canvas_height = self.window_height / 3 * 2

        # Output frame
        frm_output = tk.Frame(window, height=self.window_height / 2, width=self.window_width / 2, bg="yellow")

        lbl_id_parameters = tk.Label(frm_output, text="Output Frame")
        lbl_id_parameters.pack()

        self.txt_output = tk.Text(
            frm_output, height=15, width=70, cursor='watch')
        self.txt_output.config(wrap='none', state='disabled')
        self.txt_output.pack()

        self.txt_step_output = tk.Text(frm_output, height=4, width=70)
        self.txt_step_output.config(wrap='none', state='disabled')
        self.txt_step_output.pack(pady=20)

        self.frm_graphs = tk.Frame(frm_output, bg="green")
        self.frm_graphs.pack(fill=None, expand=False)

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
        self.canvas.draw()

        self.canvas.get_tk_widget().pack(fill=tk.BOTH)

        self.frm_sim.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        frm_output.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True)

    def update_output(self, line):
        if self.txt_output == 0:
            raise Exception("Output text is undefined")
        else:
            # Construct output line
            output_line = ""
            if self.txt_output.get("1.0", tk.END) != "\n":
                output_line += "\n"

            # output_line += str(self.output_line_nr) + ": " + line
            output_line += " " + line

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
