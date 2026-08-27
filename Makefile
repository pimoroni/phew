#!/usr/bin/make -f
#
# SPDX-FileCopyrightText: 2023 Charles Crighton <code@crighton.net.nz>
#
# SPDX-License-Identifier: MIT

SHELL := /bin/bash
.ONESHELL:
.DEFAULT_GOAL:=help
.PHONY: help dist install-local check test
.SILENT: help

help:  ## Display this help
	$(info Phew build and install targets)
	$(info )
	fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\:.*##/:/' | sed -e 's/##//'

dist:  ## Build the minified sdist and wheel
	rm -rf dist
	python -m build

install-local: dist  ## Install the built package onto an attached device
	pipkin install --no-index --find-links dist --force-reinstall micropython-phew

check:  ## Lint and spell check
	source ci/python.sh && qa_phew_check && qa_examples_check && qa_tests_check && qa_spelling_check

test:  ## Run the test suite
	source ci/python.sh && qa_test
