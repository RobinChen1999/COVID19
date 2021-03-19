import tkinter as tk
import threading
import imageio
import shutil

from tkinter import *
from PIL import Image, ImageTk
from Simulation import *
from StoreLayout import *
from GuiOutput import *
from tkinter import messagebox


class Gui:
    def __init__(self):
        self.txt_output = 0
        self.output_line_nr = 0
        self.simulating = True
        self.window_width = 1600
        self.window_height = 800

    # Input window
    def draw_input_window(self):
        window = tk.Tk()
        window.geometry('{}x{}'.format(800, 400))

        # Layout frame
        frm_layout = tk.Frame(window, bg="red")

        lbl_id_layout = tk.Label(frm_layout, text="Layout Frame")
        lbl_id_layout.pack()

        store_layout_canvas = StoreLayout(frm_layout)
        store_layout_canvas.draw_store_layout()

        # Parameters frame
        frm_parameters = tk.Frame(window, bg="yellow")

        lbl_id_parameters = tk.Label(frm_parameters, text="Parameters Frame")
        lbl_id_parameters.pack()

        frm_parameters_input = tk.Frame(
            frm_parameters, relief=tk.SUNKEN, borderwidth=2)
        frm_parameters_input.pack()

        # Seed
        lbl_seed = tk.Label(frm_parameters_input, text="Seed:")
        ent_seed = tk.Entry(frm_parameters_input, width=20)
        ent_seed.insert(0, 888892)
        lbl_seed.grid(row=0, column=0, sticky="e")
        ent_seed.grid(row=0, column=1)

        # Nr. of Customers
        lbl_nr_customers = tk.Label(
            frm_parameters_input, text="Nr. of Customers:")
        ent_nr_customers = tk.Entry(frm_parameters_input, width=20)
        ent_nr_customers.insert(0, 10000)
        lbl_nr_customers.grid(row=1, column=0, sticky="e")
        ent_nr_customers.grid(row=1, column=1)

        # Max Steps
        lbl_max_steps = tk.Label(frm_parameters_input, text="Max Steps:")
        ent_max_steps = tk.Entry(frm_parameters_input, width=20)
        ent_max_steps.insert(0, 500)
        lbl_max_steps.grid(row=2, column=0, sticky="e")
        ent_max_steps.grid(row=2, column=1)

        # Prob. Infected Customer
        lbl_prob_inf = tk.Label(frm_parameters_input,
                                text="Prob. Infected Customer:")
        ent_prob_inf = tk.Entry(frm_parameters_input, width=20)
        ent_prob_inf.insert(0, 0.01)
        lbl_prob_inf.grid(row=3, column=0, sticky="e")
        ent_prob_inf.grid(row=3, column=1)

        # Prob. New Customer
        lbl_prob_new = tk.Label(frm_parameters_input,
                                text="Prob. New Customer:")
        ent_prob_new = tk.Entry(frm_parameters_input, width=20)
        ent_prob_new.insert(0, 0.2)
        lbl_prob_new.grid(row=4, column=0, sticky="e")
        ent_prob_new.grid(row=4, column=1)

        # Run button
        btn_run = tk.Button(frm_parameters,
                            text="Run",
                            command=lambda: self.run_simulation(
                                seed=ent_seed.get(),
                                nr_customers=ent_nr_customers.get(),
                                max_steps=ent_max_steps.get(),
                                prob_inf=ent_prob_inf.get(),
                                prob_new=ent_prob_new.get(),
                                store_layout=store_layout_canvas
                            ))
        btn_run.pack()

        frm_layout.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        frm_parameters.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        window.mainloop()

    def validate_input(self, seed, nr_customers, max_steps, prob_inf, prob_new):
        try:
            int_seed = int(seed)
            int_nr_customers = int(nr_customers)
            int_max_steps = int(max_steps)
            int_prob_inf = float(prob_inf)
            int_prob_new = float(prob_new)

            if any(x <= 0 for x in (int_seed, int_nr_customers, int_max_steps, int_prob_inf, int_prob_new)) \
                    or any(x >= 1 for x in (int_prob_inf, int_prob_new)):
                raise Exception()
        except:
            tk.messagebox.showerror("Error!", "Invalid input!")
            return False
        else:
            return True

    # clear contents of simFigures folder
    def clear_folder(self):
        dir = 'simFigures'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))

    def run_simulation(self, seed, nr_customers, max_steps, prob_inf, prob_new, store_layout):
        # clear the figures of previous simulations
        self.clear_folder()

        input_valid = self.validate_input(
            seed=seed,
            nr_customers=nr_customers,
            max_steps=max_steps,
            prob_inf=prob_inf,
            prob_new=prob_new
        )

        if input_valid:
            outputGui = GuiOutput(seed=seed,
                                  nr_customers=nr_customers,
                                  max_steps=max_steps,
                                  prob_inf=prob_inf,
                                  prob_new=prob_new)

            def run_sim():
                sim = Simulation(
                    outputGui,
                    int(seed),
                    101,
                    101,
                    25,
                    int(nr_customers),
                    outputLevel=1,
                    maxSteps=int(max_steps),
                    probInfCustomer=float(prob_inf),
                    probNewCustomer=float(prob_new),
                    imageName=store_layout.saveCanvas(),
                    useDiffusion=1,
                    dx=1.0)
                storePlot = sim.runSimulation()
                self.simulating = False
                outputGui.update_output_window(storePlot=storePlot)

            # load the already simulated figures
            def load_figures():
                while self.simulating:
                    # when simFigures has at least 2 figures
                    if len(os.listdir('simFigures')) > 1:
                        figureList = glob.glob(
                            'simFigures/simFigure_%s_*' % seed + '.png')
                        # get second last element
                        latest_figure = figureList[-2]
                        img = Image.open(latest_figure)
                        frm_img = ImageTk.PhotoImage(img.resize(
                            (int(self.window_width/2), int(self.window_height/1.5))))
                        outputGui.label.config(image=frm_img)
                        outputGui.label.image = frm_img

            # Start simulation in new thread so GUI doesn't block
            threading.Thread(target=run_sim).start()
            t = threading.Thread(target=load_figures)
            t.setDaemon(True)
            t.start()
