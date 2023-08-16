from setuptools import setup

setup(
    name = 'ASTER_Preprocessing',
    version = '0.1.0',
    description = "A package for preprocessing ASTER satellite imagery within Google Earth Engine's Python API.",
    url = 'https://github.com/Mining-for-the-Future/ASTER_preprocessing',
    author = 'Eli Weaverdyck and Craig Nicolay',
    author_email = 'eweaverdyck@gmail.com',
    license = 'MIT',
    packages = ['ASTER_preprocessing'],
    install_requires = ['ee']
)