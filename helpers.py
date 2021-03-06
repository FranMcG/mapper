# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 11:32:13 2015
Name: Helpers
Description: Some helper modules, not part of main solution so lumped here as
            a means of keeping them out of main code


@author: fran
"""
import os
import time
import pywinauto
from xlrd import open_workbook
from xlwt import Workbook
# How hacky is this ?!?!?
# Module has different name in Python3 vs Python2!
# Try the python 3 module & fallback to python2
try:
    from configparser import ConfigParser as ConfigParser
except ImportError:
    from ConfigParser import ConfigParser as ConfigParser

debug=False
#debug=True

#last record to read from xls defining channel attributes
last_row=110

#xls = r'C:\Users\fran\Downloads\150325 SID LCN Stream.xlsx'
##xls = r'C:\Documents and Settings\xmltv\Parser\channels.xlsx'
##xls = r'C:\Users\Public\xmltv\channels.xlsx'


def xls_to_list_of_dicts(fileName, sheetName):
    """
    Simple wrapper to write list of dictionaries to xls
    """

    with open_workbook(fileName) as wb:
        #worksheet = wb.sheet_by_index(0)
        worksheet = wb.sheet_by_name(sheetName)
        # getting number or rows and setting current row as 0 -e.g first
        num_rows, curr_row = worksheet.nrows - 1, 0
        # retrieving keys values(first row values)
        keyValues = [x.value for x in worksheet.row(0)]
        # building dict
        data = []
        # iterating through all rows and filling with our dictionaries
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
        return data

def list_of_dicts_to_xls(fileName, datalist, sheetName):
    """
    Simple wrapper for xld to read excel file in as list of dictionaries
    """
    w = Workbook()
    # Add next "sheet x" if sheetName is None
    if sheetName == None:
        ws = w.add_sheet('sheet1')
    else:
        ws = w.add_sheet(sheetName)

    #find index longest list - this has the most keys/headers
    # making sure that's the number that will get created!
    # get length of longest element
    x = max([ len(x) for x in datalist])
    # get index of first element that long
    idx = [ datalist.index(p) for p in datalist if len(p)== x][0]
    #### TODO find location of longest list
    # get list of columns in that row
    columns = list(datalist[idx].keys())
    for colIdx, header in enumerate(datalist[idx]):
        # Use dictionary keys as first row values(e.g. headers)
        ws.write(0, colIdx, header)

        for rowIdx,itemvalue in enumerate(datalist):
            try:
                ws.write(rowIdx + 1, colIdx, itemvalue[header])
            except KeyError as e:
                pass
    w.save(fileName)
    print "xls written"
    return


def treeview_add_child(  ctrl, node, opt ):
    """
    Add a child to the tree @ node
    NB assumes pwa_app is a pywinauto app handle/ref
    """
    print "Creating  Newchild in %s "  % str(node)
    #Make sure the window is active everytime
    window.SetFocus()
    ctrl.Scroll( 'Up', "page")
    ctrl.Select( node )
    #ctrl.GetItem( node ).Click()
    ctrl.GetItem( node ).Click(button='Right')
    time.sleep(2)
    pwa_app.PopupMenu.MenuItem(opt).Click()
    print "pop"

    return


def read_config(config_file):
    """
    Read values from ini style config file
    & return to caller.

    """
    Config  =  ConfigParser()
    #Config.optionxform  = str
    try:
        Config.read(config_file)
    except Exception as e:
        message  =  "failed to read Parser config file!"
        return e, message

    configs  =  {}
    #loop thru each sectiom
    for section in Config.sections():
        if debug: print ( section )
        dict1  =  {}
        options  =  Config.options(section)

        #Loop thru the options in the current section
        for option in options:
            try:
                dict1[option]  =   Config.get(section,
                                        option)
                if dict1[option]  == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option]  =  None

        configs[section.lower()]  =  dict1
        if debug: print ( configs[section.lower()] )

    return configs