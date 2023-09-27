from setuptools import setup

# SPDX-FileCopyrightText: 2023 Charles Crighton <code@crighton.net.nz>
#
# SPDX-License-Identifier: MIT
import os

import minify_html
import python_minifier
from setuptools import Command
from setuptools import find_packages
from setuptools import setup
from setuptools.command.sdist import sdist


def minify_py_dir(directory):
    """ Minify all the python files in directory. """

    files = [directory + '/' + f for f in os.listdir(directory)
             if os.path.isfile(directory + '/' + f) and f.endswith('py')]

    total_size = 0
    total_minified_size = 0

    for filename in files:
        size = os.stat(filename).st_size
        minified_size = 0
        minified = None
        with open(filename) as f:
            minified = python_minifier.minify(f.read())
            minified_size = len(minified)
            total_size += size
        with open(filename, 'w') as f:
            f.write(minified)
        total_minified_size += minified_size
        print(f"{filename}: Size: {total_size}, minified size: {total_minified_size}, "
              f"%{total_minified_size / total_size * 100:.0f}")


def minify_html_css_js_file(filename):
    """ Minify a file.  Must be a html, css or js. """

    with open(filename, 'r') as f:
        minified = minify_html.minify(f.read(), minify_js=True, remove_processing_instructions=True)
        minified_size = len(minified)
    with open(filename, 'w') as f:
        f.seek(0)
        f.write(minified)
    return minified_size


def minify_html_css_js_dir(directory):
    """ Minify all html, css, and javascript files in the directory. """

    files = [directory + '/' + f for f in os.listdir(directory) if os.path.isfile(directory + '/' + f)
             and (f.endswith('html') or f.endswith('css') or f.endswith('js'))]

    total_size = 0
    total_minified_size = 0

    for filename in files:
        size = os.stat(filename).st_size
        minified_size = minify_html_css_js_file(filename)
        total_size += size
        total_minified_size += minified_size
        print(f"{filename}: Size: {total_size}, minified size: {total_minified_size}, "
              f"%{total_minified_size / total_size * 100:.0f}")


class SdistAndMinify(sdist):
    """ Extend sdist to add minifying python, html and css files to reduce memory overhead for resource constrained
        devices such as the esp8266.
    """

    def make_release_tree(self, base_dir, files):
        """ make_release_tree creates the directory tree for the source distribution archive.
            Extended by this class to minify the python, html and css files before packaging into a sdist tar or
            wheel.  Minification is done after the super().make_release_tree so the files are copied to base_dir but
            not yet packaged.
        """
        super().make_release_tree(base_dir, files)
        minify_html_css_js_dir(base_dir + '/phew')
        minify_py_dir(base_dir + '/phew')


setup(
    name="ccrighton-phew",
    version="0.0.4",
    description="A small webserver and templating library specifically designed for MicroPython on the Pico W.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    project_urls={
        "GitHub": "https://github.com/ccrighton/phew"
    },
    author="Jonathan Williamson - Pimoroni",
    maintainer="Charlie Crighton",
    maintainer_email="code@crighton.net.nz",
    license="MIT",
    license_files="LICENSE",
    packages=["phew"],
    cmdclass={'sdist': SdistAndMinify}
)
