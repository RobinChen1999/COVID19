from Gui import *

class GuiTabs:
    def __init__(self):
        self.window_width = 1600
        self.window_height = 800
        self.numOfSims = 0
        self.root = tk.Tk()
        
        Params.set_params()

        style = ttk.Style(self.root)
        self.root.tk.eval("""
            set base_theme_dir theme/awthemes-10.3.0/
        
            package ifneeded awdark 7.11 \
                [list source [file join $base_theme_dir awdark.tcl]]
            """)
        self.root.tk.call('package', 'require', 'awdark')
        style.theme_use('awdark')

    def draw_window(self):
        self.root.title("Input window")
        self.root.geometry('{}x{}'.format(self.window_width, self.window_height))

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
        frame = ttk.Frame(self.tab_control)
        name = "    Simulation " + str(pos+1) + "  "
        btn_close_tab = ttk.Button(frame, text="Close tab", command=self.close_tab)
        btn_close_tab.pack(anchor="nw")
        
        self.tab_control.insert(pos=pos, child=frame, text=name, padding=10)
        if not pos == "end": 
            self.tab_control.select(pos)
        
        simulation = Gui(frame, self.numOfSims)
        simulation.draw_input_window()

        

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

        self.root.destroy()

        

