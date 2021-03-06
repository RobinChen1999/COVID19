from GuiOutput import *
from Simulation import *
from StoreLayout import *
import Params

import tkinter as tk
from tkinter import messagebox, ttk
import os
import threading


class Gui:
    def __init__(self, tab_frame, frm_buttons, count):
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
        self.frm_buttons = frm_buttons
        self.outputGui = None

        Params.set_params()

    # Input window
    def draw_input_window(self):

        # tooltip
        def create_tool_tip(widget, text):
            tool_tip = ToolTip(widget)

            def enter(event):
                tool_tip.showtip(text)

            def leave(event):
                tool_tip.hidetip()

            widget.bind('<Enter>', enter)
            widget.bind('<Leave>', leave)

        # Parameters frame
        frm_parameters = ttk.Frame(self.root)

        # Layout frame
        self.frm_layout = ttk.Frame(self.root)

        lbl_id_layout = ttk.Label(self.frm_layout, text="Draw your store layout", style='Header.TLabel', font=('Helvetica', 14))
        lbl_id_layout.grid(row=0, column=0, pady=10, sticky='w')

        self.store_layout_canvas = StoreLayout(self.frm_layout)
        self.store_layout_canvas.draw_store_layout()

        def show_hide_grid():
            self.remove_focus()
            self.store_layout_canvas.hide_grid_lines()

        # button to show/hide the grid
        self.buttons_store_grid = ttk.Frame(self.root)
        self.buttons_store_grid.grid(row=0, column=1)
        btn_grid = ttk.Checkbutton(self.buttons_store_grid,
                                        text="Show Grid",
                                        variable=self.store_layout_canvas.show_grid,
                                        onvalue=1, offvalue=0,
                                        command=show_hide_grid)
        btn_grid.pack(side=tk.LEFT, padx=20)

        def remove_shelves():
            self.remove_focus()
            self.store_layout_canvas.clear_shelves()

        btn_clear_shelves = ttk.Button(self.buttons_store_grid,
                                       text="Remove All Shelves",
                                       command=remove_shelves)
        btn_clear_shelves.pack(side=tk.RIGHT, padx=10)

        def draw_default_layout():
            self.remove_focus()
            self.store_layout_canvas.draw_initial_layout()

        btn_default_layout = ttk.Button(self.buttons_store_grid,
                                       text="Draw Default Layout",
                                       command=draw_default_layout)
        btn_default_layout.pack(side=tk.RIGHT)

        # Parameters tab
        column_size_text = 200
        params = eval(os.environ["PARAMS"])

        input_tab_control = ttk.Notebook(frm_parameters, padding=(0, 20, 0, 0), takefocus=False)
        input_tab_control.bind("<<NotebookTabChanged>>", lambda event: self.remove_focus())
        self.params = []

        def add_param_input(tab_root, index, label, value, description, callback=None):
            tab_root.grid_columnconfigure(0, minsize=column_size_text)

            lbl = ttk.Label(tab_root, text=label)
            lbl.grid(row=index, column=0, sticky="w", padx=10, pady=10)

            desc = ttk.Label(tab_root, text="?")
            create_tool_tip(desc, description)
            desc.grid(row=index, column=1, sticky="e", padx=5)

            if callback is None:
                ent = ttk.Entry(tab_root, justify='right', width=8)
                ent.insert(0, value)
            else:
                ent = ttk.Entry(tab_root, justify='right', width=8, validate="key", validatecommand=(self.root.register(callback), '%P'))
                ent.insert(0, value)

            self.params.append(ent)
            ent.grid(row=index, column=2, sticky="e", padx=5)

            return ent

        def add_param_label(tab_root, row, text):
            lbl = ttk.Label(tab_root, text=text, font=('Helvetica', 11), padding=(0, 8, 0, 0))
            lbl.grid(row=row, column=0, columnspan=3)

        # Default Tab
        tab_default = ttk.Frame(input_tab_control)

        add_param_label(tab_default, 0, "Simulation")

        max_steps = add_param_input(tab_default, 2, "Max Steps:", 1500,
                                    "For how many steps the simulation will maximally run.\n"
                                    "Should be an integer larger than 0.")

        add_param_label(tab_default, 10, "Customers")

        nr_customers = add_param_input(tab_default, 11, "Nr. of Customers:", 100,
                                       "How many customers will enter the store.\n"
                                       "Should be an integer larger than 0.")

        prob_inf_customer = add_param_input(tab_default, 12, "Prob. Infected Customer:", 0.05,
                                            "Probability of a new customer being infected.\n"
                                            "Should be a number between 0 and 1.")

        max_shopping_list = add_param_input(tab_default, 13, "Max Items on Shopping List:", 20,
                                            "Maximum number of items on a customer's shopping list.\n"
                                            "Should be an integer larger than 0.")

        lbl_facemasks = ttk.Label(tab_default, text='Face Masks:')
        lbl_facemasks.grid(row=14, column=0, sticky="w", padx=10, pady=10)

        desc_facemasks = ttk.Label(tab_default, text="?")
        create_tool_tip(desc_facemasks, "Whether customers are wearing face masks. \n"
                                        "This reduces the emission of aerosols by 50%")
        desc_facemasks.grid(row=14, column=1, sticky="e", padx=5)

        chk_facemasks_enabled = tk.IntVar()
        self.chk_facemasks = ttk.Checkbutton(tab_default, command=self.remove_focus, variable=chk_facemasks_enabled)
        self.chk_facemasks.grid(row=14, column=2, sticky='we', padx=5)

        add_param_label(tab_default, 20, "Entrance / Exits")

        frm_entrance_exit = ttk.Frame(tab_default)
        frm_entrance_exit.grid(row=21, column=0, columnspan=3)

        def handle_nr_exits(value):
            if not float(value) % 1 == 0:
                nr_exits = round(float(value))

                self.lbl_nr_exits_value.configure(text=nr_exits)

                # Update distance slider
                if nr_exits != 1:
                    self.scl_d_exits.state(['!disabled'])
                    self.lbl_d_exits_value.configure(text=int(self.scl_d_exits.get()))
                    allowed_d_exits = 95 / (nr_exits - 1)
                    self.scl_d_exits.configure(to=int(allowed_d_exits))
                else:
                    self.scl_d_exits.state(['disabled'])
                    self.lbl_d_exits_value.configure(text=0)

                self.update_layout_entrance_exits(nr_exits, int(self.scl_d_exits.get()))
                self.scl_nr_exits.set(nr_exits)

        def handle_d_exits(value):
            if not float(value) % 1 == 0:
                d_exits = round(float(value))

                self.lbl_d_exits_value.configure(text=d_exits)

                # Update nr slider
                allowed_nr_exits = 95 / d_exits + 1
                self.scl_nr_exits.configure(to=int(allowed_nr_exits))

                self.update_layout_entrance_exits(int(self.scl_nr_exits.get()), d_exits)
                self.scl_d_exits.set(d_exits)

        # Column Weights
        frm_entrance_exit.columnconfigure(0, weight=1)
        frm_entrance_exit.columnconfigure(1, weight=1)
        frm_entrance_exit.columnconfigure(2, weight=1)

        # Initial values
        initial_nr_exits = params['NEXITS']
        initial_d_exits = params['CASHIERD']
        initial_allowed_nr_exits = 95 / initial_d_exits + 1
        initial_allowed_d_exits = 95 / (initial_nr_exits - 1)

        self.update_layout_entrance_exits(initial_nr_exits, initial_d_exits)

        lbl_nr_exits = ttk.Label(frm_entrance_exit, text="Number of exits:")
        lbl_nr_exits.grid(row=0, column=0, sticky='w', padx=10, pady=10)

        self.lbl_nr_exits_value = ttk.Label(frm_entrance_exit, text=initial_nr_exits)
        self.lbl_nr_exits_value.grid(row=0, column=1)

        self.scl_nr_exits = ttk.Scale(frm_entrance_exit, length=100, orient=tk.HORIZONTAL, from_=1, to=initial_allowed_nr_exits,
                                      value=initial_nr_exits, command=handle_nr_exits)
        self.scl_nr_exits.grid(row=0, column=2, sticky='e', padx=10)

        lbl_d_exits = ttk.Label(frm_entrance_exit, text="Distance between exits:")
        lbl_d_exits.grid(row=1, column=0, sticky='w', padx=10)

        self.lbl_d_exits_value = ttk.Label(frm_entrance_exit, text=initial_d_exits)
        self.lbl_d_exits_value.grid(row=1, column=1)

        self.scl_d_exits = ttk.Scale(frm_entrance_exit, length=100, orient=tk.HORIZONTAL, from_=3, to=initial_allowed_d_exits,
                                      value=initial_d_exits, command=handle_d_exits)
        self.scl_d_exits.grid(row=1, column=2, sticky='e', padx=10)

        # Advanced Tab
        tab_advanced = ttk.Frame(input_tab_control)

        add_param_label(tab_advanced, 0, "Simulation")

        seed = add_param_input(tab_advanced, 1, "Seed:", 888892,
                               "The seed is used when generating random variables.\n"
                               "Rerunning a simulation with the same seed will use the same random variables.\n"
                               "Should be an integer larger than 0.")

        add_param_label(tab_advanced, 10, "Customers")

        prob_new_customer = add_param_input(tab_advanced, 11, "Prob. New Customer:", 0.2,
                                            "Probability on each time step a new customer will enter the store.\n"
                                            "Should be a number between 0 and 1.")

        prob_block_random_step = add_param_input(tab_advanced, 12, "Prob. Random Step:", 0.8,
                                                 "Probability of customer taking a random step when their path is blocked.\n"
                                                 "Should be a number between 0 and 1.")

        prob_cough = add_param_input(tab_advanced, 13, "Prob. Cough:", 0.0003,
                                     "Probability of a customer coughing per step.\n"
                                     "Should be a number between 0 and 1.")

        plume_conc_cough = add_param_input(tab_advanced, 14, "Aerosol Conc. When Coughing:", params["PLUMECONCINC"],
                                           "Aerosol concentration when a customer coughs.\n"
                                           "Should be a number larger than 0.")

        add_param_label(tab_advanced, 20, "Diffusion")

        diff_coeff = add_param_input(tab_advanced, 21, "Diffusion Coefficient:", params["DIFFCOEFF"],
                                     "The magnitude of the molar flux through a surface per unit concentration gradient out-of-plane.\n"
                                     "Should be a number between 0 and 1.")

        acsinkcoeff = add_param_input(tab_advanced, 22, "Sink Coefficient:", params["ACSINKCOEFF"],
                                      "Coefficient for the sink term of the form: -k*c.\n"
                                      "Should be a number between 0 and 1.")

        # Add all tabs
        input_tab_control.add(tab_default, text="Options")
        input_tab_control.add(tab_advanced, text="Advanced")

        input_tab_control.pack(fill=tk.BOTH)

        frm_parameters_input = ttk.Frame(frm_parameters, relief=tk.SUNKEN, borderwidth=2)
        frm_parameters_input.pack()

        # Run button
        btn_run = ttk.Button(self.frm_buttons,
                             style='Run.TButton',
                             text="Run Simulation",
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
                                     "nexits": self.scl_nr_exits.get(),
                                     "cashierd": self.scl_d_exits.get()
                                 },
                                 diffusion_params={
                                     "diff_coeff": diff_coeff.get(),
                                     "acsinkcoeff": acsinkcoeff.get()
                                 },
                                 plume_params={
                                     "plume_conc_cough": plume_conc_cough.get()
                                 },
                                 store_layout=self.store_layout_canvas,
                                 btn_run=btn_run,
                                 frm_parameters=frm_parameters,
                                 facemasks=chk_facemasks_enabled
                             ))
        btn_run.pack(side=tk.LEFT, padx=10)

        self.frm_layout.grid(row=1, column=1, padx=50, sticky="ne")
        frm_parameters.grid(row=1, column=0, sticky="nw")
        

    def validate_input(self, simulation_params, customer_params, diffusion_params, plume_params, store_empty):
        # Default
        try:
            int_max_steps = int(simulation_params["max_steps"])

            int_nr_customers = int(customer_params["nr_customers"])
            float_prob_inf_customer = float(customer_params["prob_inf_customer"])
            int_max_shopping_list = int(customer_params["max_shopping_list"])

            if any(x <= 0 for x in (int_max_steps, int_nr_customers, float_prob_inf_customer, int_max_shopping_list)) \
                    or float_prob_inf_customer >= 1:
                raise Exception()
        except:
            tk.messagebox.showerror("Error!", "Invalid input in Default tab!")
            return False

        # Advanced
        try:
            int_seed = int(simulation_params["seed"])

            float_prob_new_customer = float(customer_params["prob_new_customer"])
            float_prob_block_random_step = float(customer_params["prob_block_random_step"])
            float_prob_cough = float(customer_params["prob_cough"])

            float_diff_coeff = float(diffusion_params["diff_coeff"])
            float_acsinkcoeff = float(diffusion_params["acsinkcoeff"])

            float_plume_conc_cough = float(plume_params["plume_conc_cough"])

            if any(x <= 0 for x in (int_seed,
                    float_prob_new_customer, float_prob_block_random_step, float_plume_conc_cough,
                    float_prob_cough, float_diff_coeff, float_acsinkcoeff)) \
                    or any(x >= 1 for x in (float_prob_new_customer, float_prob_block_random_step, float_prob_cough,
                                            float_diff_coeff, float_acsinkcoeff)):
                raise Exception()
        except:
            tk.messagebox.showerror("Error!", "Invalid input in Advanced tab!")
            return False

        # Empty store
        if store_empty:
            tk.messagebox.showerror("Error!", "The store is empty! Please add at least one shelf.")
            return False

        else:
            return True

    def run_simulation(self, simulation_params, customer_params, exit_params, diffusion_params, plume_params,
                       store_layout, btn_run, frm_parameters, facemasks):
        self.simulating = True

        input_valid = self.validate_input(
            simulation_params=simulation_params,
            customer_params=customer_params,
            diffusion_params=diffusion_params,
            plume_params=plume_params,
            store_empty=store_layout.check_store_empty()
        )

        if input_valid:
            # Disable params
            for entry in self.params:
                entry.config(state=tk.DISABLED)

            self.scl_nr_exits.state(['disabled'])
            self.scl_d_exits.state(['disabled'])
            self.chk_facemasks.state(['disabled'])

            # Remove layout
            self.frm_layout.grid_forget()
            self.buttons_store_grid.grid_forget()
            btn_run.forget()

            self.outputGui = GuiOutput(self.root, frm_parameters, self.frm_buttons, simulation_params, self.count, customer_params["nr_customers"])

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

                diff_coeff = float(diffusion_params["diff_coeff"])
                ac_sink_coeff = float(diffusion_params["acsinkcoeff"])
                plume_conc_cough = float(plume_params["plume_conc_cough"])

                if facemasks:
                    effectivity_rate = 0.5
                    diff_coeff *= effectivity_rate
                    ac_sink_coeff *= effectivity_rate
                    plume_conc_cough *= effectivity_rate

                # Diffusion
                params["DIFFCOEFF"] = diff_coeff
                params["ACSINKCOEFF"] = ac_sink_coeff

                # Plume
                params["PLUMECONCINC"] = plume_conc_cough

                os.environ["PARAMS"] = str(params)

                sim = Simulation(
                    self.outputGui,
                    int(simulation_params["seed"]),
                    100,
                    100,
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
                self.outputGui.simulating = False
                self.outputGui.update_on_sim_finished(store_plot)

            # Start simulation in new thread so GUI doesn't block
            threading.Thread(target=run_sim, daemon=True).start()

    def update_layout_entrance_exits(self, nexits, cashierd):
        self.store_layout_canvas.draw_entrance_exits(nexits, cashierd)

    def remove_focus(self):
        self.root.focus()
