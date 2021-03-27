from Simulation import *
from Gui import *
from GuiTabs import *

#~ These two have to be matched as the pixel count (in x- and y-axis) of a .ppm image, if that is imported as the simulation geometry!
# pixNx = 101
# pixNy = 101

# gui = Gui()
# gui.draw_input_window()
gui = GuiTabs()
gui.draw_window()

## parameters: seed, pixNx, pixNy, N shelves (if no file provided), N customers, ..
# sim = Simulation(888892, pixNx, pixNy, 25, 10000, outputLevel=1, maxSteps=100, probInfCustomer=0.01, probNewCustomer=0.2,imageName="ExampleSuperMarket.pbm",useDiffusion=1,dx=1.0)
# sim.runSimulation()