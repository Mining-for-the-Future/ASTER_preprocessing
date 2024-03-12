from .preprocessing import ee_i

def aster_radiance(image):
  """
  Takes an ASTER image with pixel values in DN (as stored by Googel Earth Engine).
  Converts DN to at-sensor radiance across all bands.
  """
  coefficients = ee_i.ImageCollection(
        image.bandNames().map(lambda band: ee_i.Image(image.getNumber(ee_i.String('GAIN_COEFFICIENT_').cat(band))).float())
    ).toBands().rename(image.bandNames())

  radiance = image.subtract(1).multiply(coefficients)

  return image.addBands(radiance, None, True)

def aster_reflectance(image, bands = ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09']):
  """
  Takes an ASTER image with pixel values in at-sensor radiance.
  Converts VIS/SWIR bands (B01 - B09) to at-sensor reflectance.
  """
  dayOfYear = image.date().getRelative('day', 'year')

  earthSunDistance = ee_i.Image().expression(
        '1 - 0.01672 * cos(0.01720209895 * (dayOfYear - 4))',
        {'dayOfYear': dayOfYear}
    )

  sunElevation = image.getNumber('SOLAR_ELEVATION')

  sunZen = ee_i.Image().expression(
        '(90 - sunElevation) * pi/180',
        {'sunElevation': sunElevation, 'pi': 3.14159265359}
    )

  reflectanceFactor = ee_i.Image().expression(
        'pi * pow(earthSunDistance, 2) / cos(sunZen)',
        {'earthSunDistance': earthSunDistance, 'sunZen': sunZen, 'pi': 3.14159265359}
    )

  irradiance_vals = dict(zip(
    ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09'],
    [1845.99, 1555.74, 1119.47, 231.25, 79.81, 74.99, 68.66, 59.74, 56.92]
  ))
  vis_bands = set(['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09'])
  bands = list(vis_bands.intersection(bands))
  
  irradiance = [irradiance_vals[band] for band in bands]

  # The .select() method requires two lists, one for the band selection and one for the new names.
  reflectance = image \
        .select(bands, bands) \
        .multiply(reflectanceFactor) \
        .divide(irradiance)

  return image.addBands(reflectance, None, True)

def aster_brightness_temp(image, bands = ['B10', 'B11', 'B12', 'B13', 'B14']):
  """
  Takes an ASTER image with pixel values in at-sensor radiance.
  Converts TIR bands to at-satellite brightness temperature.
  """
  k_vals = {
  'B10':{
    'K1': 3040.136402,
    'K2': 1735.337945
  },
  'B11':{
    'K1': 2482.375199,
    'K2': 1666.398761
  },
  'B12':{
    'K1': 1935.060183,
    'K2': 1585.420044
  },
  'B13':{
    'K1': 866.468575,
    'K2': 1350.069147
  },
  'B14':{
    'K1': 641.326517,
    'K2': 1271.221673
  }
  }

  tir_bands = set(['B10', 'B11', 'B12', 'B13', 'B14'])
  bands = list(tir_bands.intersection(bands))
  
  K1_vals = [k_vals[band]['K1'] for band in bands]
  K2_vals = [k_vals[band]['K2'] for band in bands]
  T = image.expression('K2 / (log(K1/L + 1))',
                   {'K1': K1_vals, 'K2': K2_vals, 'L': image.select(bands)}
  )

  return image.addBands(T.rename(bands), None, True)

# def aster_brightness_temp_all_tir(image):
#   """
#   Takes an ASTER image with pixel values in at-sensor radiance.
#   Converts TIR band B13 to at-satellite brightness temperature.
#   """
#   K1_vals = [3040.136402, 2482.375199, 1935.060183, 866.468575, 641.326517]
#   K2_vals = [1735.337945, 1666.398761, 1585.420044, 1350.069147, 1271.221673]
#   T = image.expression('K2 / (log(K1/L + 1))',
#                    {'K1': K1_vals, 'K2': K2_vals, 'L': image.select('B10', 'B11', 'B12', 'B13', 'B14')}
#   )

#   return image.addBands(T.rename('B10', 'B11', 'B12', 'B13', 'B14'), None, True)

def aster_dn2toa(image, bands):
  """
  Wrapper function that takes an aster image and converts all pixel values from 
  digital number to top-of-atmosphere reflectance (bands 1 - 9) and 
  at-satellite brightness temperature (bands 10 - 14).
  """
  img = aster_radiance(image)
  img = aster_reflectance(img, bands)
  img = aster_brightness_temp(img, bands)
  return img
