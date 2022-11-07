from collections.abc import Callable
from io import BytesIO
from multiprocessing import Process
from typing import Any
import numpy as np
from PIL import Image
import requests
import matplotlib.pyplot as plt

from .server import SharedDataServer, ImageHandler, run_server, get_best_family

class PlotClient:
    def __init__(self, port=8000):
        self._port = None
        self.server = None
        self.server_class = SharedDataServer
        self.handler_class = ImageHandler
        self.httpd = None
        self.port = port
        self._figure = None
        self._all_axes = None
        self._axes = None
        self.auto_show = True

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port):
        self._port = port
        self.server_class.address_family, self.addr = get_best_family(None, port)

    """
    Start the server in a background process.
    """
    def start_server(self):
        self.httpd = self.server_class(self.addr, self.handler_class)

        # start the server in a new process
        self.server = Process(target=run_server, args=(self.httpd,))
        self.server.start()

    """
    Stop the server background process.
    """
    def stop_server(self):
        if self.httpd is not None:
            self.httpd.shutdown()
        if self.server is not None:
            self.server.close()

    """
    Starts the server only if it is not already running.
    """
    def maybe_start_server(self):
        if self.httpd is None:
            self.start_server()

    """
    Wraps a matplotlib plot function to display the plot in a browser.

    Arguments:
        plot_func: The matplotlib plot function to wrap.
        is_3d: Whether the plot is a 3D plot.
        clear_figure: Whether to clear the figure before plotting.
        call_on_figure: Whether to call the plot function on the figure instead of the axes.
    """
    def _matplotlib_figure(self, plot_func: Callable, is_3d: bool=False, clear_figure: bool=True, call_on_figure: bool=False):
        self.maybe_start_server()

        # initialize the figure and axes
        if self._figure is None or clear_figure:
            self.figure()
        
        # call the plot function either on the figure or the axes
        result = None
        if call_on_figure:
            self._axes = plot_func(self._figure)
        else:
            if self._axes is None:
                self._axes = self._figure.add_subplot(111, projection='3d' if is_3d else None)
            result = plot_func(self._axes)

        if self.auto_show:
            self.show()

        return result

    """
    Show the figure on the remote server
    """
    def show(self):
        data = BytesIO()
        self._figure.savefig(data, format="png")
        data.seek(0)
        r = requests.post(f"http://localhost:{self.port}", data=data)
    
    """
    Instantiate a new figure.
    """
    def figure(self, *args, **kwargs):
        if self._figure:
            plt.close(self._figure)
        self._figure = plt.figure(*args, **kwargs)
        return self

    @property
    def canvas(self):
        return self._figure.canvas

    """
    Emulate matplotlib plt.subplots
    """
    def subplots(self, *args, **kwargs):
        if len(args) > 0:
            self._figure, self._all_axes = plt.subplots(*args, **kwargs)
            self._axes = self._all_axes.flatten()[0]
        return self, self

    def add_subplot(self, *args, **kwargs):
        self._axes = self._figure.add_subplot(*args, **kwargs)
        return self

    """
    Emulate getting a specific axis. This actually sets the current axis, and return the client.
    """
    def __getitem__(self, *args):
        self._axes = self._all_axes[args[0]]
        self._figure.sca(self._axes)
        return self

    """
    Show an image without going through matplotlib
    """
    def imshow_native(self, img):
        self.maybe_start_server()

        # send the image to the server
        data = BytesIO()
        if isinstance(img, np.ndarray):
            img = Image.fromarray(img)
        img.save(data, 'png')
        data.seek(0)
        r = requests.post(f"http://localhost:{self.port}", data=data)

    """
    Get an attribute of the plt module by mapping each name to a function that calls the 
    corresponding function on the axes object or the figure object.
    """
    def __getattr__(self, name: str) -> Any:
        matplotlib_attributes = [
            'imshow', 'plot', 'scatter', 'bar', 'stem', 'step', 'fill_between', 
            'stackplot', 'hist', 'boxplot', 'errorbar', 'violinplot', 'eventplot',
            'hist2d', 'hexbin', 'pie', 'tricontour', 'tricontourf', 'tripcolor',
            'triplot', 'pcolormesh', 'contour', 'contourf', 'barbs', 'quiver',
            'streamplot'
        ]

        matplotlib_attributes_3d = [
            'plot_surface', 'plot_wireframe', 'plot_trisurf', 'scatter3D', 'bar3D',
            'contour3D', 'quiver3D', 'streamplot3D'
        ]

        matplotlib_axes_attributes_map = {
            'title': 'set_title',
            'text': 'text',
            'ylim': 'set_ylim',
            'xlim': 'set_xlim',
            'set_xlim': 'set_xlim',
            'set_ylim': 'set_ylim',
            'xlabel': 'set_xlabel',
            'ylabel': 'set_ylabel',
            'yscale': 'set_yscale',
            'xscale': 'set_xscale',
            'xticks': 'set_xticks',
            'yticks': 'set_yticks',
            'legend': 'legend',
            'clf': 'clear',
            'grid': 'grid',
            'axis': 'axis',
            'annotate': 'annotate',
            'set': 'set',
            'set_aspect': 'set_aspect',
            'pcolormesh': 'pcolormesh',
            'axvline': 'axvline',
        }

        matplotlib_figure_attributes_map = {
            'subplots_adjust': 'subplots_adjust',
            'subplot': 'add_subplot',
            'suptitle': 'suptitle',
            'colorbar': 'colorbar'
        }

        # get the matplotlib function name and set the meta flags
        call_on_figure = False
        is_3d = name in matplotlib_attributes_3d
        matplotlib_func_name = None
        if name in matplotlib_attributes:
            matplotlib_func_name = name
        elif name in matplotlib_attributes_3d:
            matplotlib_func_name = name.replace('3D', '')
            is_3d = True
        elif name in matplotlib_axes_attributes_map:
            matplotlib_func_name = matplotlib_axes_attributes_map[name]
        elif name in matplotlib_figure_attributes_map:
            matplotlib_func_name = matplotlib_figure_attributes_map[name]
            call_on_figure = True

        # get a callable function for matplotlib
        if matplotlib_func_name is not None:
            return lambda *args, **kwargs: \
                self._matplotlib_figure(
                    lambda ax: getattr(ax, matplotlib_func_name)(*args, **kwargs),
                    is_3d=is_3d,
                    call_on_figure=call_on_figure,
                    clear_figure=kwargs.pop("clear_figure", False)
                )