from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='algoql',
    version='0.0.1',
    author='Marcin Zawiejski',
    author_email='dragmz@gmail.com',
    packages=['algoql'],
    license='LICENSE.txt',
    description='Algorand streamin Query Language',
    install_requires=required,
)