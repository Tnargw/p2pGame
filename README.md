# Overview
This program is a simple pong game that utilizes a library called Python Banyan to create a instance of the program that a second player can then connect to.

The goal of this program was to create a two player game that utilizes networking.

[Software Demo Video](http://youtube.link.goes.here)

# Network Communication
This program was built using a peer-to-peer system that allows the game to send and receive updates from both players in real time.

The program utilizes TCP and uses ports 43125 and 43124.

The program functions by having each client send messages containing topics and payloads to the Banyan Backplane.
The topic dictates what function the payload is sent to, and the payload is the information to be passed through that function.

# Development Environment
This program was made in Python.

Required packages:
- python-banyan
- arcade
- msgpack
- zmq
- psutil

# Useful Websites
The following website is a proof of concept that illistrates not only that the python-banyan library works, but also how to make a simple program using it.
* [Peer To Peer Gaming With Arcade and Python Banyan](https://mryslab.github.io/bots-in-pieces/python-banyan/arcade/2020/02/21/p2p-arcade-1.html)

A link to the Python Arcade library.
* [The Python Arcade Library](https://api.arcade.academy/en/latest/index.html)

# Future Work
* Add options to add progressively more balls.
* Make sprites animated.
* Add ability for game to be played by up to 4 players.