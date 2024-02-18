"""
A package for preprocessing ASTER satellite imagery within Google Earth Engine's Python API.
"""

__version__ = '0.1.0'
__author__ = 'Eli Weaverdyck and Craig Nicolay'

try:
    import ee
except ImportError as e:
    if "No module named 'StringIO'" in str(e):
        from io import StringIO
        import ee
    else:
        raise

def initialize_ee():
    """
    Initialize the Earth Engine API by authenticating and initializing the connection.
    Returns:
    ee: The initialized Earth Engine API.
    """
    ee.Authenticate()
    ee.Initialize()
    return ee
