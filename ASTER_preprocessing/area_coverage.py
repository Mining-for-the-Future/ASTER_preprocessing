from .preprocessing import ee_i

def get_geom_area(geom, proj):
   """
   Calculate the area of a given geometry object.

   Parameters:
     geom (ee.Geometry.Polygon): The geometry object for which to calculate the area.
     proj (ee.Projection): The projection to use for the calculation.

   Returns:
     The calculated area of the geometry object.
   """
   return geom.area(maxError = 1, proj = proj)

def get_pixel_area(image, geom, proj):
   """
   Compute the pixel area within the specified geometry and projection of the given image.
   
   Args:
       image (ee.Image): The input image.
       geom (ee.Geometry.Polygon): The geometry for which to compute the pixel area.
       proj (ee.Projection): The projection information.
       
   Returns:
       ee.Number: The computed pixel area within the specified geometry and projection.
   """
   return ee_i.Number(
      image.pixelArea().
      multiply(image.mask()).
      reduceRegion(ee_i.Reducer.sum(), geom, crs = proj.crs(), scale = proj.nominalScale(), bestEffort = True)
      .values().reduce(ee_i.Reducer.mean()))

def set_geom_coverage_property(image, geom, geom_area, proj):
   """
   Set the 'geom_coverage' property of the image using the provided geometry, geometry area, and projection.

   Parameters:
       image (ee.Image): The image to set the property on.
       geom (ee.Geometry.Polygon): The geometry used for coverage.
       geom_area (ee.Number): The area of the geometry.
       proj (ee.Projection): The projection to use for calculations.

   Returns:
       ee.Image: The image with the 'geom_coverage' property set.
   """
   return image.set({'geom_coverage': get_pixel_area(image, geom, proj).divide(geom_area)})