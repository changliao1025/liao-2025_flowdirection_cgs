import sys
import numpy as np
from osgeo import ogr, osr, gdal
from datetime import datetime
import glob
import json

import netCDF4 as nc
import matplotlib as mpl
from pyearth.system.define_global_variables import *

from pyearth.toolbox.reader.text_reader_string import text_reader_string
from pyearth.gis.location.get_geometry_coordinates import get_geometry_coordinates
from pyearth.gis.geometry.calculate_distance_based_on_longitude_latitude import calculate_distance_based_on_longitude_latitude


sPath_project = '/qfs/people/liao313/workspace/python/liao-2025_flowdirection_cgs/'
#add the project path of the pythonpath
sys.path.append(sPath_project)
from codes.shared.ladder_plot_xy_data import ladder_plot_xy_data

#use a global mesh id to find all downstream cells

#should i use the json or geojson file? json is better because it has cell id
lCellID_head = 44348

aX_all = list()
aY_all = list()
for iCase in range(1, 5):
    if iCase  == 4: #special case for dggrid
        lCellID_head = 325542   #36345
        sCase= '{:03d}'.format(iCase-1)
        sFilename_watershed_json = '/compyfs/liao313/04model/pyhexwatershed/mississippi/pyhexwatershed20250101' +sCase + '/hexwatershed/00000001/watershed.json'
    else:
        lCellID_head = 44348
        sCase= '{:03d}'.format(iCase)
        sFilename_watershed_json = '/compyfs/liao313/04model/pyhexwatershed/mississippi/pyhexwatershed20250201' +sCase + '/hexwatershed/00000001/watershed.json'
    #read the json file
    aID = list()
    aLongitude = list()
    aLatitude = list()
    aCellID = list()
    aCellID_downslope = list()
    aElevation = list()
    aDrainage = list()
    aSlope = list()
    with open(sFilename_watershed_json) as json_file:
        data = json.load(json_file)
        nCell = len(data)
        lID = 1
        for i in range(nCell):
            pcell = data[i]
            aID.append(lID)
            lID = lID + 1
            #aArea.append(dArea)
            aLongitude.append(float(pcell['dLongitude_center_degree']))
            aLatitude.append(float(pcell['dLatitude_center_degree']))
            aCellID.append(int(pcell['lCellID']))
            aCellID_downslope.append(int(pcell['lCellID_downslope']))
            aElevation.append(float(pcell['dElevation']))
            dDrainage = float(pcell['dDrainage_area'])
            aDrainage.append(dDrainage)
            # qa for slope
            dSlope = float(pcell['dSlope_between'])

    iFlag_find_outlet = 0
    lCellID_current = lCellID_head
    aCellID = np.array(aCellID)
    aCellID_ladder = list()
    aCellID_ladder.append(lCellID_head)
    aCellIndex_ladder = list()

    while iFlag_find_outlet == 0:
        index = np.where(aCellID == lCellID_current)
        iIndex = np.ravel(index)[0]
        aCellIndex_ladder.append(iIndex)
        lCellID_downslope = aCellID_downslope[iIndex]
        if lCellID_downslope == -1:
            iFlag_find_outlet = 1
        else:
            aCellID_ladder.append(lCellID_downslope)
            lCellID_current = lCellID_downslope

    #calculate the distance reversely
    nCell_ladder = len(aCellID_ladder)
    aCellDistance_unstructured = np.full(nCell_ladder, np.nan)
    aDrainage_ladder = np.full(nCell_ladder, np.nan)

    aCellDistance_unstructured[nCell_ladder-1] = 0.0
    for i in range(nCell_ladder-2, -1, -1):
        index0 = aCellIndex_ladder[i]
        index1 = aCellIndex_ladder[i+1]
        dLongitude_from = aLongitude[i]
        dLatitude_from = aLatitude[i]
        dLongitude_to= aLongitude[i+1]
        dLatitude_to = aLatitude[i+1]
        distance = calculate_distance_based_on_longitude_latitude( dLongitude_from,
                                                       dLatitude_from,
                                                       dLongitude_to,
                                                       dLatitude_to)
        aCellDistance_unstructured[i] = aCellDistance_unstructured[i+1] + distance
        aDrainage_ladder[i] = aDrainage[index0]

    aX_all.append(aCellDistance_unstructured)
    aY_all.append(aDrainage_ladder)

print('ready for plot')

#aY_all_twin_in= list()
#aY_all_twin_in.append(aData_structured1)
#aY_all_twin_in.append(aData_unstructured1)
aColor = ['black','red', 'blue', 'green']
aMarker= ['s', 'h', 'o', 'd']
aSize = np.full(4, mpl.rcParams['lines.markersize'] )
aLinestyle = ['-', '--', '-.', ':']
aLinewidth = [0.25, 0.25, 0.25, 0.25]

aLabel_legend=['Elevation based, priority-flood', 'Hybrid stream burning and priority-flood',
                'Stream burning seeded priority-flood','Stream burning seeded priority-flood (uniform resolution)']

sFormat_x =  '%.1E'
sFormat_y =  '%.1E'
sLabel_x = 'Distance to outlet (m)'
sLabel_y = r'Drainage area $(m^{2})$'
sFilename_out = '/qfs/people/liao313/workspace/python/liao-2025_flowdirection_cgs/figures/ladderplot_drainage_area.png'
ladder_plot_xy_data(aX_all,  aY_all,
        sFilename_out,
        #aY_all_twin_in=aY_all_twin_in,
          #iFlag_twiny_in=1,
          #aLabel_legend_twin_in=['DRT mesh-based water depth', 'MPAS mesh-based water depth'],
           # dMax_y_twin_in=6,
        iDPI_in = None, aFlag_trend_in = None,
            iReverse_y_in = None,  iSize_x_in = None,
                    iFlag_scientific_notation_x_in=1,
                      iFlag_scientific_notation_y_in=1,
                iSize_y_in = None,  ncolumn_in = None,
                    dMax_x_in = 1.15E9,  dMin_x_in = 0,
                    dMax_y_in =3.5E12, dMin_y_in = 0,
                        dSpace_y_in = None,
                            aColor_in = aColor, aLinestyle_in = aLinestyle,
                              aLinewidth_in= aLinewidth,
                            aMarker_in = aMarker,
                            aMarker_size_in= aSize,
                                    aLocation_legend_in = [1.0,1.0],
                                        sLabel_x_in = sLabel_x,
                                        sLabel_y_in = sLabel_y,
                                            aLabel_legend_in = aLabel_legend,
        sLocation_legend_in='upper right', sFormat_x_in = sFormat_x, sFormat_y_in =sFormat_y,
        sTitle_in = None)