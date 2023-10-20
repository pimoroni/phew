#!/usr/bin/make -f
#
# SPDX-FileCopyrightText: 2023 Charles Crighton <code@crighton.net.nz>
#
# SPDX-License-Identifier: MIT

SHELL := /bin/bash
.ONESHELL:
.DEFAULT_GOAL:=help
.PHONY: help dist dist-build
.SILENT: help

UID := $(shell id -u)
PWD := $(shell pwd)

PORT ?= /dev/ttyUSB0
VENV ?= ~/.virtualenvs/phew

help:  ## Display this help
	$(info Rockwren build and flash targets)
	$(info )
	fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\:.*##/:/' | sed -e 's/##//'

dist:  ## Package phew python distribution
	rm -rf dist
	python -m build

publish-testpypi:  ## Publish distribution file to TestPyPI
	python3 -m twine upload --repository testpypi dist/*

publish-pypi:  ## Publish distribution file to PyPI
	 python3 -m twine upload --repository pypi dist/*
