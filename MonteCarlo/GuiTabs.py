from Gui import *

class GuiTabs:
    def __init__(self):
        self.window_width = 1600
        self.window_height = 800
        self.numOfSims = 0
        self.root = tk.Tk()
        
        Params.set_params()

        self.style = ttk.Style(self.root)
        self.root.tk.eval("""
            set base_theme_dir theme/awthemes-10.3.0/

            package ifneeded awdark 7.11 \
                [list source [file join $base_theme_dir awdark.tcl]]
            package ifneeded awlight 7.9 \
                [list source [file join $base_theme_dir awlight.tcl]]
            """)
        self.root.tk.call('package', 'require', 'awdark')
        self.root.tk.call('package', 'require', 'awlight')
        self.root.tk.call('source', 'theme/tkBreeze-master/breeze/breeze.tcl')
        self.root.tk.call('source', 'theme/tkBreeze-master/breeze-dark/breeze-dark.tcl')
        self.style.theme_use('breeze')
        self.switch_theme()
        

    def draw_window(self):
        self.root.title("Supermarket Spread")
        self.root.state('zoomed')

        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill=tk.BOTH)
        self.tab_control.bind("<<NotebookTabChanged>>", self.tab_changed)
        
        # add simulation button
        btn_add_sim = ttk.Button(self.tab_control)
        self.tab_control.add(btn_add_sim, text="    + Add Simulation    ")

        self.create_simulation(pos=0)    # create first sim tab
        
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
        self.root.mainloop()

    def create_simulation(self, pos):
        self.numOfSims+=1
        frame = ttk.Frame(self.tab_control, padding=20)
        frame.grid_columnconfigure(2, weight=1)
        name = "    Simulation " + str(pos+1) + "  "

        frm_buttons = ttk.Frame(frame)
        frm_buttons.grid(row=0, column=0, sticky="w")

        btn_close_tab = ttk.Button(frm_buttons, text="Close Tab", command=self.close_tab)
        btn_close_tab.pack(side=tk.LEFT)

        btn_frame = ttk.Frame(frame)
        btn_help = ttk.Button(btn_frame, text="Help", command=self.open_help)
        self.btn_switch_theme = ttk.Button(btn_frame, text="Switch Theme", command=self.switch_theme)
        btn_help.pack(side=tk.RIGHT)
        self.btn_switch_theme.pack(side=tk.RIGHT, padx=10)
        btn_frame.grid(row=0, column=2, sticky="ne")
        
        self.tab_control.insert(pos=pos, child=frame, text=name)
        if not pos == "end": 
            self.tab_control.select(pos)
        
        self.simulation = Gui(frame, frm_buttons, self.numOfSims)
        self.simulation.draw_input_window()

        

    def tab_changed(self, event):
        current_tab = self.tab_control.index("current")
        last_tab = self.tab_control.index("end") - 1
        if current_tab == last_tab:
            self.create_simulation(pos=last_tab)

    def rename_tabs_after_close(self):
        for tab in self.tab_control.tabs():
            index = self.tab_control.index(tab)+1
            if index != self.tab_control.index("end"):              # don't rename "Add sim" tab
                name = "    Simulation " + str(index) + "  "
                self.tab_control.tab(tab, text=name)
        
    def close_tab(self):
        result = tk.messagebox.askquestion("Warning!", "Are you sure you want to close this tab?")
        if result == "yes":
            current_tab = self.tab_control.index("current")            
            self.tab_control.forget("current")
            try: self.tab_control.select(current_tab-1)
            except: self.tab_control.select(0)
            self.rename_tabs_after_close()

    # when window closes
    def close_window(self):
        self.root.destroy()

        # clear figures from simFigures folder
        figureList = glob.glob('simFigures/simFigure*' + '.png')
        for f in figureList:
            os.remove(f)

        # remove all data files
        dataFiles = glob.glob('*.dat')
        for d in dataFiles:
            os.remove(d)

        # remove all videos
        videos = glob.glob('*.mkv')
        for v in videos:
            os.remove(v)

    def switch_theme(self):
        if self.style.theme_use() == "breeze":
            theme = "breeze-dark"
            color_run = '#44bb44'
            color_terminate = '#f94548'
            color_header = '#ddd'
        else:
            theme = "breeze"
            color_run = 'green'
            color_terminate = '#dd0000'
            color_header = '#222'

        if hasattr(self, 'simulation'):
            if self.simulation.outputGui is not None:
                self.simulation.outputGui.update_plot_theme(theme)
                self.simulation.outputGui.update_customer_plot_theme(theme)

        self.style.theme_use(theme)

        self.style.configure('Run.TButton', foreground=color_run, font=('Helvetica', 10, 'bold'))
        self.style.configure('Terminate.TButton', foreground=color_terminate, font=('Helvetica', 10, 'bold'))
        self.style.configure('Header.TLabel', foreground=color_header)
        self.style.configure('.', font=('Helvetica', 10))

        self.root.focus()

    def open_help(self):
        self.help_frame = ttk.Frame(self.root)
        btn_close = ttk.Button(self.help_frame, text="Close", command=self.close_help)
        btn_close.pack(anchor="ne")
        message = ttk.Label(self.help_frame, text="HEEELLUUUUP")
        message.pack()
        self.help_frame.place(relheight=1, relwidth=1, relx=0, rely=0, bordermode=tk.INSIDE)
        
        
    def close_help(self):
        self.help_frame.place_forget()