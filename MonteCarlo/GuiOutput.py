import tkinter as tk
import threading
import imageio
import shutil
from PIL import Image, ImageTk

class GuiOutput:
    window_width = 1600
    window_height = 800

    def __init__(self, seed, nr_customers, max_steps, prob_inf, prob_new):
        self.draw_output_window()
        self.update_output("Running simulation with the following parameters:")
        self.update_output(" Seed:                    " + seed)
        self.update_output(" Nr. of Customers:        " + nr_customers)
        self.update_output(" Max Steps:               " + max_steps)
        self.update_output(" Prob. Infected Customer: " + prob_inf)
        self.update_output(" Prob. New Customer:      " + prob_new)

    # updates output window after simulation is done
    def update_output_window(self):
        self.txt_output.config(cursor='arrow')
        self.txt_output.pack()
        self.update_output("Simulation finished!")
        self.stream()
        # More stuff TODO after simulation

        #updates simulation frame
    def update_figure(self, label, id, step):
        image = Image.open('simFigures/simFigure_%d_%07d.png'%(id, step))
        img = ImageTk.PhotoImage(image.resize((int(self.window_width/2), int(self.window_height/1.5))))
        label.configure(image=img)
        label.image = img
    
    # load the already simulated figures
    def load_figures(self):
        while self.simulating:
            # when simFigures has at least 2 figures
            if len(os.listdir('simFigures')) > 1:
                figureList = glob.glob('simFigures/simFigure_%s_*'%seed + '.png')
                latest_figure = figureList[-2] # get second last element  
                img = Image.open(latest_figure)
                frm_img = ImageTk.PhotoImage(img.resize((int(self.window_width/2), int(self.window_height/1.5))))
                self.label.config(image=frm_img)
                self.label.image = frm_img

    # Stream video
    def stream(self):
        video = imageio.get_reader("video.mkv")
        for image in video.iter_data():
            image_frame = Image.fromarray(image)          
            frame_image = ImageTk.PhotoImage(image_frame.resize((int(self.window_width/2), int(self.window_height/1.5))))
            self.label.config(image=frame_image)
            self.label.image = frame_image

    # Output
    def draw_output_window(self):
        self.output_line_nr = 0

        window = tk.Toplevel()
        window.geometry('{}x{}'.format(self.window_width, self.window_height))

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

        frm_sim.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        frm_output.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True)

        self.label = lbl_id_sim

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