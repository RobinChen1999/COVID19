from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Store import *
from Customer import *

import tkinter as tk

from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.tri as tri
from numpy import linspace, meshgrid
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import ListedColormap
from matplotlib import colors as cls
from matplotlib import ticker
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


class StorePlot:
    def __init__(self, store, customers, parula_map, useDiffusion):
        self.store = store
        self.customers = customers
        self.parula_map = parula_map
        self.useDiffusion = useDiffusion

    def showStore(self, step):
        fig = plt.figure(figsize=(12, 8))

        # first plot the static store structures
        ax = fig.add_axes([0.07, 0.07, 0.85, .85])

        ax.plot(self.store.entrance[0], self.store.entrance[1], 'bs', ms=10)
        ax.text(self.store.entrance[0], self.store.entrance[1] -
                4, "entrance", color=(0.5, 0.5, 0.5))

        for i, s in enumerate(self.store.exit):
            ax.plot(s[0], s[1], 'bs', ms=10)
            ax.text(s[0], s[1]-4, "exit", color=(0.5, 0.5, 0.5))

        # plot the plumes
        if not self.useDiffusion:
            ax.plot(np.argwhere(self.store.plumes > 0)[:, 0], np.argwhere(
                self.store.plumes > 0)[:, 1], 'rs', ms=10)
        else:
            x = np.linspace(0., self.store.Lx-1, self.store.Lx)
            y = np.linspace(0., self.store.Ly-1, self.store.Ly)
            z = np.clip(self.store.plumes[:, :], 0.1, 100.0)
            X, Y = np.meshgrid(x, y)
            plumePlotData = (np.transpose(
                z.reshape(self.store.Lx, self.store.Ly)))
            lev_exp = np.arange(-1.1, 2.034, 0.0333)
            levs = np.power(10, lev_exp)
            difPlumes = ax.contourf(
                X, Y, plumePlotData, levs, norm=cls.LogNorm(), cmap=self.parula_map, zorder=1)

            # Colormap for the shelves
            colors = [(1, 1, 1, 0), (0, 0, 0, 1)]
            n_bins = 2
            cmap_name = 'my_list'
            cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

            ax.imshow(self.store.blockedShelves.T,
                      interpolation='nearest', zorder=1, origin='lower', cmap=cm)
            ax.plot(self.store.entrance[0],
                    self.store.entrance[1], 'bs', ms=10)
            ax.text(
                self.store.entrance[0], self.store.entrance[1]-4, "entrance", color=(0.5, 0.5, 0.5))

        # add every cutomer to the plot,and the colour denotes infected and healthy customers
        for i, c in enumerate(self.customers):
            if c.initStep <= step and step < (c.initStep + len(c.route)):
                if c.infected:
                    col = 'r'
                    marker = 'D'
                else:
                    col = 'y'
                    marker = 'o'
                ax.plot(c.route[step-c.initStep][0], c.route[step-c.initStep][0], '{}{}'.format(col, marker),
                        ms=17, clip_on=False)

        def onpick(event):
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            points = tuple(zip(xdata[ind], ydata[ind]))
            print('onpick points:', points)

        fig.canvas.mpl_connect('pick_event', onpick)
        # plt.show()

        plt.xlim([0., self.store.Lx])
        plt.ylim([0., self.store.Ly])
        cb = fig.colorbar(difPlumes, ticks=[0.1, 1.0, 10.0, 100.0])

        font_size = 36
        cb.set_label(
            label="$\mathrm{Aerosols} / \mathrm{m}^3$", weight='bold', size=36)
        cb.ax.tick_params(labelsize=font_size)
        plt.axis('off')
        # plt.savefig("simFigures/simFigure_{}_{:07d}.png".format(self.seed, step))
        # plt.close()
        return fig
