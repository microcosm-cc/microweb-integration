#!/bin/bash

if [[ "$OSTYPE" == "linux-gnu" ]]; then
	sudo apt-get -y install python-pip
	sudo pip install virtualenv
elif [[ "$OSTYPE" == "darwin"* ]]; then
	brew install python
	pip install virtualenv
else
	echo -e "${COL_RED}This script only works on Linux and OSX $COL_RESET"
	exit 1
fi

virtualenv ENV
source ENV/bin/activate
ORIGPATH=$PATH
export PATH=$PWD/ENV/bin:$PATH
pip install -r requirements.txt
deactivate
export PATH=$ORIGPATH
