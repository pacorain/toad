from setuptools import setup

setup(
    name='mockhass',
    version='0.1',
    description='Framework for testing Home Assistant configurations',
    packages=['mockhass'],
    package_dir={'mockhass': 'src/python/mockhass'},
    install_requires=['pytest==8.3.4', 'homeassistant==2025.1.2', 'pytest-asyncio==0.25.2', 'pytest-xdist==3.6.1'],
)