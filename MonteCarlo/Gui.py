import tkinter as tk
import threading
import imageio
import shutil
import Params
import os

from tkinter import *
from PIL import Image, ImageTk
from Simulation import *
from StoreLayout import *
from tkinter import messagebox


class Gui:
    def __init__(self):
        self.txt_output = 0
        self.txt_step_output = 0
        self.output_line_nr = 0
        self.simulating = True
        self.window_width = 1600
        self.window_height = 800

        Params.set_params()

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

        frm_parameters_input = tk.Frame(frm_parameters, relief=tk.SUNKEN, borderwidth=2)
        frm_parameters_input.pack()

        # Seed
        lbl_seed = tk.Label(frm_parameters_input, text="Seed:")
        ent_seed = tk.Entry(frm_parameters_input, width=20)
        ent_seed.insert(0, 888892)
        lbl_seed.grid(row=0, column=0, sticky="e")
        ent_seed.grid(row=0, column=1)

        # Nr. of Customers
        lbl_nr_customers = tk.Label(frm_parameters_input, text="Nr. of Customers:")
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
        lbl_prob_inf = tk.Label(frm_parameters_input, text="Prob. Infected Customer:")
        ent_prob_inf = tk.Entry(frm_parameters_input, width=20)
        ent_prob_inf.insert(0, 0.01)
        lbl_prob_inf.grid(row=3, column=0, sticky="e")
        ent_prob_inf.grid(row=3, column=1)

        # Prob. New Customer
        lbl_prob_new = tk.Label(frm_parameters_input, text="Prob. New Customer:")
        ent_prob_new = tk.Entry(frm_parameters_input, width=20)
        ent_prob_new.insert(0, 0.2)
        lbl_prob_new.grid(row=4, column=0, sticky="e")
        ent_prob_new.grid(row=4, column=1)

        params = eval(os.environ["PARAMS"])

        # Diff Coef
        lbl_diff_coef = tk.Label(frm_parameters_input, text="Diffusion Coefficient:")
        ent_diff_coef = tk.Entry(frm_parameters_input, width=20)
        ent_diff_coef.insert(0, params["DIFFCOEFF"])
        lbl_diff_coef.grid(row=21, column=0, sticky="e")
        ent_diff_coef.grid(row=21, column=1)

        # Run button
        btn_run = tk.Button(frm_parameters,
                            text="Run",
                            command=lambda: self.run_simulation(
                                seed=ent_seed.get(),
                                nr_customers=ent_nr_customers.get(),
                                max_steps=ent_max_steps.get(),
                                prob_inf=ent_prob_inf.get(),
                                prob_new=ent_prob_new.get(),
                                store_layout=store_layout_canvas,
                                diff_coef=ent_diff_coef.get()
                            ))
        btn_run.pack()

        frm_layout.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        frm_parameters.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        window.mainloop()

    def validate_input(self, seed, nr_customers, max_steps, prob_inf, prob_new, diff_coef):
        try:
            int_seed = int(seed)
            int_nr_customers = int(nr_customers)
            int_max_steps = int(max_steps)
            float_prob_inf = float(prob_inf)
            float_prob_new = float(prob_new)
            float_diff_coef = float(diff_coef)

            if any(x <= 0 for x in (int_seed, int_nr_customers, int_max_steps, float_prob_inf, float_prob_new, float_diff_coef)) \
                    or any(x >= 1 for x in (float_prob_inf, float_prob_new, float_diff_coef)):
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

    # updates output window after simulation is done
    def update_output_window(self):
        self.txt_output.config(cursor='arrow')
        self.txt_output.pack()
        self.update_output("Simulation finished!")
        # More stuff TODO after simulation

    def run_simulation(self, seed, nr_customers, max_steps, prob_inf, prob_new, store_layout, diff_coef):
        # clear the figures of previous simulations
        self.clear_folder()

        input_valid = self.validate_input(
            seed=seed,
            nr_customers=nr_customers,
            max_steps=max_steps,
            prob_inf=prob_inf,
            prob_new=prob_new,
            diff_coef=diff_coef
        )

        if input_valid:
            self.label = self.draw_output_window()

            initial_output_text = "Running simulation with the following parameters:\n" \
                                  "  Seed:                    {}\n" \
                                  "  Nr. of Customers:        {}\n" \
                                  "  Max Steps:               {}\n" \
                                  "  Prob. Infected Customer: {}\n" \
                                  "  Prob. New Customer:      {}\n" \
                                  "  Diffusion Coefficient:   {}".format(seed, nr_customers, max_steps, prob_inf, prob_new, diff_coef)

            self.update_output(initial_output_text)

            # Stream video
            def stream():
                video = imageio.get_reader("video.mkv")
                for image in video.iter_data():
                    image_frame = Image.fromarray(image)          
                    frame_image = ImageTk.PhotoImage(image_frame.resize((int(self.window_width/2), int(self.window_height/1.5))))
                    self.label.config(image=frame_image)
                    self.label.image = frame_image

            def run_sim():
                # Update global params
                params = eval(os.environ["Params"])
                params["DIFFCOEFF"] = float(diff_coef)
                os.environ["PARAMS"] = str(params)
                print(os.environ)

                sim = Simulation(
                    self,
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
                sim.runSimulation()
                self.simulating = False
                self.update_output_window()
                stream()
            
            # load the already simulated figures
            def load_figures():
                while self.simulating:
                    # when simFigures has at least 2 figures
                    if len(os.listdir('simFigures')) > 1:
                        figureList = glob.glob('simFigures/simFigure_%s_*'%seed + '.png')
                        latest_figure = figureList[-2] # get second last element  
                        img = Image.open(latest_figure)
                        frm_img = ImageTk.PhotoImage(img.resize((int(self.window_width/2), int(self.window_height/1.5))))
                        self.label.config(image=frm_img)
                        self.label.image = frm_img

            # Start simulation in new thread so GUI doesn't block
            threading.Thread(target=run_sim).start()
            t = threading.Thread(target=load_figures)
            t.setDaemon(True)
            t.start()
        
    #updates simulation frame
    def update_figure(self, label, id, step):
        image = Image.open('simFigures/simFigure_%d_%07d.png'%(id, step))
        img = ImageTk.PhotoImage(image.resize((int(self.window_width/2), int(self.window_height/1.5))))
        label.configure(image=img)
        label.image = img

    # Output
    def draw_output_window(self):
        self.output_line_nr = 0

        window = tk.Toplevel()
        window.state('zoomed')

        # Simulation frame
        frm_sim = tk.Frame(window, height=self.window_height/2, width=self.window_width/2, bg="red")

        lbl_id_sim = tk.Label(frm_sim, text="Simulation Frame")
        lbl_id_sim.pack()
        btn_frame = tk.Button(frm_sim, text="Show simulation frame", command=lambda: self.update_figure(lbl_id_sim, 888892, 1))
        btn_frame.pack()

        # Output frame
        frm_output = tk.Frame(window, height=self.window_height/2, width=self.window_width/2, bg="yellow")

        lbl_id_parameters = tk.Label(frm_output, text="Output Frame")
        lbl_id_parameters.pack()

        self.txt_output = tk.Text(frm_output, height=15, width=70, cursor='watch')
        self.txt_output.config(wrap='none', state='disabled')
        self.txt_output.pack()

        self.txt_step_output = tk.Text(frm_output, height=5, width=70)
        self.txt_step_output.config(wrap='none', state='disabled')
        self.txt_step_output.pack()

        frm_sim.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        frm_output.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True)

        return lbl_id_sim

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

    def update_displayed_step(self, step, customers_in_store=-1, customers_in_queue=-1, emitting_customers_in_store=-1, exposure=-1):
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
                     "  Exposure on healthy customers: {:.3f}".format(step, customers_in_store, customers_in_queue, emitting_customers_in_store, exposure)

            self.txt_step_output.config(state='normal')
            self.txt_step_output.delete('1.0', tk.END)
            self.txt_step_output.insert(tk.END, output)
            self.txt_step_output.config(state='disabled')
