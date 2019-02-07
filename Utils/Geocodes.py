from django.conf import settings

PROJECTION_CURVE_1 = settings.PROJECTION_CURVE_1
PROJECTION_CURVE_2 = settings.PROJECTION_CURVE_2
PROJECTION_MAP_1 = settings.PROJECTION_MAP_1
PROJECTION_MAP_2 = settings.PROJECTION_MAP_2
PROJECTION_SPLIT_LIMIT = settings.PROJECTION_SPLIT_LIMIT



def geodep_from_geocode(geocode):
    if geocode.startswith("group") or geocode.startswith("FR99"):
        return geocode
    return 'FR992%s' % (geocode[2:4])

def curvproj_from_geodep(geocode):
    if geocode.startswith('group'):
        projection = PROJECTION_CURVE_2
    else:
        department = int(geocode[-2:])
        if department == 99:
            projection = PROJECTION_CURVE_2
        else:
            projection = (PROJECTION_CURVE_1 if department <= PROJECTION_SPLIT_LIMIT
                          else PROJECTION_CURVE_2)
    return projection

def mapproj_from_geocode(geocode):
    if geocode.startswith("group"):
        projection = PROJECTION_MAP_2
    else:
        department = int(geocode[2:4])
        if department == 99:
            projection = PROJECTION_MAP_2
        else:
            projection = (PROJECTION_MAP_1 if department <= PROJECTION_SPLIT_LIMIT
                          else PROJECTION_MAP_2)
    return projection
