from setuptools import setup

setup(
    name='mockhass',
    version='0.2.1',
    description='Framework for testing Home Assistant configurations',
    packages=['mockhass'],
    package_dir={'mockhass': 'src/python/mockhass'},
    install_requires=['pytest==8.4.2', 'homeassistant==2025.10.4', 'pytest-asyncio==1.2.0', 'pytest-xdist==3.8.0'],
)