from setuptools import setup, find_packages
import sys
import os

if sys.platform == "darwin":
    os.environ["QT_QPA_PLATFORM"] = "cocoa"

def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "src", "openturbine", "version.py")
    if os.path.exists(version_file):
        with open(version_file) as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="openturbine",
    version=get_version(),
    description="Open-source wind turbine simulation software",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="OpenTurbine Contributors",
    author_email="info@openturbine.org",
    url="https://github.com/openturbine/openturbine",
    license="Apache-2.0",
    packages=find_packages(exclude=["tests", "tests.*", "docs"]),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "pandas>=1.3.0",
        "pyqtgraph>=0.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "ui": [
            "PySide6>=6.4.0",
            "vtk>=9.2.0",
        ],
        "full": [
            "PySide6>=6.4.0",
            "vtk>=9.2.0",
            "pyvista>=0.37.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "openturbine=openturbine.ui.main_window:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
