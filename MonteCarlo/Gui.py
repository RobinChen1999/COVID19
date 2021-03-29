from tkinter import *
from tkinter import messagebox
import Params
from Simulation import *
from StoreLayout import *
from GuiOutput import *


class Gui:
    def __init__(self, tab_frame, count):
        self.frm_sim = 0
        self.lbl_sim = 0
        self.txt_output = 0
        self.txt_step_output = 0
        self.output_line_nr = 0
        self.simulating = True
        self.window_width = 1600
        self.window_height = 800
        self.count = count
        self.root = tab_frame

        Params.set_params()

    # Input window
    def draw_input_window(self):
        self.frm_input_window = ttk.Frame(self.root)
        self.frm_input_window.pack(side=tk.LEFT, fill=tk.Y)

        self.frm_output_window = ttk.Frame(self.root)
        self.frm_output_window.pack(side=tk.RIGHT, fill=tk.Y)

        # Parameters frame
        frm_parameters = ttk.Frame(self.frm_input_window)

        lbl_id_parameters = ttk.Label(frm_parameters, text="Parameters Frame")
        lbl_id_parameters.pack()

        # Layout frame
        frm_layout = ttk.Frame(self.frm_input_window)

        lbl_id_layout = ttk.Label(frm_layout, text="Layout Frame")
        lbl_id_layout.pack()

        self.store_layout_canvas = StoreLayout(frm_layout)
        self.store_layout_canvas.draw_store_layout()

        # Parameters tab
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
        params = eval(os.environ["PARAMS"])

        input_tab_control = ttk.Notebook(frm_parameters)

        def add_param_input(tab_root, index, label, value, description, callback=None):
            tab_root.grid_columnconfigure(0, minsize=column_size_text)
            tab_root.grid_columnconfigure(2, minsize=column_size_input)

            lbl = ttk.Label(tab_root, text=label)
            lbl.grid(row=index, column=0, sticky="w")

            desc = ttk.Label(tab_root, text="?")
            create_tool_tip(desc, description)
            desc.grid(row=index, column=1, sticky="e", padx=10)

            if callback is None:
                ent = ttk.Entry(tab_root)
                ent.insert(0, value)
            else:
                ent = ttk.Entry(tab_root, validate="key", validatecommand=(self.root.register(callback), '%P'))
                ent.insert(0, value)

            ent.grid(row=index, column=2, sticky="we")

            return ent

        # Simulation Tab
        tab_simulation = ttk.Frame(input_tab_control)

        seed = add_param_input(tab_simulation, 0, "Seed:", 888892,
                               "The seed is the id of the simulation.\n"
                               "This is used when generating random variables.\n"
                               "Rerunning a simulation with the same seed will use the same random variables.")

        max_steps = add_param_input(tab_simulation, 1, "Max Steps:", 100,
                                    "For how many steps the simulation will maximally run.")

        # Customer Tab
        tab_customer = ttk.Frame(input_tab_control)

        nr_customers = add_param_input(tab_customer, 0, "Nr. of Customers:", 100,
                                       "How many customers will enter the store.")

        prob_new_customer = add_param_input(tab_customer, 1, "Prob. New Customer:", 0.2,
                                            "Probability on each time step a new customer will enter the store.")

        prob_inf_customer = add_param_input(tab_customer, 2, "Prob. Infected Customer:", 0.01,
                                            "Probability of a new customer being infected.")

        prob_block_random_step = add_param_input(tab_customer, 3, "Prob. Random Step:", 0.8,
                                                 "Probability of customer taking a random step when their path is blocked.")

        prob_cough = add_param_input(tab_customer, 4, "Prob. Cough:", 0.0003,
                                     "Probability of a customer coughing per step.")

        plume_conc_cough = add_param_input(tab_customer, 5, "Aerosol Conc. When Coughing:", params["PLUMECONCINC"],
                                           "Aerosol concentration when a customer coughs.")

        max_shopping_list = add_param_input(tab_customer, 6, "Max Items on Shopping List:", 20,
                                            "Maximum number of items on a customer's shopping list.")

        # Exits Tab
        tab_exit = ttk.Frame(input_tab_control)

        self.lbl_exit_error = ttk.Label(tab_exit)
        self.lbl_exit_error.grid(row=10, column=0, columnspan=3, sticky="we")
        self.lbl_exit_error.grid_remove()

        nexits = None
        cashierd = None

        def update_nexits(value):
            ent = tk.Entry(None)
            ent.insert(0, value)
            self.update_exits(ent, cashierd)
            return True

        def update_cashierd(value):
            ent = tk.Entry(None)
            ent.insert(0, value)
            self.update_exits(nexits, ent)
            return True

        nexits = add_param_input(tab_exit, 0, "Nr. of Exits:", params["NEXITS"], "Number of exits in the store.",
                                 update_nexits)

        cashierd = add_param_input(tab_exit, 1, "Distance between exits:", params["CASHIERD"],
                                   "The distance between the exits.", update_cashierd)

        # Diffusion Tab
        tab_diffusion = ttk.Frame(input_tab_control)

        diff_coeff = add_param_input(tab_diffusion, 0, "Diffusion Coefficient:", params["DIFFCOEFF"],
                                     "Diffusion coefficient.")

        acsinkcoeff = add_param_input(tab_diffusion, 1, "Sink Coefficient:", params["ACSINKCOEFF"],
                                      "Coefficient for the sink term of the form: -k*c.")

        # Plume Tab
        tab_plume = ttk.Frame(input_tab_control)

        plume_lifetime = add_param_input(tab_plume, 0, "Plume Lifetime:", params["PLUMELIFETIME"],
                                         "Lifetime of plume for discrete plumes without diffusion.")

        plume_conc_cont = add_param_input(tab_plume, 2, "Continuous Aerosol Emission:", params["PLUMECONCCONT"],
                                          "Continuous aerosol emission.")

        # Add all tabs
        input_tab_control.add(tab_simulation, text="Simulation")
        input_tab_control.add(tab_customer, text="Customer")
        input_tab_control.add(tab_exit, text="Exits")
        input_tab_control.add(tab_diffusion, text="Diffusion")
        # input_tab_control.add(tab_plume, text="Plume")

        input_tab_control.pack(expand=0)

        frm_parameters_input = ttk.Frame(frm_parameters, relief=tk.SUNKEN, borderwidth=2)
        frm_parameters_input.pack()

        # Run button
        btn_run = ttk.Button(frm_parameters,
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
                                 exit_params={
                                     "nexits": nexits.get(),
                                     "cashierd": cashierd.get()
                                 },
                                 diffusion_params={
                                     "diff_coeff": diff_coeff.get(),
                                     "acsinkcoeff": acsinkcoeff.get()
                                 },
                                 plume_params={
                                     "plume_lifetime": plume_lifetime.get(),
                                     "plume_conc_cough": plume_conc_cough.get(),
                                     "plume_conc_cont": plume_conc_cont.get()
                                 },
                                 store_layout=self.store_layout_canvas
                             ))
        btn_run.pack()

        frm_layout.pack(fill=tk.BOTH, side=tk.LEFT, anchor="nw", expand=True)
        frm_parameters.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True)
        

    def validate_input(self, simulation_params, customer_params, diffusion_params, plume_params, store_empty):
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
            if self.lbl_exit_error.cget("text") != "":
                raise Exception()
            # Other validation is done in update_exits
        except:
            tk.messagebox.showerror("Error!", "Invalid input in Exits tab!")
            return False

        # Diffusion
        try:
            float_diff_coeff = float(diffusion_params["diff_coeff"])
            float_acsinkcoeff = float(diffusion_params["acsinkcoeff"])

            if any(x <= 0 for x in (float_diff_coeff, float_acsinkcoeff)) or \
                    any(x >= 1 for x in (float_diff_coeff, float_acsinkcoeff)):
                raise Exception()
        except:
            tk.messagebox.showerror("Error!", "Invalid input in Diffusion tab!")
            return False

        # Plume
        try:
            int_plume_lifetime = int(plume_params["plume_lifetime"])
            float_plume_conc_cough = float(plume_params["plume_conc_cough"])
            float_plume_conc_cont = float(plume_params["plume_conc_cont"])

            if any(x <= 0 for x in (int_plume_lifetime, float_plume_conc_cough, float_plume_conc_cont)):
                raise Exception()
        except:
            tk.messagebox.showerror("Error!", "Invalid input in Plume tab!")
            return False
        
        # Empty store
        if store_empty:
            tk.messagebox.showerror("Error!", "The store is empty! Please add at least one shelf.")
            return False

        else:
            return True

    def run_simulation(self, simulation_params, customer_params, exit_params, diffusion_params, plume_params,
                       store_layout):
        self.simulating = True

        input_valid = self.validate_input(
            simulation_params=simulation_params,
            customer_params=customer_params,
            diffusion_params=diffusion_params,
            plume_params=plume_params,
            store_empty=store_layout.check_store_empty()
        )

        if input_valid:
            outputGui = GuiOutput(self.frm_output_window, simulation_params, self.count, customer_params["nr_customers"])

            def run_sim():
                # Update global params
                params = eval(os.environ["Params"])

                # Customer
                params["BLOCKRANDOMSTEP"] = float(customer_params["prob_block_random_step"])
                params["PROBSPREADPLUME"] = float(customer_params["prob_cough"])
                params["MAXSHOPPINGLIST"] = int(customer_params["max_shopping_list"])

                # Exits
                params["NEXITS"] = int(exit_params["nexits"])
                params["CASHIERD"] = int(exit_params["cashierd"])

                # Diffusion
                params["DIFFCOEFF"] = float(diffusion_params["diff_coeff"])
                params["ACSINKCOEFF"] = float(diffusion_params["acsinkcoeff"])

                # Plume
                params["PLUMELIFETIME"] = int(plume_params["plume_lifetime"])
                params["PLUMECONCINC"] = float(plume_params["plume_conc_cough"])
                params["PLUMECONCCONT"] = float(plume_params["plume_conc_cont"])

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
                store_plot = sim.runSimulation()
                outputGui.simulating = False
                outputGui.update_on_sim_finished(store_plot)

            # Start simulation in new thread so GUI doesn't block
            threading.Thread(target=run_sim, daemon=True).start()


    def update_exits(self, _nexits, _cashierd):
        params = eval(os.environ["PARAMS"])

        if all(x is not None for x in [_nexits, _cashierd]):
            # Validate input
            error_message = "Invalid Input!"

            try:
                str_nexits = _nexits.get()
                str_cashierd = _cashierd.get()

                int_nexits = int(str_nexits) if str_nexits != "" else 0
                int_cashierd = int(str_cashierd) if str_cashierd != "" else 0

                if int_nexits <= 0:
                    error_message = "Nr. of Exits should be higher than 0!"
                    raise Exception()

                if int_cashierd <= 2:
                    error_message = "Distance between exits should be higher than 2!"
                    raise Exception()

                if (int_nexits - 1) * int_cashierd >= 95:
                    error_message = "Exits are placed outside of the store!"
                    raise Exception()

                self.lbl_exit_error.config(text="")
                self.lbl_exit_error.grid_remove()
                self.update_layout_entrance_exits(int_nexits, int_cashierd)
            except:
                self.lbl_exit_error.config(text=error_message)
                self.lbl_exit_error.grid()
                return False
        else:
            self.update_layout_entrance_exits(params["NEXITS"], params["CASHIERD"])
        return True

    def update_layout_entrance_exits(self, nexits, cashierd):
        self.store_layout_canvas.draw_entrance_exits(nexits, cashierd)


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
