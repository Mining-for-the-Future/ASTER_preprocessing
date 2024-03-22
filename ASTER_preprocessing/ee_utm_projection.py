from .preprocessing import ee_i
import utm

def get_utm_proj_from_coords(coordinates):
    """
    Returns a UTM projection based on the input coordinates.
    
    Parameters
    ----------
    coordinates : list
        A list containing the longitude and latitude of a point in decimal degrees.
        The format should be [Longitude, Latitude].

    Returns
    -------
    ee.Projection
        An Earth Engine projection object in Universal Transverse Mercator (UTM) projection.

    Raises
    ------
    ValueError
        If the input coordinates are not in the format [Longitude, Latitude].
    """
    
    # Check if the input is in the format [Longitude, Latitude]
    if len(coordinates) != 2:
        raise ValueError("Input coordinates should be in the format [Longitude, Latitude].")

    # Extract longitude and latitude from the input
    longitude, latitude = coordinates

    # Calculate UTM zone and hemisphere
    utm_zone = utm.latlon_to_zone_number(latitude, longitude)
    
    # Determine the EPSG code based on the hemisphere
    if latitude >= 0:
        epsg_code = 32600 + utm_zone
    else:
        epsg_code = 32700 + utm_zone

    epsg_str = 'EPSG:'+str(epsg_code)
    projection = ee_i.Projection(epsg_str).atScale(1)

    return projection

