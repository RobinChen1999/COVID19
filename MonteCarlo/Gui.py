from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import Params
from Simulation import *
from StoreLayout import *
from GuiOutput import *

class Gui:
    def __init__(self):
        self.frm_sim = 0
        self.lbl_sim = 0
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

    def run_simulation(self, simulation_params, customer_params, exit_params, diffusion_params, plume_params,
                       store_layout):
        self.simulating = True
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
            outputGui = GuiOutput(simulation_params)

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
                    outputGui,
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
                outputGui.simulating = False
                outputGui.update_output_window()

            # Start simulation in new thread so GUI doesn't block
            threading.Thread(target=run_sim).start()


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
