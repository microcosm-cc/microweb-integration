#!/bin/bash

sudo apt-get -y install python-pip
sudo pip install virtualenv

virtualenv ENV
source ENV/bin/activate
ORIGPATH=$PATH
export PATH=$PWD/ENV/bin:$PATH
pip install -r requirements.txt
deactivate
export PATH=$ORIGPATH
