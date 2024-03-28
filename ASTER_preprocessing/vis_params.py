from .preprocessing import ee_i
from .ee_utm_projection import get_utm_zone_code_from_poly

def vis_params_image(image, bands):
    geometry = image.geometry()
    projection = get_utm_zone_code_from_poly(geometry)
    
    percentiles = image.select(bands).reduceRegion(
        reducer = ee_i.Reducer.percentile([1, 99]),
        geometry = geometry,
        crs = projection.crs(),
        scale = 30,
        bestEffort = True).getInfo()

    b_p1 = [band + '_p1' for band in bands]
    b_p99 = [band + '_p99' for band in bands]
    mins = [percentiles[min] for min in b_p1]
    maxs = [percentiles[max] for max in b_p99]
    vis_params = {'min': mins, 'max': maxs, 'bands': bands}
    return vis_params