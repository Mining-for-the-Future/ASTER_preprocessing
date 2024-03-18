from .preprocessing import ee_i
from .ee_utm_projection import get_utm_proj_from_coords

def vis_params_image(image, bands):
    geometry = image.geometry()
    projection = get_utm_proj_from_coords(geometry.centroid().coordinates().getInfo())
    
    percentiles = image.select(bands).reduceRegion(
        reducer = ee_i.Reducer.percentile([5, 95]),
        geometry = geometry,
        crs = projection.crs(),
        scale = 30,
        bestEffort = True).getInfo()

    b_p5 = [band + '_p5' for band in bands]
    b_p95 = [band + '_p95' for band in bands]
    mins = [percentiles[min] for min in b_p5]
    maxs = [percentiles[max] for max in b_p95]
    vis_params = {'min': mins, 'max': maxs, 'bands': bands}
    return vis_params