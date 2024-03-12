# This module contains all the functions necessary to process L1T ASTER data 
# for quantitative analysis. 
# All functions are called in the function aster_preprocessing() which 
# takes an ee_i.Geometry object defining the area of interest. 
# It returns a dictionary containing the processed image as an ee_i.Image object, 
# the crs and the crs transform. 

from .__init__ import initialize_ee
ee_i = initialize_ee()

from .data_conversion import aster_dn2toa, aster_radiance, aster_reflectance, aster_brightness_temp
from .masks import water_mask, aster_cloud_mask, aster_snow_mask

# Filter ASTER imagery that contain all bands
def aster_bands_present_filter(collection, bands = ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B13']):
    """
    Takes an image collection, assumed to be ASTER imagery.
    Returns a filtered image collection that contains only
    images with all nine VIR/SWIR bands and all 5 TIR bands.
    By default, filters for the bands necessary to calculate the cloud mask.
    """
    filters = [ee_i.Filter.listContains('ORIGINAL_BANDS_PRESENT', band) for band in bands]
    
    return collection.filter(ee_i.Filter.And(filters))

def aster_image_preprocessing(image, bands=['B01', 'B02', 'B3N', 'B04', 'B13'], masks = ['cloud']):
   """
   Converts the specified bands in an image from digital number to 
   at-sensor reflectance (VIS/SWIR) and at-satellite brightness temperature (TIR),
   then applies the specified masks (snow, water, and cloud).
   """
   snow_bands = {'B01', 'B04'}
   if 'snow' in masks:
      bands = list(snow_bands.union(bands))

   cloud_bands = {'B01', 'B02', 'B3N', 'B04', 'B13'}
   if 'cloud' in masks:
      bands = list(cloud_bands.union(bands))
   
   mask_dict = {
      'cloud': aster_cloud_mask,
      'snow': aster_snow_mask,
      'water': water_mask
   }
   
   image = aster_dn2toa(image, bands)
   for mask in masks:
      image = mask_dict[mask](image)
   return image



def aster_collection_preprocessing(geom, bands = ['B01', 'B02', 'B3N', 'B04', 'B13'], masks = ['cloud', 'snow', 'water']):
  """
  Takes a geometry (ee_i.ComputedObject, ee_i.FeatureCollection, or ee_i.Geometry).
  Collects ASTER satellite imagery that intersects the geometry and
  implements all available preprocessing functions.
  Reduces resulting ImageCollection to a single Image object
  by calculating the median pixel value.
  Clips the image to the geometry.
  Returns a dictionary containing the processed image along with 
  the crs and crs_transform metadata of the first image in the
  ImageCollection that intersects the geometry.
  """
  coll = ee_i.ImageCollection("ASTER/AST_L1T_003")
  coll = coll.filterBounds(geom)
  coll = aster_bands_present_filter(coll, bands = bands)
  crs = coll.first().select(bands[0]).projection().getInfo()['crs']
  transform = coll.first().select(bands[0]).projection().getInfo()['transform']
  
  coll = coll.map(lambda x: aster_image_preprocessing(x, bands, masks))
  coll = coll.map(lambda x: x.clip(geom))
  
  # coll = coll.median().clip(geom)
  return {'imagery': coll, 'crs': crs, 'transform': transform}
