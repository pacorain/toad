from setuptools import setup

with open("tests/requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name='mockhass',
    version='0.1',
    description='Framework for testing Home Assistant configurations',
    packages=['mockhass'],
    package_dir={'mockhass': 'src/python/mockhass'},
    install_requires=requirements,
)