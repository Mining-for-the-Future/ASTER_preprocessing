from .preprocessing import ee_i

def vis_params(img_dict, bands):
    """
    Returns a dictionary of visualization parameters for ASTER imagery.
    """
    geometry = img_dict['imagery'].geometry()
    
    percentiles = img_dict['imagery'].select(bands).reduceRegion(
        reducer =ee_i.Reducer.percentile([5, 95]), 
        geometry = geometry, 
        crs = img_dict['crs'], 
        crsTransform = img_dict['transform'],
        bestEffort = True).getInfo()
    b_p5 = [band + '_p5' for band in bands]
    b_p95 = [band + '_p95' for band in bands]
    mins = [percentiles[min] for min in b_p5]
    maxs = [percentiles[max] for max in b_p95]
    vis_params = {'min': mins, 'max': maxs, 'bands': bands}
    return vis_params


def vis_params_image(image, bands):
    geometry = image.geometry()
    projection = image.select(bands[0]).projection().getInfo()
    
    percentiles = image.select(bands).reduceRegion(
        reducer = ee_i.Reducer.percentile([5, 95]),
        geometry = geometry,
        crs = projection['crs'],
        crsTransform = projection['transform'],
        bestEffort = True).getInfo()

    b_p5 = [band + '_p5' for band in bands]
    b_p95 = [band + '_p95' for band in bands]
    mins = [percentiles[min] for min in b_p5]
    maxs = [percentiles[max] for max in b_p95]
    vis_params = {'min': mins, 'max': maxs, 'bands': bands}
    return vis_params