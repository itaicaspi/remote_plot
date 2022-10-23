from io import BytesIO
from multiprocessing import Process
import numpy as np
from PIL import Image
import requests

from .server import SharedDataServer, ImageHandler, run_server, get_best_family

class PlotClient:
    def __init__(self, port=8000):
        self.port = port
        self.server = None
        self.server_class = SharedDataServer
        self.handler_class = ImageHandler
        self.server_class.address_family, self.addr = get_best_family(None, port)
        self.httpd = None

    def start(self):
        self.httpd = self.server_class(self.addr, self.handler_class)

        # start the server in a new process
        self.server = Process(target=run_server, args=(self.httpd,))
        self.server.start()

    def stop(self):
        self.httpd.shutdown()

    def imshow(self, img):
        if self.httpd is None:
            self.start()

        # send the image to the server
        data = BytesIO()
        if isinstance(img, np.ndarray):
            img = Image.fromarray(img)
        img.save(data, 'png')
        data.seek(0)
        r = requests.post(f"http://localhost:{self.port}", data=data)
