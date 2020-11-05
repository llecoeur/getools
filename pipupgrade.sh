#!/bin/bash


pip install `pip freeze -l | cut --fields=1 -d = -` --upgrade

