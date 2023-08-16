# This module contains all the functions necessary to process L1T ASTER data 
# for quantitative analysis. 
# All functions are called in the function aster_pre_processing() which 
# takes an ee.Geometry object defining the area of interest. 
# It returns a dictionary containing the processed image as an ee.Image object, 
# the crs and the crs transform. 

from data_conversion import aster_radiance, aster_reflectance, aster_brightness_temp
from masks import water_mask, aster_cloud_mask, aster_snow_mask
import ee
ee.Initialize()

# Filter ASTER imagery that contain all bands
def aster_bands_present_filter(collection):
    """
    Takes an image collection, assumed to be ASTER imagery.
    Returns a filtered image collection that contains only
    images with all nine VIR/SWIR bands and all 5 TIR bands.
    """
    return collection.filter(ee.Filter.And(
    ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B01'),
    ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B02'),
    ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B3N'),
    ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B04'),
    ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B05'),
    ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B06'),
    ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B07'),
    ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B08'),
    ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B09'),
    ee.Filter.listContains('ORIGINAL_BANDS_PRESENT', 'B13')
))

def aster_preprocessing(geom):
  """
  Takes a geometry (ComputedObject, Geometry, or FeatureCollection object).
  Collects ASTER satellite imagery that intersects the geometry and
  implements all available preprocessing functions.
  Reduces resulting ImageCollection to a single Image object
  by calculating the median pixel value.
  Clips the image to the geometry.
  Returns a dictionary containing the processed image along with 
  the crs and crs_transform metadata of the first image in the
  ImageCollection that intersects the geometry.
  """
  coll = ee.ImageCollection("ASTER/AST_L1T_003")
  coll = coll.filterBounds(geom)
  coll = aster_bands_present_filter(coll)
  crs = coll.first().select('B01').projection().getInfo()['crs']
  transform = coll.first().select('B01').projection().getInfo()['transform']
  coll = coll.map(aster_radiance)
  coll = coll.map(aster_reflectance)
  coll = coll.map(aster_brightness_temp)
  coll = coll.map(water_mask)
  coll = coll.map(aster_cloud_mask)
  coll = coll.map(aster_snow_mask)
  coll = coll.median().clip(geom)
  return {'imagery': coll, 'crs': crs, 'transform': transform}