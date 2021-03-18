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
from tkinter import ttk


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

        def create_tool_tip(widget, text):
            tool_tip = ToolTip(widget)

            def enter(event):
                tool_tip.showtip(text)

            def leave(event):
                tool_tip.hidetip()

            widget.bind('<Enter>', enter)
            widget.bind('<Leave>', leave)

        column_size_text = 200
        column_size_input = 100
        img = ImageTk.PhotoImage(Image.open("questionmark.png").resize((15, 15)))
        params = eval(os.environ["PARAMS"])

        input_tab_control = ttk.Notebook(frm_parameters)

        def add_param_input(tab_root, index, label, value, description):
            tab_root.grid_columnconfigure(0, minsize=column_size_text)
            tab_root.grid_columnconfigure(2, minsize=column_size_input)

            lbl = tk.Label(tab_root, text=label)
            lbl.grid(row=index, column=0, sticky="w")

            desc = tk.Label(tab_root, image=img)
            create_tool_tip(desc, description)
            desc.grid(row=index, column=1, sticky="e")

            ent = tk.Entry(tab_root)
            ent.insert(0, value)
            ent.grid(row=index, column=2, sticky="we")

            return ent

        # Simulation Tab
        tab_simulation = ttk.Frame(input_tab_control)

        seed = add_param_input(tab_simulation, 0, "Seed:", 888892,
                               "The seed is the id of the simulation.\n"
                               "This is used when generating random variables.\n"
                               "Rerunning a simulation with the same seed will use the same random variables.")

        max_steps = add_param_input(tab_simulation, 1, "Max Steps:", 500,
                                    "For how many steps the simulation will maximally run.")

        # Customer Tab
        tab_customer = ttk.Frame(input_tab_control)

        nr_customers = add_param_input(tab_customer, 0, "Nr. of Customers:", 1000,
                                       "How many customers will enter the store.")

        prob_new_customer = add_param_input(tab_customer, 1, "Prob. New Customer:", 0.2,
                                            "Probability on each time step a new customer will enter the store.")

        prob_inf_customer = add_param_input(tab_customer, 2, "Prob. Infected Customer:", 0.01,
                                            "Probability of a new customer being infected.")

        prob_block_random_step = add_param_input(tab_customer, 3, "Prob. Random Step:", 0.8,
                                                 "Probability of customer taking a random step when their path is blocked.")

        prob_cough = add_param_input(tab_customer, 4, "Prob. Cough:", 0.0003,
                                     "Probability of a customer coughing per second.")

        max_shopping_list = add_param_input(tab_customer, 5, "Max Items on Shopping List:", 20,
                                            "Maximum number of items on a customer's shopping list.")

        # Exits Tab
        tab_exit = ttk.Frame(input_tab_control)
        # TODO: Add

        # Diffusion Tab
        tab_diffusion = ttk.Frame(input_tab_control)

        diff_coeff = add_param_input(tab_diffusion, 0, "Diffusion Coefficient:", params["DIFFCOEFF"],
                                     "Diffusion coefficient.")
        # TODO: Add

        # Plume Tab
        tab_plume = ttk.Frame(input_tab_control)
        # TODO: Add

        # Add all tabs
        input_tab_control.add(tab_simulation, text="Simulation")
        input_tab_control.add(tab_customer, text="Customer")
        input_tab_control.add(tab_exit, text="Exits")
        input_tab_control.add(tab_diffusion, text="Diffusion")
        input_tab_control.add(tab_plume, text="Plume")

        input_tab_control.pack(expand=0)

        frm_parameters_input = tk.Frame(frm_parameters, relief=tk.SUNKEN, borderwidth=2)
        frm_parameters_input.pack()

        # Run button
        btn_run = tk.Button(frm_parameters,
                            text="Run",
                            command=lambda: self.run_simulation(
                                simulation_params={
                                    "seed": seed.get(),
                                    "max_steps": max_steps.get()
                                },
                                customer_params={
                                    "nr_customers": nr_customers.get(),
                                    "prob_new_customer": prob_new_customer.get(),
                                    "prob_inf_customer": prob_inf_customer.get(),
                                    "prob_block_random_step": prob_block_random_step.get(),
                                    "prob_cough": prob_cough.get(),
                                    "max_shopping_list": max_shopping_list.get()
                                },
                                exit_params={},
                                diffusion_params={
                                    "diff_coeff": diff_coeff.get(),
                                },
                                plume_params={},
                                store_layout=store_layout_canvas
                            ))
        btn_run.pack()

        frm_layout.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        frm_parameters.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        window.mainloop()

    def validate_input(self, simulation_params, customer_params, exit_params, diffusion_params, plume_params):
        # Simulation
        try:
            int_seed = int(simulation_params["seed"])
            int_max_steps = int(simulation_params["max_steps"])

            if any(x <= 0 for x in (int_seed, int_max_steps)):
                raise Exception()
        except:
            tk.messagebox.showerror("Error!", "Invalid input in Simulation tab!")
            return False

        # Customer
        try:
            int_nr_customers = int(customer_params["nr_customers"])
            float_prob_new_customer = float(customer_params["prob_new_customer"])
            float_prob_inf_customer = float(customer_params["prob_inf_customer"])
            float_prob_block_random_step = float(customer_params["prob_block_random_step"])
            float_prob_cough = float(customer_params["prob_cough"])
            int_max_shopping_list = int(customer_params["max_shopping_list"])

            if any(x <= 0 for x in (
                    int_nr_customers, float_prob_new_customer, float_prob_inf_customer, float_prob_block_random_step,
                    float_prob_cough, int_max_shopping_list)) \
                    or any(x >= 1 for x in (
                    float_prob_new_customer, float_prob_inf_customer, float_prob_block_random_step, float_prob_cough)):
                raise Exception()
        except:
            tk.messagebox.showerror("Error!", "Invalid input in Customer tab!")
            return False

        # Exit
        try:
            # TODO: Add
            True
        except:
            tk.messagebox.showerror("Error!", "Invalid input in Exit tab!")
            return False

        # Diffusion
        try:
            float_diff_coeff = float(diffusion_params["diff_coeff"])

            if float_diff_coeff <= 0 or float_diff_coeff >= 1:
                raise Exception()
        except:
            tk.messagebox.showerror("Error!", "Invalid input in Diffusion tab!")
            return False

        # Plume
        try:
            # TODO: Add
            True
        except:
            tk.messagebox.showerror("Error!", "Invalid input in Plume tab!")
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

    def run_simulation(self, simulation_params, customer_params, exit_params, diffusion_params, plume_params,
                       store_layout):
        # clear the figures of previous simulations
        self.clear_folder()

        input_valid = self.validate_input(
            simulation_params=simulation_params,
            customer_params=customer_params,
            exit_params=exit_params,
            diffusion_params=diffusion_params,
            plume_params=plume_params
        )

        if input_valid:
            self.label = self.draw_output_window()

            # initial_output_text = "Running simulation with the following parameters:\n" \
            #                       "  Seed:                    {}\n" \
            #                       "  Nr. of Customers:        {}\n" \
            #                       "  Max Steps:               {}\n" \
            #                       "  Prob. Infected Customer: {}\n" \
            #                       "  Prob. New Customer:      {}\n" \
            #                       "  Diffusion Coefficient:   {}".format(seed, nr_customers, max_steps, prob_inf,
            #                                                              prob_new, diff_coeff)

            initial_output_text = "Running simulation"
            self.update_output(initial_output_text)

            # Stream video
            def stream():
                video = imageio.get_reader("video.mkv")
                for image in video.iter_data():
                    image_frame = Image.fromarray(image)
                    frame_image = ImageTk.PhotoImage(
                        image_frame.resize((int(self.window_width / 2), int(self.window_height / 1.5))))
                    self.label.config(image=frame_image)
                    self.label.image = frame_image

            def run_sim():
                # Update global params
                params = eval(os.environ["Params"])

                # Customer
                params["BLOCKRANDOMSTEP"] = float(customer_params["prob_block_random_step"])
                params["PROBSPREADPLUME"] = float(customer_params["prob_cough"])
                params["MAXSHOPPINGLIST"] = int(customer_params["max_shopping_list"])

                # Diffusion
                params["DIFFCOEFF"] = float(diffusion_params["diff_coeff"])

                os.environ["PARAMS"] = str(params)

                sim = Simulation(
                    self,
                    int(simulation_params["seed"]),
                    101,
                    101,
                    25,
                    int(customer_params["nr_customers"]),
                    outputLevel=1,
                    maxSteps=int(simulation_params["max_steps"]),
                    probInfCustomer=float(customer_params["prob_inf_customer"]),
                    probNewCustomer=float(customer_params["prob_new_customer"]),
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
                        figureList = glob.glob('simFigures/simFigure_%s_*' % simulation_params["seed"] + '.png')
                        latest_figure = figureList[-2]  # get second last element
                        img = Image.open(latest_figure)
                        frm_img = ImageTk.PhotoImage(
                            img.resize((int(self.window_width / 2), int(self.window_height / 1.5))))
                        self.label.config(image=frm_img)
                        self.label.image = frm_img

            # Start simulation in new thread so GUI doesn't block
            threading.Thread(target=run_sim).start()
            t = threading.Thread(target=load_figures)
            t.setDaemon(True)
            t.start()

    # updates simulation frame
    def update_figure(self, label, id, step):
        image = Image.open('simFigures/simFigure_%d_%07d.png' % (id, step))
        img = ImageTk.PhotoImage(image.resize((int(self.window_width / 2), int(self.window_height / 1.5))))
        label.configure(image=img)
        label.image = img

    # Output
    def draw_output_window(self):
        self.output_line_nr = 0

        window = tk.Toplevel()
        window.state('zoomed')

        # Simulation frame
        frm_sim = tk.Frame(window, height=self.window_height / 2, width=self.window_width / 2, bg="red")

        lbl_id_sim = tk.Label(frm_sim, text="Simulation Frame")
        lbl_id_sim.pack()
        btn_frame = tk.Button(frm_sim, text="Show simulation frame",
                              command=lambda: self.update_figure(lbl_id_sim, 888892, 1))
        btn_frame.pack()

        # Output frame
        frm_output = tk.Frame(window, height=self.window_height / 2, width=self.window_width / 2, bg="yellow")

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
        self.tip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
