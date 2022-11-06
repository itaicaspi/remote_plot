import atexit
from .client import PlotClient

plt = PlotClient()

def exit_handler():
    plt.stop_server()

atexit.register(exit_handler)