from setuptools import setup

setup(
    name="micropython-phew",
    version="0.0.3",
    description="A small webserver and templating library specifically designed for MicroPython on the Pico W.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    project_urls={
        "GitHub": "https://github.com/pimoroni/phew"
    },
    author="Jonathan Williamson",
    maintainer="Phil Howard",
    maintainer_email="phil@pimoroni.com",
    license="MIT",
    license_files="LICENSE",
    packages=["phew"]
)
