
#Next 20 or so lines snipped from __int.py of geopy
#
# Is there a pythonic way to import this directly ??
geocoders = (
#    "get_geocoder_for_service",
    "ArcGIS",
#    "Baidu",   # needs API key
#    "Bing",    # needs API key
    "DataBC",
    "GeocoderDotUS",
    "GeocodeFarm",
#    "GeoNames",    # Needs a login!
    "GoogleV3",
#    "IGNFrance",   # needs API key
#    "OpenCage",    # needs API key
    "OpenMapQuest",
    "NaviData",
    "Nominatim",
#    "YahooPlaceFinder", # needs API key and more
#    "LiveAddress",     # ditto
    'Yandex',
#    "What3Words",
)

import geopy.geocoders

for geolocator in geocoders:
    print geolocator

    # It's a kinda magic !
    # getattr return a ref to the method in geopy.geocoders named eval(geolocator)
    locator = getattr( geopy.geocoders, geolocator)()
    #location = locator.geocode("42 st agnes pk, crumlin, dublin, ireland")
    location = locator.geocode(address['Address'])
    if location == None:
        print "Empty result for %s" %geolocator
    else:
        print location.longitude, location.latitude
    print
