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
    def update_output_window(self, storePlot):
        self.txt_output.config(cursor='arrow')
        self.txt_output.pack()
        self.lbl_sim.config(cursor='arrow')
        self.lbl_sim.pack()
        self.update_output("Simulation finished!")
        steps = int(self.max_steps) - 1
        length = max(int((self.window_width/2)/steps), 10)
        slider = tk.Scale(self.frm_sim, from_=0, to=steps, length=int(self.window_width/2), sliderlength=length, orient=tk.HORIZONTAL, command=self.update_figure)
        slider.pack()
        btn_export = tk.Button(self.frm_sim, text="Export video", command=lambda: self.save_file())
        btn_export.pack()
        self.storePlot = storePlot
        self.update_storeplot()
        self.stream()
        # More stuff TODO after simulation

    def update_storeplot(self):
        window = tk.Toplevel()
        window.geometry('{}x{}'.format(self.window_width, self.window_height))

        step_slider = tk.Scale(window, from_=0, to=50)
        step_slider.set(0)
        step_slider.pack()
        fig = self.storePlot.showStore(step_slider.get())
        bar = FigureCanvasTkAgg(fig, window)
        bar.get_tk_widget().pack()

    # opens a 'save-as' window to save the video
    def save_file(self):
        file = asksaveasfile(mode="wb", title="Save Figure", defaultextension=".mkv", filetypes = (("mkv files",".mkv"),("all files",".*")))
        if file is None:
            return None
        vid_to_save = open("video.mkv","rb").read()
        file.write(vid_to_save)
        file.close()

    def update_figure(self, value):
        image = Image.open('simFigures/simFigure_%s_%07d.png'%(self.seed, int(value)))
        img = ImageTk.PhotoImage(image.resize((int(self.window_width/2), int(self.window_height/1.5))))
        self.lbl_sim.configure(image=img)
        self.lbl_sim.image = img
    
    # load the already simulated figures
    def load_figures(self):
        while self.simulating:
            # when simFigures has at least 2 figures
            if len(os.listdir('simFigures')) > 1:
                figureList = glob.glob('simFigures/simFigure_%s_*'%self.seed + '.png')
                latest_figure = figureList[-2] # get second last element  
                img = Image.open(latest_figure)
                frm_img = ImageTk.PhotoImage(img.resize((int(self.window_width/2), int(self.window_height/1.5))))
                self.lbl_sim.config(image=frm_img)
                self.lbl_sim.image = frm_img

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
