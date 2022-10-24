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

    def _matplotlib_figure(self, plot_func: Callable):
        self.maybe_start_server()

        f = plt.figure(1)
        f.clf()
        ax = f.add_subplot(111)
        plot_func(ax)
        data = BytesIO()
        f.savefig(data, format="png")
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

    def __getattr__(self, __name: str) -> Any:
        matplotlib_attributes = [
            'imshow', 'plot', 'scatter', 'bar', 'stem', 'step', 'fill_between', 
            'stackplot', 'hist', 'boxplot', 'errorbar', 'violinplot', 'eventplot',
            'hist2d', 'hexbin', 'pie', 'tricontour', 'tricontourf', 'tripcolor',
            'triplot', 'pcolormesh', 'contour', 'contourf', 'barbs', 'quiver',
            'streamplot'
        ]
        if __name in matplotlib_attributes:
            return lambda *args, **kwargs: self._matplotlib_figure(lambda ax: getattr(ax, __name)(*args, **kwargs))