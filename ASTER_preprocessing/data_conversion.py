from .preprocessing import ee_i
from warnings import warn

def __no_valid_bands_result__(image):
    """
    A function that handles the case when no valid bands are found in an image.

    Args:
        image (any): The image for which valid bands are being checked.

    Returns:
        any: The original image if no valid bands are found.

    Raises:
        UserWarning: If no valid bands are found in the image.
    """
    warn("No valid bands found in image. Function not run.", UserWarning)
    return image

def __call_function_with_bands__(image, user_bands, required_bands, function):
    """
    A function that calls another function with specified bands. 
    
    Args:
        image: The image to operate on.
        user_bands: The bands provided by the user.
        required_bands: The bands required for the operation.
        function: The function to be called with the specified bands.
    
    Returns:
        The result of calling the function on the image with the specified bands.
    """
    if len(user_bands) == 0:
        bands = image.bandNames()
    else:
        bands = ee_i.List(user_bands)

    bands = bands.filter(ee_i.Filter.inList('item', required_bands))
    return ee_i.Algorithms.If(bands.length().eq(0), trueCase = __no_valid_bands_result__(image), falseCase = ee_i.Image(function(image, bands)))

def __aster_radiance__(image):
  """
  Takes an ASTER image with pixel values in DN (as stored by Googel Earth Engine).
  Converts DN to at-sensor radiance across all bands.
  """
  coefficients = ee_i.ImageCollection(
        image.bandNames().map(lambda band: ee_i.Image(image.getNumber(ee_i.String('GAIN_COEFFICIENT_').cat(band))).float())
    ).toBands().rename(image.bandNames())

  radiance = image.subtract(1).multiply(coefficients)

  return ee_i.Image(image.addBands(radiance, None, True))

def __aster_reflectance__(image, bands):
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

  irradiance_vals = ee_i.Dictionary(dict(zip(
    ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09'],
    [1845.99, 1555.74, 1119.47, 231.25, 79.81, 74.99, 68.66, 59.74, 56.92]
  )))
    
  irradiance = bands.map(lambda band: irradiance_vals.get(band))
  irradiance = ee_i.Image.constant(irradiance)

  # The .select() method requires two lists, one for the band selection and one for the new names.
  reflectance = image \
        .select(bands, bands) \
        .multiply(reflectanceFactor) \
        .divide(irradiance)

  return ee_i.Image(image.addBands(reflectance, None, True))

def __aster_brightness_temp__(image, bands = []):
  """
  Takes an ASTER image with pixel values in at-sensor radiance.
  Converts TIR bands to at-satellite brightness temperature.
  """
    
  k_vals = ee_i.Dictionary({
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
  })
  
  K1_vals = bands.map(lambda band: ee_i.Dictionary(k_vals.get(band)).get('K1'))
  K1_vals = ee_i.Image.constant(K1_vals)

  K2_vals = bands.map(lambda band: ee_i.Dictionary(k_vals.get(band)).get('K2'))
  K2_vals = ee_i.Image.constant(K2_vals)
  
  T = image.expression('K2 / (log(K1/L + 1))',
                   {'K1': K1_vals, 'K2': K2_vals, 'L': image.select(bands)}
  )

  return ee_i.Image(image.addBands(T.rename(bands), None, True))

def aster_dn2toa(image, bands):
  """
  Wrapper function that takes an aster image and converts all pixel values from 
  digital number to radiance and then converts the specified bands from radiance
  to top-of-atmosphere reflectance (bands 1 - 9) and at-satellite brightness temperature (bands 10 - 14).
  """
  img = __aster_radiance__(image)
  img = __call_function_with_bands__(img, bands, ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09'], __aster_reflectance__)
  img = __call_function_with_bands__(img, bands, ['B10', 'B11', 'B12', 'B13', 'B14'], __aster_brightness_temp__)
  return ee_i.Image(img)
