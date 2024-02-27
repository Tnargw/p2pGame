from setuptools import setup
'''
In order to run this game you will need to open your terminal with this file open and input the following command 
"pip install -e ."
After this the first player can run the game by entering the following command in their terminal: 
"run"
and player 2 will be able to run the program by entering the following command into their terminal:
"run -p 1 -b 192.168.1.1" <- Replace the ip-address with the ip-address listed in the console from the first player.
In the command above "-p 1" is identifying that the player joining will be "player 1" and "-b 192.168.1.1" is telling
the game to connect to the Backplane that was initialized by the first player.
'''
setup(
    name='p2p_arcade',
    version='0.2',
    packages=[
        'p2pArcade',
    ],
    install_requires=[
        'python_banyan', 'arcade', 'msgpack', 'zmq', 'psutil'
    ],

    entry_points={
        'console_scripts': [
            'run = p2pArcade.p2pArcade:p2pArcade',
        ]
    }
)