# ia-digdug
DigDug clone for AI teaching

https://github.com/PauloMaced0/digdug-ia/assets/99764328/ba22adda-b3d2-4685-ae18-6fc253e51978

## How to install

Make sure you are running Python 3.11.

`$ pip install -r requirements.txt`

*Tip: you might want to create a virtualenv first*

## How to play

open 3 terminals:

`$ python3 server.py`

`$ python3 viewer.py`

`$ python3 client.py`

to play using the sample client make sure the client pygame hidden window has focus

As an alternative to the previous `$ python3 client.py` command, you can also try:

`$ python3 student.py`

This will run the autonomous agent to solve digdug levels

### Keys

Directions: arrows

*A*: 'a' - pump enemies

## Debug Installation

Make sure pygame is properly installed:

python -m pygame.examples.aliens

# Tested on:
- MacOS 13.6
- Ubuntu 20.04

# CREDITS 
Huge thanks to [Diogo Gomes](https://github.com/dgomes) for the digdug game template. 

