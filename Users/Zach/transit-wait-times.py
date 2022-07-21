#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 08:31:26 2022

@author: zaneedell
"""
import pandas as pd


#%%

def fixPathTraversals(PTs):
    PTs['duration'] = PTs['arrivalTime'] - PTs['departureTime']
    PTs['mode_extended'] = PTs['mode']
    PTs['isRH'] = PTs['vehicle'].str.contains('rideHail')
    PTs['isCAV'] = PTs['vehicleType'].str.contains('L5')
    PTs.loc[PTs['isRH'], 'mode_extended'] += '_RideHail'
    PTs.loc[PTs['isCAV'], 'mode_extended'] += '_CAV'
    PTs['occupancy'] = PTs['numPassengers']
    PTs.loc[PTs['mode_extended'] == 'car', 'occupancy'] += 1
    PTs.loc[PTs['mode_extended'] == 'walk', 'occupancy'] = 1
    PTs.loc[PTs['mode_extended'] == 'bike', 'occupancy'] = 1
    PTs['vehicleMiles'] = PTs['length'] / 1609.34
    PTs['passengerMiles'] = (PTs['length'] * PTs['occupancy']) / 1609.34
    PTs['totalEnergyInJoules'] = PTs['primaryFuel'] + PTs['secondaryFuel']
    PTs['gallonsGasoline'] = 0
    PTs.loc[PTs['primaryFuelType'] == 'gasoline',
            'gallonsGasoline'] += PTs.loc[PTs['primaryFuelType'] == 'gasoline', 'primaryFuel'] * 8.3141841e-9
    PTs.loc[PTs['secondaryFuelType'] == 'gasoline',
            'gallonsGasoline'] += PTs.loc[PTs['secondaryFuelType'] == 'gasoline', 'secondaryFuel'] * 8.3141841e-9
    PTs.drop(columns=['numPassengers', 'length'], inplace=True)
    return PTs

def ridersToList(val):
    if str(val) == 'nan':
        return []
    else:
        return str(val).split(':')

def processEvents(directory, filename='events.csv.gz'):
    fullPath = directory + filename
    PTs = []
    PEVs = []
    PLVs = []
    print('Reading ', fullPath)
    for chunk in pd.read_csv(fullPath, chunksize=1000000):
        if sum((chunk['type'] == 'PathTraversal')) > 0:
            chunk['vehicle'] = chunk['vehicle'].astype(str)
            PT = chunk.loc[(chunk['type'] == 'PathTraversal') & (chunk['length'] > 0)].dropna(how='all', axis=1)
            PT['departureTime'] = PT['departureTime'].astype(int)
            PT['arrivalTime'] = PT['arrivalTime'].astype(int)
            # if 'riders' in PT.columns:
            #     PT['riders'] = PT.riders.apply(ridersToList)
            # else:
            #     PT['riders'] = [[]] * len(PT)
            PTs.append(PT[['driver', 'vehicle', 'mode', 'length', 'startX', 'startY', 'endX', 'endY', 'vehicleType',
                           'arrivalTime', 'departureTime', 'primaryFuel', 'primaryFuelType', 'secondaryFuel',
                           'secondaryFuelType', 'numPassengers']])
            PEV = chunk.loc[(chunk.type == "PersonEntersVehicle") &
                            ~(chunk['person'].apply(str).str.contains('Agent').fillna(False)) &
                            ~(chunk['vehicle'].str.contains('body').fillna(False)), :].dropna(how='all', axis=1)
            if ~PEV.empty:
                PEV['person'] = PEV['person'].astype(int)
                PEV['time'] = PEV['time'].astype(int)
                PEVs.append(PEV)

            PLV = chunk.loc[(chunk.type == "PersonLeavesVehicle") &
                            ~(chunk['person'].apply(str).str.contains('Agent').fillna(False)) &
                            ~(chunk['vehicle'].str.contains('body').fillna(False)), :].dropna(how='all', axis=1)
            if ~PLV.empty:
                PLV['person'] = PLV['person'].astype(int)
                PLV['time'] = PLV['time'].astype(int)
                PLVs.append(PLV)
    PTs = fixPathTraversals(pd.concat(PTs))
    return PTs, pd.concat(PEVs), pd.concat(PLVs)
#%%


skHalf = pd.read_csv('scenario/transit-headway/2.activitySimODSkims_current.less.csv.gz')
skNormal = pd.read_csv('scenario/transit-headway/2.activitySimODSkims_current.normal.csv.gz')
skSmall = pd.read_csv('scenario/transit-headway/0.activitySimODSkims_current.small.csv.gz')
#%%
PThalf, PEVhalf, PLVhalf = processEvents('scenario/transit-headway/','2.events.less.csv.gz')
PTdouble, PEVdouble, PLVdouble = processEvents('scenario/transit-headway/','2.events.normal.csv.gz')


#%%
pHalf = pd.read_csv('scenario/transit-headway/plans-lesstransit.csv.gz')
pBase = pd.read_csv('scenario/transit-headway/plans-base.csv.gz')


#%%

tazSf = pd.read_csv('/Users/zaneedell/Desktop/git/beam-data-sfbay/taz-centers.csv')
timePeriods = ['EV','EA','AM','MD','PM']
reservationTypes = ['Solo','Pooled']
out = {}

for taz in tazSf.taz:
    for tp in timePeriods:
        for reservationType in reservationTypes:
            out[(taz, tp, reservationType)] = pd.Series({"waitTimeInMinutes":6.0, "costPerMile":2.0,"unmatchedRequestPortion":0.1,"observations":0})

pd.concat(out, names=('origin','timePeriod','reservationType')).unstack().to_csv('scenario/ridehail/as-origin-skims-sf-taz.csv.gz', compression='gzip')
"""     aggregatedInput = {
        "origin": str,
        "timePeriod": str,
        "reservationType": str,sw
        "waitTimeInMinutes": float,
        "costPerMile": float,
        "unmatchedRequestPortion": float,
        "observations": int
    }
"""

tazAustin = pd.read_csv('/Users/zaneedell/Desktop/git/beam-data-austin/blockgroup-centers.csv.gz')
timePeriods = ['EV','EA','AM','MD','PM']
reservationTypes = ['Solo','Pooled']
out = {}

for taz in tazAustin.taz:
    for tp in timePeriods:
        for reservationType in reservationTypes:
            out[(taz, tp, reservationType)] = pd.Series({"waitTimeInMinutes":6.0, "costPerMile":2.0,"unmatchedRequestPortion":0.1,"observations":0})

pd.concat(out, names=('origin','timePeriod','reservationType')).unstack().to_csv('scenario/ridehail/as-origin-skims-austin-bg.csv.gz', compression='gzip')

