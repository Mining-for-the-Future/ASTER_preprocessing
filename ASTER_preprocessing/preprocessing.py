from .__init__ import initialize_ee
ee_i = initialize_ee()

from .data_conversion import aster_dn2toa
from .masks import water_mask, aster_cloud_mask, aster_snow_mask
from .ee_utm_projection import get_utm_zone_code_from_poly

# Filter ASTER imagery that contain all bands
def aster_bands_present_filter(collection, bands):
    """
    Takes an image collection, assumed to be ASTER imagery.
    Returns a filtered image collection that contains only
    images with all of the specified bands.
    """
    filters = [ee_i.Filter.listContains('ORIGINAL_BANDS_PRESENT', band) for band in bands]
    
    return collection.filter(ee_i.Filter.And(filters))

def get_geom_area(geom, proj):
   return geom.area(maxError = 1, proj = proj)

def get_pixel_area(image, geom, proj):
   return ee_i.Number(
      image.pixelArea().
      multiply(image.mask()).
      reduceRegion(ee_i.Reducer.sum(), geom, crs = proj.crs(), scale = proj.nominalScale(), bestEffort = True)
      .values().reduce(ee_i.Reducer.mean()))

def set_geom_coverage_property(image, geom, geom_area, proj):
   return image.set({'geom_coverage': get_pixel_area(image, geom, proj).divide(geom_area)})

def aster_image_preprocessing(image, bands=['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B10', 'B11', 'B12', 'B13', 'B14'], masks = []):
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
   
   image = ee_i.Image(image.select(image.get('ORIGINAL_BANDS_PRESENT')))
   image = aster_dn2toa(image, bands)
   for mask in masks:
      image = mask_dict[mask](image)
   return image



def aster_collection_preprocessing(geom, bands = ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B10', 'B11', 'B12', 'B13', 'B14'], masks = [], cloudcover = 25):
  """
  Generate a preprocessed ASTER image collection based on the input geometry, specified bands, and masks.
  
  Parameters:
  - geom: The geometry to filter the ASTER image collection by.
  - bands: List of bands to include in the preprocessing (default is ['B01', 'B02', 'B3N', 'B04', 'B13']).
  - masks: List of masks to apply during preprocessing (default includes all available masks: ['cloud', 'snow', 'water']).
  - cloudcover: Maximum image cloud cover percentage (default is 25).
  
  Returns:
  ee.ImageCollection: Preprocessed ASTER image collection clipped to the input geometry.
  """
  geom = ee_i.Geometry(ee_i.Algorithms.If(
    ee_i.Algorithms.IsEqual(ee_i.Algorithms.ObjectType(geom), 'Feature'),
    trueCase = geom.geometry(),
    falseCase = geom
   ))
  
  projection = get_utm_zone_code_from_poly(geom)
  geom_area = get_geom_area(geom, projection)

  snow_bands = {'B01', 'B04'}
  if 'snow' in masks:
    bands = list(snow_bands.union(bands))
  cloud_bands = {'B01', 'B02', 'B3N', 'B04', 'B13'}
  if 'cloud' in masks:
    bands = list(cloud_bands.union(bands)) 

  coll = ee_i.ImageCollection("ASTER/AST_L1T_003")
  coll = coll.filterBounds(geom)
  coll = coll.filter(ee_i.Filter.lte('CLOUDCOVER', cloudcover))
  coll = aster_bands_present_filter(coll, bands = bands)
  coll = coll.map(lambda x: x.clip(geom))
  
  coll = coll.map(lambda x: aster_image_preprocessing(x, bands, masks))
  coll = coll.map(lambda x: set_geom_coverage_property(x, geom, geom_area, projection))
  coll = coll.filter(ee_i.Filter.gte('geom_coverage', 0.75))

  return coll
