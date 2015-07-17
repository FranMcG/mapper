
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


with open_workbook(fileName) as wb:
    ##### Need to confirm this  #####
    # we are using the 2nd sheet here
    #worksheet = wb.sheet_by_index(0)
    worksheet = wb.sheet_by_name(sheetName)
    # getting number or rows and setting current row as 0 -e.g first
    num_rows, curr_row = worksheet.nrows - 1, 0
    # retrieving keys values(first row values)
    keyValues = [x.value for x in worksheet.row(0)]
    # building dict
    data = []
    # iterating through all rows and fulfilling our dictionary
    while curr_row < min(num_rows,last_row):
        d = dict()
        curr_row += 1
        for idx, val in enumerate(worksheet.row(curr_row)):
            x = val.value
            if x:
                if isinstance(x,unicode):
                    d[keyValues[idx]]= x
                else:
                    d[keyValues[idx]]= str( int(x) )
        data.append(d)

