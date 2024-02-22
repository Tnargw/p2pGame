from setuptools import setup

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