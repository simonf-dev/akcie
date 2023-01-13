VENV_PATH := $(abspath venv)
PIP_REQUIREMENTS:=$(abspath requirements.in)
PYTHON_INSTALLED := $(shell python3.8 --version 2> /dev/null)
VENV_EXISTS:=$(shell ls ${VENV_PATH} 2> /dev/null)

install-python:
ifndef PYTHON_INSTALLED
	apt-get -y install python3.8
	python3.8 -m pip install pip
endif
.PHONY: install-python

create-venv: install-python
ifndef VENV_EXISTS
	python3.8 -m venv ${VENV_PATH};)
endif
.PHONY: create-venv


prepare-venv: create-venv
	${VENV_PATH}/bin/pip3.8 install -r ${PIP_REQUIREMENTS}
.PHONY: prepare-venv

clean:
	rm -Rf ${VENV_PATH}
.PHONY: clean

