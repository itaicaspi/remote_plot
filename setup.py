"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="remote_plot",
    version="1.0.0",
    description="Like matplotlib but renders in a local server so you can work remotely",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/itaicaspi/remote_plot",
    author="Itai Caspi",
    author_email="itaicaspi@gmail.com",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="matplotlib, plotting, remote development",
    packages=find_packages(where="src"),
    python_requires=">=3.7, <4",
    install_requires=["pillow", "numpy"],
    extras_require={  # Optional
        "dev": [],
        "test": [],
    },
)