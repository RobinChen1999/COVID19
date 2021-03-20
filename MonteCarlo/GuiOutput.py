from StorePlot import *

import tkinter as tk
import threading
import imageio
# import shutil
import glob
import os
from PIL import Image, ImageTk

import matplotlib
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
        
        self.store_plot = store_plot
        self.store_plot.init_canvas(canvas=self.canvas_sim, store_fig=self.lbl_sim, height=self.canvas_height)

        steps = int(self.max_steps) - 1
        length = max(int((self.window_width/2)/steps), 10)
        slider = tk.Scale(self.frm_sim, from_=0, to=steps, length=int(self.canvas_height), sliderlength=length, orient=tk.HORIZONTAL, command=self.store_plot.update_figure)
        slider.pack()
        btn_export = tk.Button(self.frm_sim, text="Export video", command=lambda: self.save_file())
        btn_export.pack()
        

    # opens a 'save-as' window to save the video
    def save_file(self):
        file = asksaveasfile(mode="wb", title="Save Figure", defaultextension=".mkv", filetypes = (("mkv files",".mkv"),("all files",".*")))
        if file is None:
            return None
        vid_to_save = open("video.mkv","rb").read()
        file.write(vid_to_save)
        file.close()
    
    # load the already simulated figures
    def load_figures(self):
        while self.simulating:
            # when simFigures has at least 2 figures
            if len(os.listdir('simFigures')) > 1:
                figureList = glob.glob('simFigures/simFigure_%s_*'%self.seed + '.png')
                latest_figure = figureList[-2] # get second last element  
                img = Image.open(latest_figure)
                self.frm_img = ImageTk.PhotoImage(img.resize((int(self.canvas_height), int(self.canvas_height))))
                self.canvas_sim.itemconfig(self.lbl_sim, image=self.frm_img)

    # Output
    def draw_output_window(self):
        self.output_line_nr = 0

        window = tk.Toplevel()
        window.state('zoomed')

        # Simulation frame
        self.frm_sim = tk.Frame(window, height=self.window_height / 2, width=self.window_width / 2, bg="red")

        lbl_id_sim = tk.Label(self.frm_sim, text="Simulation Frame")
        lbl_id_sim.pack()
        
        self.canvas_height = height=self.window_height / 3*2
        self.canvas_sim = tk.Canvas(self.frm_sim, height=self.canvas_height, width=self.canvas_height)
        self.canvas_sim.pack()
        self.lbl_sim = self.canvas_sim.create_image(0, 0, anchor="nw")

        # Output frame
        frm_output = tk.Frame(window, height=self.window_height / 2, width=self.window_width / 2, bg="yellow")

        lbl_id_parameters = tk.Label(frm_output, text="Output Frame")
        lbl_id_parameters.pack()

        self.txt_output = tk.Text(
            frm_output, height=15, width=70, cursor='watch')
        self.txt_output.config(wrap='none', state='disabled')
        self.txt_output.pack()

        self.txt_step_output = tk.Text(frm_output, height=5, width=70)
        self.txt_step_output.config(wrap='none', state='disabled')
        self.txt_step_output.pack()

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

    def update_displayed_step(self, step, customers_in_store=-1, customers_in_queue=-1, emitting_customers_in_store=-1,
                              exposure=-1):
        if self.txt_step_output == 0:
            raise Exception("Step output text is undefined")
        else:
            if any(x == -1 for x in [customers_in_store, customers_in_queue, emitting_customers_in_store, exposure]):
                print("todo")
                # TODO: Get data from store_data.dat file

            output = " Step: {}\n" \
                     "  Customers in store:            {:.0f}\n" \
                     "  Customers heading for exit:    {:.0f}\n" \
                     "  Infected customers:            {:.0f}\n" \
                     "  Exposure on healthy customers: {:.3f}".format(step, customers_in_store, customers_in_queue,
                                                                      emitting_customers_in_store, exposure)

            self.txt_step_output.config(state='normal')
            self.txt_step_output.delete('1.0', tk.END)
            self.txt_step_output.insert(tk.END, output)
            self.txt_step_output.config(state='disabled')
