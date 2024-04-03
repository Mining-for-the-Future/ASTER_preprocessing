from .preprocessing import ee_i, aster_collection_preprocessing, get_best_image, default_bands, default_masks, default_cloudcover

def get_geom_from_feat(feat):
    return feat.geometry()

def coll_preprocess_from_feat(feat, bands = default_bands, masks = default_masks, cloudcover = default_cloudcover):
    geom = get_geom_from_feat(feat)
    return aster_collection_preprocessing(geom, bands, masks, cloudcover)

def get_best_image_from_feat(feat, bands = default_bands, masks = default_masks, cloudcover = default_cloudcover):
    return get_best_image(coll_preprocess_from_feat(feat, bands, masks, cloudcover))

def image_coll_from_feat_coll(feat_coll, bands = default_bands, masks = default_masks, cloudcover = default_cloudcover):
    return ee_i.ImageCollection(feat_coll.map(lambda x: get_best_image_from_feat(x, bands, masks, cloudcover)))