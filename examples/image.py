# Before running this example, you need to run:
# pip install pillow requests

from remote_plot import plt
import requests
from PIL import Image
from io import BytesIO


url = 'https://matplotlib.org/stable/_images/stinkbug.png'
response = requests.get(url)
img = Image.open(BytesIO(response.content))
plt.imshow(img)