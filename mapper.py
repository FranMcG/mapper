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

import argparse
import geopy.geocoders
from geopy.exc import *
import matplotlib.pyplot as plt
import os
import simplekml
#import xlrd

from helpers import xls_to_list_of_dicts, list_of_dicts_to_xls
#from geopy import geocoders
from mpl_toolkits.basemap import Basemap
from random import randint

# Next lot used for creating kml tour
from pykml.factory import nsmap
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX
from pykml.parser import Schema
from lxml import etree

# Some variables/statics
debug = False
#debug = True
run_geocoders=True
#run_geocoders=False
WD = r'C:\Users\fran\Python\mapper'
recursion = 0
#default_xls = r'C:\Users\fran\Python\mapper\Site list.xlsx'
default_xls = r'C:\Users\fran\Python\mapper\IPG.xlsx'
coders_used = {}
oc_key = 'd24196d372ad23c9d43b06bf9fb51197'

#Next 20 or so lines snipped from __int.py of geopy
# & adapted a little incl.  useless coders commented out
#
geocoders = (
#    "get_geocoder_for_service",
#    "ArcGIS",
#    "Baidu",   # needs API key
#    "Bing",    # needs API key
#    "DataBC",  # British Colombia only
    "GeocoderDotUS",
    "GeocodeFarm",
#    "GeoNames",    # Needs a login!
    "GoogleV3",
#    "IGNFrance",   # needs API key
#    "OpenCage",    # needs API key
    "OpenMapQuest",
#    "NaviData",     # Polish firm providing info from OSM
    "Nominatim",
#    "YahooPlaceFinder", # needs API key and more
#    "LiveAddress",     # ditto
#    'Yandex',          # Seems to return locations in russia for all input
#    "What3Words",
)


def add_longitude_and_latitude(addresses, coders ):
    """
    appends longitude and latudes to list of addresses
    addresses are stored as dicts with at least 'address' key
    uses a random geocoder for each address (privacy anti-snooping)
    """
    global recursion
    global coders_used

    new_addresses, not_geocoded =[], []

    for address in addresses:
        print 'Processing %s' % address['Address']
        #List for missed adddresses
        missed=[]
        geo_address=[]
        # get a random geocoder
        if len(coders) > 1:
            coder = coders[randint(0,len(coders)-1)]
        else:
            # when there's only one there's only 1
            coder = coders[0]

        #coders_used[address['Site']].append({coder: result)
        if debug: print "   trying %s" % (coder)

        # It's a kinda magic !
        # getattr return a ref to the method in geopy.geocoders named eval(geolocator)
        if coder == 'OpenCage':
            locator = getattr( geopy.geocoders, coder)(oc_key)
        else:
            locator = getattr( geopy.geocoders, coder)()

        try:
            #Try to geocode address
            location = locator.geocode(address['Address'])
        except (GeocoderParseError, GeocoderTimedOut, GeocoderServiceError) as e:
            # keep track of fails
            print "%s failed with error %s" % ( address['Address'], e)
            coders_used[address['Site']].append({coder: 'fail'})
            # new_coders is coders with the current coder removed
            new_coders = list(coders)
            new_coders.remove(coder)
            # If we still have coders do recursive call
            if len(new_coders) > 0:
                recursion = recursion + 1
                if debug: print "Recursive call %s, removing %s from coders" % (recursion, coder)
                #NB recursive call using a LIST of 1 element
                # does NOT ==> recursion will never go more than 2 calls deep!!
                geo_address, missed=add_longitude_and_latitude([address], new_coders)
#                missed=missed[0]
                # single address called, want the 0th dict in address
                recursion = recursion - 1
                if debug: print "Recursion return, level: %s, adding %s back to coders" % (recursion, coder)
            else:
                #If we have error result and no coders left then add address to missing
                missed = [address]
        else:
            if location <> None:
                # Non-empty location ==> geocode success, add long & lat
                coders_used[address['Site']].append({coder: 'success'})
                if debug: print '(%s,%s) with %s' % ( location.longitude, location.latitude, coder)
                address['longitude'], address['latitude']  =  \
                             location.longitude, location.latitude
                address['geocoder'] = coder
                geo_address.append(address)
            else:
                # Otherwise we have empty result
                if debug: print "Null result ... failed with %s" % ( coder)
                coders_used[address['Site']].append({ coder: 'None'})
                # new_coders is coders with the current coder removed
                new_coders = list(coders)
                new_coders.remove(coder)
                # Try with a different coder if coder list isn't empty
                if len(new_coders) > 0 :
                    recursion = recursion + 1
                    if debug: print "Recursive call %s, removing %s from coders" % (recursion, coder)
                    #NB recursive call using a LIST of 1 element
                    # does NOT ==> recursion will never go more than 2 calls deep!!
                    geo_address, missed=add_longitude_and_latitude([address], new_coders)
                    recursion = recursion - 1
                    if debug: print "Recursion return, level: %s, adding %s back to coders" % (recursion, coder)
                else:
                    # no coders left,  add to missing
                    missed = [address]

        if len(geo_address)>0:
            new_addresses.extend(geo_address)
        if len(missed)>0:
            not_geocoded.extend(missed)

    print
    return new_addresses, not_geocoded


def add_what3words(addresses):
    '''
    Addess a what3words field to a list of dicts_of_addresses
    '''
    w3w_key='LBZKVJ7I'

    locator= geopy.What3Words(w3w_key)

    for address in addresses:
        x, y = address['latitude'], address['longitude']
        w3w = locator.reverse([x,y], lang='EN')
        address['what3words']=w3w.address

    return


def create_kml(addresses, filename):
    '''
    Saves a simple kml file called filename.kml using addreses as points
    '''

    kml = simplekml.Kml()

    for address in addresses:
        latitude, longitude = address['latitude'], address['longitude']
        name, description = address['Site'], address['geocoder']
        print "Adding %s @ [%s,%s] geocoders %s" % (name, latitude, longitude, description)
        pnt = kml.newpoint (name=name, coords=[(longitude, latitude)])
        pnt.description = description

    kml.save(filename + '.kml')

    return


def create_kml_tour(addresses, filename):
    '''
    Creates a kml tour of the sites
    Modified from pykml example here https://pythonhosted.org/pykml/examples/tour_examples.html
    python
    Generate a KML document of a tour based on rotating around locations.
    '''
    tilt = 20
    distance = 20

    # define a variable for the Google Extensions namespace URL string
    gxns = '{' + nsmap['gx'] + '}'

    # start with a base KML tour and playlist
    tour_doc = KML.kml(
        KML.Document(
          GX.Tour(
            KML.name("Play me!"),
            GX.Playlist(),
          ),
          KML.Folder(
            KML.name('Sites'),
            id='sites',
          ),
        )
    )

    for address in addresses:
        #import ipdb; ipdb.set_trace()
        # fly to a space viewpoint
        tour_doc.Document[gxns+"Tour"].Playlist.append(
          GX.FlyTo(
            GX.duration(5),
            GX.flyToMode("smooth"),
            KML.LookAt(
              KML.longitude(address['longitude']),
              KML.latitude(address['latitude']),
              KML.altitude(0),
              KML.heading(0),
              KML.tilt(0),
              KML.range(10000000.0),
              KML.altitudeMode("relativeToGround"),
            )
          ),
        )
        # fly to the address
        tilt = tilt + 10
        distance = distance + 10
        tour_doc.Document[gxns+"Tour"].Playlist.append(
          GX.FlyTo(
            GX.duration(0.25),
            GX.flyToMode("smooth"),
            KML.LookAt(
              KML.longitude(address['longitude']),
              KML.latitude(address['latitude']),
              KML.altitude(0),
              KML.heading(0),
##              KML.tilt(address['tilt']),
##              KML.range(address['range']),
              KML.tilt(tilt),
              KML.range(distance),
              KML.altitudeMode("relativeToGround"),
            )
          ),
        )
        
        # add a placemark for the address
        tour_doc.Document.Folder.append(
          KML.Placemark(
            KML.name("?"),
            KML.description(
                "<h1>{name}</h1><br/>{desc}".format(
                        name=address['Site'],
                        desc=address['Bandwidth'],
                )
            ),
            KML.Point(
              KML.extrude(1),
              KML.altitudeMode("relativeToGround"),
              KML.coordinates("{lon},{lat},{alt}".format(
                      lon=address['longitude'],
                      lat=address['latitude'],
                      alt=50,
                  )
              )
            ),
            id=address['Site'].replace(' ','_')
          )
        )
        # show the placemark balloon
        tour_doc.Document[gxns+"Tour"].Playlist.append(
            GX.AnimatedUpdate(
              GX.duration(2.0),
              KML.Update(
                KML.targetHref(),
                KML.Change(
                  KML.Placemark(
                    KML.visibility(1),
                    GX.balloonVisibility(1),
                    targetId=address['Site'].replace(' ','_')
                  )
                )
              )
            )
        )

        tour_doc.Document[gxns+"Tour"].Playlist.append(GX.Wait(GX.duration(2.0)))

        tour_doc.Document[gxns+"Tour"].Playlist.append(
            GX.AnimatedUpdate(
              GX.duration(2.0),
              KML.Update(
                KML.targetHref(),
                KML.Change(
                  KML.Placemark(
                    GX.balloonVisibility(0),
                    targetId=address['Site'].replace(' ','_')
                  )
                )
              )
            )
        )
        
        
        # spin around the address
        for aspect in range(0,360,10):

            tour_doc.Document[gxns+"Tour"].Playlist.append(
                GX.FlyTo(
                    GX.duration(0.25),
                    GX.flyToMode("smooth"),
                        KML.LookAt(
                              KML.longitude(address['longitude']),
                              KML.latitude(address['latitude']),
                              KML.altitude(0),
                              KML.heading(aspect),
                              KML.tilt(tilt),
                              KML.range(distance),
                              KML.altitudeMode("relativeToGround"),
                        )
                    )
            )

        for angle in range(0,360,10):
            tour_doc.Document[gxns+"Tour"].Playlist.append(
              GX.FlyTo(
                GX.duration(0.25),
                GX.flyToMode("smooth"),
                KML.LookAt(
                  KML.longitude(address['longitude']),
                  KML.latitude(address['latitude']),
                  KML.altitude(0),
                  KML.heading(angle),
##                  KML.tilt(address['tilt']),
##                  KML.range(address['range']),
                  KML.tilt(tilt),
                  KML.range(distance),
                  KML.altitudeMode("relativeToGround"),
                )
              )
            )

        tour_doc.Document[gxns+"Tour"].Playlist.append(GX.Wait(GX.duration(1.0)))

    #    tour_doc.Document[gxns+"Tour"].Playlist.append(
    #        GX.TourControl(GX.playMode("pause"))
    #    )

        # fly to a space viewpoint
        tour_doc.Document[gxns+"Tour"].Playlist.append(
          GX.FlyTo(
            GX.duration(5),
            GX.flyToMode("bounce"),
            KML.LookAt(
              KML.longitude(address['longitude']),
              KML.latitude(address['latitude']),
              KML.altitude(0),
              KML.heading(0),
              KML.tilt(0),
              KML.range(10000000.0),
              KML.altitudeMode("relativeToGround"),
            )
          ),
        )

    # check that the KML document is valid using the Google Extension XML Schema
    #assert(Schema("kml22gx.xsd").validate(tour_doc))
    #always bombs
#    print etree.tostring(tour_doc, pretty_print=True)

    # output a KML file (named based on the Python script)
    outfile = kmlfile + '_tour.kml'
    with open(outfile,'w') as file:
        file.write(etree.tostring(tour_doc, pretty_print=True))

    return

def draw_map(points):
    '''Use Basemap to paint points on a map
    '''

    # Basic map details
    bm = Basemap(llcrnrlon=-20,llcrnrlat=33,urcrnrlon=35,urcrnrlat=70, \
                        projection='cyl', lon_0= 0,lat_0=10,resolution='i')
#    bm = Basemap(llcrnrlon=-10.5,llcrnrlat=49.5,urcrnrlon=3.5,urcrnrlat=59.5,
#            resolution='i',projection='tmerc',lon_0=-4.36,lat_0=54.7)

    #Fill the globe with a blue color
    bm.drawmapboundary(fill_color='aqua')
    #Fill the continents with the land color
    bm.fillcontinents(color='coral',lake_color='aqua', zorder=0)
    # draw coastlines & countries
    bm.drawcoastlines()
    bm.drawcountries()

    # Convert lat & lon
    lons = [ float(p['longitude']) for p in points]
    lats = [ float(p['latitude']) for p in points]
#    bw = [int((p['Bandwidth']).replace('Mb','')) for p in points]
    x,y = bm(lons, lats)
    # plot points using bw as scale
    plt.scatter(x, y, s=15, alpha = 1, zorder=10)

    plt.show()
    plt.savefig('fig1.png', dpi = 100)

    return

def main():
   
    os.chdir(WD)

    parser = argparse.ArgumentParser()
    #parser.add_argument("--output", help = "output file")
    parser.add_argument('file', type=str,  help = "Excel file with addresses to be geocoded", nargs='?', default =default_xls)
#    parser.add_argument('-g', '--grab', nargs = '?', const = 1, type = str, default = 'Y')
    args = parser.parse_args()
    xls_input =args.file
    xls_dir = os.path.dirname(xls)
    xls_basename=os.path.basename(xls)
    xls_basename, xls_extension=os.path.splitext(xls_input)
    new_xls =xls_basename+'_geocoded_'+xls_extension
    uncoded_xls =xls_basename+'_uncoded_'+xls_extension
    tabName = 'Sites'
    tabName = 'New'
    newTab = 'geocoded'
    kmlfile= 'kmlfile'


    # Add longitude & latitude    
    if run_geocoders:
        #read in site list
        sites = xls_to_list_of_dicts(xls_input, tabName )
    
        #populate list of coders_used
        for address in sites:
            coders_used[address['Site']] = []

        sites_coded, sites_uncoded = add_longitude_and_latitude(sites, geocoders)
        if debug: print "Finished coding sites"
       # Save co-ords with data in xls, list of uncoded sites if there are any & coders used (TODO)
        list_of_dicts_to_xls( new_xls, sites_coded, newTab)
        if len(sites_uncoded) > 0:
                list_of_dicts_to_xls( uncoded_xls, sites_uncoded, tabName)
    #    list_of_dicts_to_xls( 'coders.xls', coders_used, None)
        if debug: print "Saved excels"
    else:
        print 'Skipping geocoding'      
        # Load previously geocoded addresses into sites_coded so we have some data
        sites_coded = xls_to_list_of_dicts(new_xls, newTab )

    # Add reverse info from what3words
#    add_what3words(sites_coded)
 #   if debug: print "Finished adding what3words"

    #Save simple kml with all the sites
    create_kml(sites_coded, kmlfile)
    if debug: print "Finished writing simple kml file"

    #Save kml tour with all the sites
    create_kml_tour(sites_coded, kmlfile)
    if debug: print "Finished writing kml tour file"

    # Draw the basemap
    draw_map(sites_coded)
    if debug: print "Finished drawing map"

    return


if __name__ == '__main__':
    main()
