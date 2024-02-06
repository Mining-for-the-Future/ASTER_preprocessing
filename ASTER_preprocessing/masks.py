from .__init__ import initialize_ee
ee_i = initialize_ee()

def water_mask(image):
  """
  Takes an ASTER image and masks pixels that are classified as surface water 
  in the month and year that the image was captured according to the
  JRC Monthly Water History, v1.4 dataset 
  (https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory).
  Returns a masked image.
  """
  month_water = ee_i.ImageCollection("JRC/GSW1_4/MonthlyHistory")
  m = image.date().get('month')
  y = image.date().get('year')
  water = month_water.filter(ee_i.Filter.And(
      ee_i.Filter.eq('month', m),
      ee_i.Filter.eq('year', y)
  )).mode()
  # the mode() method call is necessary because the filter() method returns an image collection containing one image. 
  # mode() reduces it to a single image object
  mask = water.neq(2)
  return image.updateMask(mask)


def aster_ndsi(image):
  """
  Takes an ASTER image and calculates the Normalized Difference Snow Index.
  Returns an image with a single band.
  """
  return (image.select('B01').subtract(image.select('B04')).divide((image.select('B01').add(image.select('B04'))))).rename('ndsi')

def ac_filt1(image):
  """
  Takes an ASTER image and applies filter 1 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """
  filt1 = image.select('B02').gt(0.08)
  return image.updateMask(filt1)

def ac_filt2(image):
  """
  Takes an ASTER image and applies filter 2 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """  
  filt2 = aster_ndsi(image).lt(0.7)
  return image.updateMask(filt2)

def ac_filt3(image):
  """
  Takes an ASTER image and applies filter 3 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """
  filt3 = image.select('B13').lt(300)
  return image.updateMask(filt3)

def ac_filt4(image):
  """
  Takes an ASTER image and applies filter 4 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """
  filt4 = ((image.select('B04').multiply(-1)).add(1)).multiply(image.select('B13')).lt(240)
  return image.updateMask(filt4)

def ac_filt5(image):
  """
  Takes an ASTER image and applies filter 5 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """
  filt5 = image.select('B3N').divide(image.select('B02')).lt(2)
  return image.updateMask(filt5)

def ac_filt6(image):
  """
  Takes an ASTER image and applies filter 6 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """
  filt6 = image.select('B3N').divide(image.select('B01')).lt(2.3)
  return image.updateMask(filt6)

def ac_filt7(image):
  """
  Takes an ASTER image and applies filter 7 in the first pass of Hulley and Hook's (2008) NACMA.
  Returns a masked image.
  """
  filt7 = image.select('B3N').divide(image.select('B04')).gt(0.83)
  return image.updateMask(filt7)

def aster_cloud_mask(image):
  """
  Takes an ASTER image and applies the seven filters in the first pass
  of the New Aster Cloud Mask Algorithm (NACMA) proposed by Hulley and Hook (2008).
  Returns a masked image.
  """
  img = ac_filt1(image)
  img = ac_filt2(img)
  img = ac_filt3(img)
  img = ac_filt4(img)
  img = ac_filt5(img)
  img = ac_filt6(img)
  img = ac_filt7(img)
  # The seven filters identify pixels that ARE clouds and mask the rest.
  # ee_i.Image.unmask() replaces the masked pixels of an image with a constant value.
  # The .eq() filter returns a binary mask identifying which pixels match the
  # constant value assigned in the unmask() method, i.e., pixels that ARE NOT clouds.
  mask = img.unmask(ee_i.Image.constant(-1)).eq(-1)
  return image.updateMask(mask)


def aster_snow_mask(image):
  """
  Takes an ASTER image and masks out pixels with NDSI greater than 0.4.
  Returns a masked image.
  """
  mask = aster_ndsi(image).lt(0.4)
  return image.updateMask(mask)