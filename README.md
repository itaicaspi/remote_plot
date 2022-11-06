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

### A more advanced example

Here's a more advnaced example taken from [the official matplotlib documentation](https://matplotlib.org/stable/tutorials/introductory/pyplot.html#working-with-text)

```
from remote_plot import plt
import numpy as np

mu, sigma = 100, 15
x = mu + sigma * np.random.randn(10000)

# the histogram of the data
n, bins, patches = plt.hist(x, 50, density=True, facecolor='g', alpha=0.75)


plt.xlabel('Smarts')
plt.ylabel('Probability')
plt.title('Histogram of IQ')
plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
plt.axis([40, 160, 0, 0.03])
plt.grid(True)
plt.show()
```

![plot](https://matplotlib.org/stable/_images/sphx_glr_pyplot_008.png)


Check the (examples directory)[https://github.com/itaicaspi/remote_plot/examples] for more examples.


## API

Remote plot is intended to act as a drop-in replacement to matplotlib. Because of this, it replicates the matplotlib API, which you can find [here](https://matplotlib.org/stable/plot_types/index).


By default, every call plot will automatically render the result (equivalent to calling `plt.show()` on matplotlib).
This can make things a bit slow, so if you prefer to turn it off, set `plt.auto_show = False`, and use `plt.show()` as usual.


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
