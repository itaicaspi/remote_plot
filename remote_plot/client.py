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
        self.figure = None
        self.axes = None

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port):
        self._port = port
        self.server_class.address_family, self.addr = get_best_family(None, port)

    def start_server(self):
        self.httpd = self.server_class(self.addr, self.handler_class)

        # start the server in a new process
        self.server = Process(target=run_server, args=(self.httpd,))
        self.server.start()

    def stop_server(self):
        self.httpd.shutdown()

    def maybe_start_server(self):
        if self.httpd is None:
            self.start_server()

    def _matplotlib_figure(self, plot_func: Callable, is_3d=False, clear_figure=True):
        self.maybe_start_server()

        if self.figure is None or clear_figure:
            if self.figure:
                plt.close(self.figure)
            if is_3d:
                self.figure = plt.figure()
                self.axes = self.figure.add_subplot(111, projection='3d')
            else:
                self.figure, self.axes = plt.subplots()
        plot_func(self.axes)
        data = BytesIO()
        self.figure.savefig(data, format="png")
        data.seek(0)
        r = requests.post(f"http://localhost:{self.port}", data=data)

    def imshow_native(self, img):
        self.maybe_start_server()

        # send the image to the server
        data = BytesIO()
        if isinstance(img, np.ndarray):
            img = Image.fromarray(img)
        img.save(data, 'png')
        data.seek(0)
        r = requests.post(f"http://localhost:{self.port}", data=data)

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

        if name in matplotlib_attributes:
            return lambda *args, **kwargs: self._matplotlib_figure(lambda ax: getattr(ax, name)(*args, **kwargs), clear_figure=kwargs.pop("clear_figure", True))

        if name in matplotlib_attributes_3d:
            return lambda *args, **kwargs: self._matplotlib_figure(lambda ax: getattr(ax, name.replace("3D", ""))(*args, **kwargs), is_3d=True, clear_figure=kwargs.pop("clear_figure", True))