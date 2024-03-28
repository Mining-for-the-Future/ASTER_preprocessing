from .preprocessing import ee_i
import utm

def get_zone_no_from_lat_lon_ee(latitude, longitude):
    variables = {'latitude': latitude, 'longitude': longitude}

    test_32 = ee_i.Number.expression(
        expression = '56 <= latitude & latitude < 64 & 3 <= longitude & longitude < 12',
        vars = variables
    )

    test_31 = ee_i.Number.expression(
        expression = '72 <= latitude & latitude <= 84 & longitude >= 0 & longitude < 9',
        vars = variables
    )

    test_33 = ee_i.Number.expression(
        expression = '72 <= latitude & latitude <= 84 & longitude >= 0 & longitude < 21',
        vars = variables
    )

    test_35 = ee_i.Number.expression(
        expression = '72 <= latitude & latitude <= 84 & longitude >= 0 & longitude < 33',
        vars = variables
    )

    test_37 = ee_i.Number.expression(
        expression = '72 <= latitude & latitude <= 84 & longitude >= 0 & longitude < 42',
        vars = variables
    )

    zone_from_lon = ee_i.Number.expression(
        expression = '((longitude + 180) / 6) + 1',
        vars = variables
    ).floor()

    result = ee_i.Number(ee_i.Algorithms.If(
        test_32, trueCase = 32, falseCase = ee_i.Algorithms.If(
            test_31, trueCase = 31, falseCase = ee_i.Algorithms.If(
                test_33, trueCase = 33, falseCase = ee_i.Algorithms.If(
                    test_35, trueCase = 35, falseCase = ee_i.Algorithms.If(
                        test_37, trueCase = 37, falseCase = zone_from_lon
                    )
                )
            )
        )
    )).uint8()

    return result

def get_utm_proj_from_poly(geom):
    coordinates = geom.centroid(maxError = 1).coordinates()
    latitude = coordinates.getNumber(1)
    longitude = coordinates.getNumber(0)
    zone_no = get_zone_no_from_lat_lon_ee(latitude, longitude)
    epsg_no = ee_i.Number(ee_i.Algorithms.If(
        latitude.gte(0),
        trueCase = zone_no.add(32600),
        falseCase = zone_no.add(32700)
    ))
    epsg_str = ee_i.Algorithms.String(epsg_no)
    epsg_code = ee_i.String('EPSG:').cat(ee_i.String(epsg_str))
    return ee_i.Projection(epsg_code).atScale(1)
