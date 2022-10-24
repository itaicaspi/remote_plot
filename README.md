# Remote Plot

[![PyPI version](https://badge.fury.io/py/remote-plot.svg)](https://badge.fury.io/py/remote-plot)

Developing python code on a remote machine can get frustrating when you want to visualize your results.
Instead of relying on a remote screen / X11 forwarding / VNC, Remote Plot opens your plots in a local server.
It's a super simple library that replicates the API of matplotlib with a web renderer.
All you need to do is forward the port to your machine. If your using VS Code, it will take care of it for you.

## Getting started

### Installation
```
pip install remote_plot
```

### Port forwarding

If you are using VSCode, once you run your first plot, it will automatically forward the port
and pop a dialog box that will let you open the plot in your web browser.

If you are using SSH, you can forward the port using he following flag while connecting to the remote machine:
```
ssh YOUR_USER_NAME@YOUR_MACHINE_IP -L 8000:localhost:8000
```
Then, you can just open [localhost:8000](localhost:8000) in a web browser once you run your first plot.

### Your first plot
```
from remote_plot import plt

plt.plot([1, 2, 3], [4, 5, 6])
```

## API

Remote plot replicates the matplotlib API, which you can find [here](https://matplotlib.org/stable/plot_types/index).

It also supports native image displaying that can display numpy array or pillow images.
```
from PIL import Image
img = Image.open("PATH TO YOUR IMAGE")
plt.imshow_native(img)
```

### Changing the web server port

```
from remote_plot import plt

plt.port = 8001
```

## License

MIT License. See [LICENSE](LICENSE) for further details.
