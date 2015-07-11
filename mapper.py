#-------------------------------------------------------------------------------
# Name:        mapper
# Purpose:      geo code a list of co-ords and draw on a map
#
# Author:      fran
#
# Created:     10/07/2015
# Copyright:   (c) fran 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import geopy.geocoders
import matplotlib.pyplot as plt
import xlrd

from helpers import xls_to_list_of_dicts
from geopy import geocoders
from mpl_toolkits.basemap import Basemap as bm
from random import randint

debug = True
recursion = 0

#Next 20 or so lines snipped from __int.py of geopy
# & adapted a little incl.  useless coders commented out
#
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
#    "OpenMapQuest",
    "NaviData",
    "Nominatim",
#    "YahooPlaceFinder", # needs API key and more
#    "LiveAddress",     # ditto
    'Yandex',
#    "What3Words",
)


def add_longitude_and_latitude(addresses, coders ):
    """
    appends longitude and latudes to list of addresses
    addresses are stored as dicts with at least 'address' key
    uses a random geocoder for each address (privacy anti-snooping)
    """
    global recursion

    new_addresses, not_coded =[], []

    for address in addresses:
        # get a random geocoder
        coder = coders[randint(0,len(coders)-1)]
        if debug: print "Using %s to code %s" % (coder, address['Address'])

        # It's a kinda magic !
        # getattr return a ref to the method in geopy.geocoders named eval(geolocator)
        locator = getattr( geopy.geocoders, coder)()

        try:
            #location = locator.geocode("42 st agnes pk, crumlin, dublin, ireland")
            location = locator.geocode(address['Address'])
        except Exception as GeocoderParseError:
            recursion = recursion + 1
            if debug: print "Recursive call %s" % recursion
            # new_coders is coders with the current coder removed
            new_coders = list(coders)
            new_coders.remove(coder)
            #NB recursive call using a LIST of 1 element
            # does NOT ==> will never go more than 2 calls deep
            address, missed=add_longitude_and_latitude([address], new_coders)
            not_coded.append(missed)
        else:
            if location == None:
                if debug: print "Empty result for %s %s" % (coder, address['Address'])
                # collect addresses that didn't code
                address['geocoder'] = coder
                not_coded.append(address)
                continue
            else:
    #            if debug: print address['Site'], location.longitude, location.latitude
                address['longitude'], address['latitude'], address['geocoder'] =  \
                         location.longitude, location.latitude, coder

        new_addresses.append(address)

    print
    return new_addresses, not_coded

xls = r'C:\Users\fran\Python\mapper\Site list.xlsx'
tabName = 'Sites'

def main():
    #
    # TODO Add argparse
    #

    #read in site list
    sites = xls_to_list_of_dicts(xls, tabName )

    # Add longitude & latitude
    sites_coded, sites_uncoded = add_longitude_and_latitude(sites, geocoders)
    print sites




if __name__ == '__main__':
    main()
