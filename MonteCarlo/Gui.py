import tkinter as tk

from Simulation import *
from tkinter import messagebox


class Gui:
    def __init__(self):
        self.txt_output = 0
        self.output_line_nr = 0

    # Input window
    def draw_input_window(self):
        window = tk.Tk()
        window.geometry('{}x{}'.format(800, 400))

        # Layout frame
        frm_layout = tk.Frame(window, bg="red")

        lbl_id_layout = tk.Label(frm_layout, text="Layout Frame")
        lbl_id_layout.pack()

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
        ent_max_steps.insert(0, 1000)
        lbl_max_steps.grid(row=2, column=0, sticky="e")
        ent_max_steps.grid(row=2, column=1)

        # Run button
        btn_run = tk.Button(frm_parameters,
                            text="Run",
                            command=lambda: self.run_simulation(
                                seed=ent_seed.get(),
                                nr_customers=ent_nr_customers.get(),
                                max_steps=ent_max_steps.get()
                            ))
        btn_run.pack()

        frm_layout.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        frm_parameters.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        window.mainloop()

    def validate_input(self, seed, nr_customers, max_steps):
        try:
            int_seed = int(seed)
            int_nr_customers = int(nr_customers)
            int_max_steps = int(max_steps)

            if int_seed <= 0 or int_nr_customers <= 0 or int_max_steps <= 0:
                raise Exception()
        except:
            tk.messagebox.showerror("Error!", "Invalid input!")
            return False
        else:
            return True

    def run_simulation(self, seed, nr_customers, max_steps):
        input_valid = self.validate_input(
            seed=seed,
            nr_customers=nr_customers,
            max_steps=max_steps
        )

        if input_valid:
            self.draw_output_window()

            self.update_output("Running simulation with the following parameters:")
            self.update_output(" Seed:             " + seed)
            self.update_output(" Nr. of Customers: " + nr_customers)
            self.update_output(" Max Steps:        " + max_steps)

            # sim = Simulation(
            #     int(seed),
            #     101,
            #     101,
            #     25,
            #     int(nr_customers),
            #     outputLevel=0,
            #     maxSteps=int(max_steps),
            #     probInfCustomer=0.01,
            #     probNewCustomer=0.2,
            #     imageName="ExampleSuperMarket.pbm",
            #     useDiffusion=1,
            #     dx=1.0)
            # sim.runSimulation()

    # Output
    def draw_output_window(self):
        self.output_line_nr = 0

        window = tk.Toplevel()
        window.geometry('{}x{}'.format(800, 400))

        # Layout frame
        frm_layout = tk.Frame(window, bg="red")

        lbl_id_layout = tk.Label(frm_layout, text="Layout Frame")
        lbl_id_layout.pack()

        # Output frame
        frm_parameters = tk.Frame(window, bg="yellow")

        lbl_id_parameters = tk.Label(frm_parameters, text="Output Frame")
        lbl_id_parameters.pack()

        self.txt_output = tk.Text(frm_parameters, height=5, width=60)
        self.txt_output.config(state='disabled')
        self.txt_output.pack()

        btn_run = tk.Button(frm_parameters,
                            text="Add text",
                            command=lambda: self.update_output("New line"))
        btn_run.pack()

        frm_layout.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        frm_parameters.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

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
            self.txt_output.see(tk.END)
            self.txt_output.config(state='disabled')

            self.output_line_nr += 1