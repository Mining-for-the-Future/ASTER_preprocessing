# ASTER preprocessing
This package contains functions for preprocessing ASTER satellite imagery in Google Earth Engine's Python API.

## Installation
To install, enter the following code in your terminal. Ensure that you are in the correct environment.  
`pip install git+https://github.com/Mining-for-the-Future/ASTER_preprocessing.git`

## Description
The package consists of three modules: `preprocessing`, `data_conversion`, and `masks`.

The `preprocessing` module contains the wrapper function `aster_preprocessing`.
This function takes a geometry object (ee.ComputedObject, ee.FeatureCollection, or ee.Geometry) and creates an ImageCollection
of ASTER imagery intersecting that geometry. It then applies all preprocessing functions, reduces the ImageCollection to an Image object by taking the median pixel value, and clips the image to the geometry.
The function returns a dictionary containing the preprocessed image as well as metadata (crs and crs transform) from one of the original ASTER images. This metadata is helpful for exporting the resulting image.

<details>
<summary>`aster_preprocessing(geometry)`<summary>

**Parameters:**
 | Name | Type |	Description |	Default |
 | --- | --- | --- | --- |
 | `geometry` | `ee.ComputedObject | ee.FeatureCollection | ee.Geometry` | The input geometry. | _required_ |

**Returns:**
 | Type |	Description |	
 | --- | --- | 
 | `dict` | The processed image along with the crs and crs_transform metadata of the first image in the ImageCollection that intersects the geometry. | 
<details>

These functions were originally designed for mineral exploration, so they might not all be applicable for other use cases.
For that reason, the functions can also be used individually.

The `data_conversion` module contains functions that:
* convert the pixel values of ASTER imagery from digital numbers to at-sensor-radiance (`aster_radiance`)[^1]
* convert at-sensor-radiance of visible and shortwave infrared bands to top-of-atmosphere reflectance (`aster_reflectance`)[^1]
* convert at-sensor-radiance of all thermal infrared bands to top-of-atmosphere brightness-temperature (`aster_brightness_temp_all_tir`).[^2] This function is not used elsewhere in this package.
* convert at-sensor-radiance of band 13 to top-of-atmosphere brightness-temperature (`aster_brightness_temp`).[^2] This function is used in the `aster_cloud_mask` function in the `masks` module.
* perform all conversions for all bands in a single function (`aster_data_conversion`).


The `masks` module contains a series of functions that mask out certain pixels.
* The `water_mask` function uses monthly historical data on surface water derived from Landsat imagery to remove pixels covered with water.[^3]
* The `aster_cloud_mask` function implements the first pass of the New Aster Cloud Mask Algorithm by Hulley and Hook.[^4]
* The `aster_snow_mask` function calculates the Normalized Difference Snow Index and masks out all pixels with a value greater than 0.4.

When using these functions individually, remember that not all ASTER images contain all the bands. 
The `preprocessing` module contains a function (`aster_bands_present_filter`) that filters out images that lack any of the bands required in the functions called by `aster_preprocessing`.
We recommend that you implement a similar filter when using the other functions individually.

[^1]: Based on [Smith, M. S. “How to convert ASTER radiance values to reflectance. An online guide.” (2007)](https://r.search.yahoo.com/_ylt=AwrFDLoSy9xkBeQHeyJXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Ny/RV=2/RE=1692220307/RO=10/RU=http%3a%2f%2fgeography.middlebury.edu%2fdata%2fgg1002%2fHandouts%2fHow%2520to%2520Convert%2520ASTER%2520Radiance%2520Values%2520to%2520Reflectance.pdf/RK=2/RS=7Jx8xRPJRPcIQWqf0nJyNdub7_k-).
[^2]: Based on [Ghulam, A. "How to calculate reflectance and temperature using ASTER data." (2009)](https://r.search.yahoo.com/_ylt=AwrhbfxJytxkrZIHpx9XNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Ny/RV=2/RE=1692220105/RO=10/RU=http%3a%2f%2fwww.pancroma.com%2fdownloads%2fASTER%2520Temperature%2520and%2520Reflectance.pdf/RK=2/RS=sW4RWF1wzxFwjrtfSngbTNt1iT0-).
[^3]: Pekel, J.-F., A. Cottam, N. Gorelick, and A. S. Belward. "High-resolution mapping of global surface water and its long-term changes." *Nature* 540, 418-422 (2016). The dataset used here is the [JRC Montly Water History, v1.4 image collection](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_MonthlyHistory#citations).
[^4]: [Hulley, G. C. and S. J. Hook. "A new methodology for cloud detection and classification with ASTER data." *Geophysical Research Letters* 35, L16812 (2008)](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2008GL034644).
