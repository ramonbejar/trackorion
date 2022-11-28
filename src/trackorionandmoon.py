# Plot trajectory from NASA/ESA Orion-1 spacecraft
#

import sys
import math
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from astropy.coordinates import get_body_barycentric, get_body, get_moon, CartesianRepresentation
from astropy.time import Time
from astroquery.jplhorizons import Horizons


# Time format in EPH for Horizons queries:
#
# Use utc time format :  y-m-d h:m:s utc
# body names: 'orion' 'moon'
def loadTrajectoryFromJPLHorizons(bodyname,sdate,edate,step = '15m'):
    body = Horizons(id=bodyname, epochs = { 'start' : sdate, 'stop' : edate, 'step': '15m' }, location='500' )
    print(body)
    bvectors = body.vectors(refplane='earth')
    bvectors['x'].convert_unit_to('km')
    bvectors['y'].convert_unit_to('km')
    bvectors['z'].convert_unit_to('km')
    bvectors['vx'].convert_unit_to('km/h')
    bvectors['vy'].convert_unit_to('km/h')
    bvectors['vz'].convert_unit_to('km/h')


    bvectorsx = bvectors['x'].quantity
    bvectorsy = bvectors['y'].quantity
    bvectorsz = bvectors['z'].quantity
    bvectorsvx = bvectors['vx'].quantity
    bvectorsvy = bvectors['vy'].quantity
    bvectorsvz = bvectors['vz'].quantity
    bdates = bvectors['datetime_jd'].quantity
    size = len(bvectorsx)

    dates = []
    trajectoryX = []
    trajectoryY = []
    trajectoryZ = []
    velocity = []
    for i in range(size):
    # convert km to miles
       trajectoryX.append(bvectorsx[i].value * 0.621371192)
       trajectoryY.append(bvectorsy[i].value * 0.621371192 )
       trajectoryZ.append(bvectorsz[i].value * 0.621371192 )
       velocity.append( (bvectorsvx[i].value* 0.621371192,bvectorsvy[i].value * 0.621371192,bvectorsvz[i].value *0.621371192) )
       dates.append( Time( bdates[i].value, format='jd' ) )
    return dates,trajectoryX,trajectoryY,trajectoryZ,velocity


def plot3DSeries( trajdataX, trajdataY, trajdataZ, veldata, stopindextime, bodyname, color, msize, pfig = None, pax = None, lastplot=True ):
   print(" total length: ",len(trajdataX), "stop at: ", stopindextime)
   print(" Position of ", bodyname," at stoptime: ", trajdataX[stopindextime-1], trajdataY[stopindextime-1], trajdataZ[stopindextime-1])
   print( "Distance to earth: ", math.sqrt( trajdataX[stopindextime-1]**2.0 + trajdataY[stopindextime-1]**2.0 +  trajdataZ[stopindextime-1]**2.0  ))
   if (pfig == None):
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
   else:
     fig = pfig
     ax = pax
   if (stopindextime == 1):
     ax.scatter( trajdataX[0], trajdataY[0], trajdataZ[0], color, s=msize )
   else:
     ax.plot( trajdataX[:stopindextime], trajdataY[:stopindextime], trajdataZ[:stopindextime], color, markersize=msize )
   if (lastplot):
      plt.show()
   return fig,ax

def findStopTime( dates, stoptime ):
    for i in range(len(dates)):
        if stoptime <= dates[i]:
            return i-1
    return i


def main_dataEPHNasa( filenames ):
    WholetrajX = []
    WholetrajY = []
    WholetrajZ = []
    Wholevel = []
    Wholedates = []
    utcnow = datetime.datetime.now(datetime.timezone.utc)
    print( "UTC time now: ",utcnow)
    stoptime = time.strptime( "2022-11-21T09:12:0", "%Y-%m-%dT%H:%M:%S" )
    t =  Time("2022-11-21 10:00", scale='utc')
    pos = get_body_barycentric('moon', t)
    print (" Moon pos in AU", pos)
    for fname in filenames:
      dates, trajectoryX, trajectoryY, trajectoryZ, velocity = loadTrajectory(fname)
      WholetrajX = WholetrajX + trajectoryX
      WholetrajY = WholetrajY + trajectoryY
      WholetrajZ = WholetrajZ + trajectoryZ
      Wholevel = Wholevel + velocity
      Wholedates = Wholedates + dates
    stopindex = findStopTime( Wholedates, stoptime )
    plot3DSeries( WholetrajX,  WholetrajY,  WholetrajZ, Wholevel, stopindex )

def main_datafromHorizons( sdate, edate ):
    WholetrajX = []
    WholetrajY = []
    WholetrajZ = []
    Wholevel = []
    Wholedates = []
    utcnow = datetime.datetime.now(datetime.timezone.utc)
    print( "UTC time now: ",utcnow)
    lasttime =  Time( edate, scale='utc')
    pos = get_body_barycentric('moon', lasttime)
    print (" Moon pos in AU", pos)

    fig,ax = plot3DSeries( [0], [0], [0], [(0,0,0)], 1, "Earth", "black", 200, None, None, False )
    dates,trajectoryX,trajectoryY,trajectoryZ,velocity = loadTrajectoryFromJPLHorizons("Orion",sdate,edate,step = '15m')
    stopindex = findStopTime( dates, lasttime )
    fig,ax = plot3DSeries( trajectoryX, trajectoryY, trajectoryZ, velocity, stopindex, "Orion", "blue", 1, fig, ax, False )

    dates,trajectoryX,trajectoryY,trajectoryZ,velocity = loadTrajectoryFromJPLHorizons("301",sdate,edate,step = '15m')
    fig,ax = plot3DSeries( trajectoryX, trajectoryY, trajectoryZ, velocity, stopindex, "Moon", "gray", 1, fig, ax, True )



if __name__ == '__main__':

   main_datafromHorizons( sys.argv[1]+' '+sys.argv[2], sys.argv[3]+' '+sys.argv[4] )
