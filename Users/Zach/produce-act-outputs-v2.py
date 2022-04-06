import geopandas as gpd
import numpy as np
import pandas as pd
import boto.s3

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


def addGeometryIdToDataFrame(df, gdf, xcol, ycol, idColumn="geometry", df_geom='epsg:4326'):
    gdf_data = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[xcol], df[ycol]))
    gdf_data.set_crs(df_geom)
    joined = gpd.sjoin(gdf_data.to_crs('epsg:26910'), gdf.to_crs('epsg:26910'))
    gdf_data = gdf_data.merge(joined['blkgrpid'], left_index=True, right_index=True, how="left")
    gdf_data.rename(columns={'blkgrpid': idColumn}, inplace=True)
    df = pd.DataFrame(gdf_data.drop(columns='geometry'))
    df.drop(columns=[xcol, ycol], inplace=True)
    return df.loc[~df.index.duplicated(keep='first'), :]


def ridersToList(val):
    if str(val) == 'nan':
        return []
    else:
        return str(val).split(':')


def processEvents(directory):
    fullPath = directory + 'ITERS/it.0/0.events.csv.gz'
    PTs = []
    PEVs = []
    PLVs = []
    print('Reading ', fullPath)
    for chunk in pd.read_csv("s3://beam-outputs/" + fullPath, chunksize=2500000):
        if sum((chunk['type'] == 'PathTraversal')) > 0:
            chunk['vehicle'] = chunk['vehicle'].astype(str)
            PT = chunk.loc[(chunk['type'] == 'PathTraversal') & (chunk['length'] > 0)].dropna(how='all', axis=1)
            PT['departureTime'] = PT['departureTime'].astype(int)
            PT['arrivalTime'] = PT['arrivalTime'].astype(int)
            if 'riders' in PT.columns:
                PT['riders'] = PT.riders.apply(ridersToList)
            else:
                PT['riders'] = [[]] * len(PT)
            PTs.append(PT[['driver', 'vehicle', 'mode', 'length', 'startX', 'startY', 'endX', 'endY', 'vehicleType',
                           'arrivalTime', 'departureTime', 'primaryFuel', 'primaryFuelType', 'secondaryFuel',
                           'secondaryFuelType', 'numPassengers', 'riders']])
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


def createLabeledNetwork(directory, gdf):
    fullPath = 's3://beam-outputs/' + directory + 'network.csv.gz'
    network = pd.read_csv(fullPath)[['linkId', 'fromLocationX', 'fromLocationY']]
    network = gpd.GeoDataFrame(network, geometry=gpd.points_from_xy(network.fromLocationX, network.fromLocationY))
    network.crs = 'epsg:26910'
    joined = gpd.sjoin(network, gdf[['geometry', 'blkgrpid']].to_crs('epsg:26910'))
    network = pd.DataFrame(joined.drop(columns=['geometry', 'index_right'])).rename(columns={'blkgrpid': 'blockGroup'})
    return network


def labelTrips(trips, labeledNetwork):
    labeledTrips = trips.merge(labeledNetwork, left_on='legRouteStartLink', right_on='linkId', how='left')
    labeledTrips.drop(columns=['linkId', 'fromLocationX', 'fromLocationY'], inplace=True)
    labeledTrips.rename(columns={'blockGroup': 'startBlockGroup'}, inplace=True)
    labeledTrips = labeledTrips.merge(labeledNetwork, left_on='legRouteEndLink', right_on='linkId', how='left')
    labeledTrips.drop(columns=['linkId', 'fromLocationX', 'fromLocationY'], inplace=True)
    labeledTrips.rename(columns={'blockGroup': 'endBlockGroup'}, inplace=True)
    return labeledTrips

def addTimesToPlans(plans):
    legInds = np.where(plans['ActivityElement'].str.lower() == "leg")[0]
    plans.loc[:, 'legDepartureTime'] = np.nan
    plans.iloc[legInds, plans.columns.get_loc('legDepartureTime')] = plans['departure_time'].iloc[legInds - 1].copy()
    plans.loc[:, 'originX'] = np.nan
    plans.iloc[legInds, plans.columns.get_loc('originX')] = plans['x'].iloc[legInds - 1].copy()
    plans.loc[:, 'originY'] = np.nan
    plans.iloc[legInds, plans.columns.get_loc('originY')] = plans['y'].iloc[legInds - 1].copy()
    plans.loc[:, 'destinationX'] = np.nan
    plans.iloc[legInds, plans.columns.get_loc('destinationX')] = plans['x'].iloc[legInds + 1].copy()
    plans.loc[:, 'destinationY'] = np.nan
    plans.iloc[legInds, plans.columns.get_loc('destinationY')] = plans['y'].iloc[legInds + 1].copy()
    return plans

def processPlans(directory):
    fullPath = directory + 'plans.csv.gz'
    trips = []
    activities = []
    personToTripDeparture = {}
    print(fullPath)
    df = pd.read_csv("s3://beam-outputs/" + fullPath)
    df = addTimesToPlans(df)
    legs = df.loc[(df['ActivityElement'].str.lower().str.contains('leg'))].dropna(how='all', axis=1)
    legsSub = legs[['person_id', 'legDepartureTime',  'PlanElementIndex', 'originX', 'originY', 'destinationX', 'destinationY']]
    for rowID, val in legsSub.iterrows():
        personToTripDeparture.setdefault(val.person_id, []).append(
            {"planID": val.PlanElementIndex, "departureTime": val.legDepartureTime * 3600.0})
    trips.append(legsSub)
    acts = df.loc[(df['ActivityElement'].str.lower().str.contains('activity'))].dropna(how='all', axis=1)

    actsSub = acts[['person_id', 'ActivityType', 'x', 'y', 'departure_time']]
    activities.append(actsSub)
    return pd.concat(trips), pd.concat(activities), personToTripDeparture


def personToPathTraversal(PTs, PEVs, PLVs, personToTripDeparture):
    vehicleToPT = PTs.groupby('vehicle').apply(lambda x: list(x.index)).apply(
        lambda x: {y: [] for y in x}).to_dict()

    PEVlookup = PEVs[['person', 'vehicle', 'time']].value_counts().to_dict()
    PLVlookup = PLVs.groupby(['person', 'vehicle']).apply(lambda x: list(x.time)).to_dict()
    # personToPT = PEVs['person'].value_counts().apply(lambda x: []).to_dict()

    for key, counts in PEVlookup.items():
        person = key[0]
        vehicle = key[1]
        departureTime = key[2]
        if vehicle in vehicleToPT:
            legs = vehicleToPT[vehicle]
            if (person, vehicle) in PLVlookup:
                if person in personToTripDeparture:
                    planTrips = personToTripDeparture[person]
                    tripsLeavingBeforeDeparture = [-1] + [t['planID'] for t in planTrips if
                                                          t['departureTime'] <= (departureTime + 1800)]
                else:
                    tripsLeavingBeforeDeparture = [-1]
                endTimes = PLVlookup[(person, vehicle)]
                plvsAfterDeparture = [t for t in endTimes if t > departureTime]

                if len(plvsAfterDeparture) > 0:
                    firstPLVafterDeparture = plvsAfterDeparture[0]
                    lastTripBeforeDeparture = tripsLeavingBeforeDeparture[-1]
                    if lastTripBeforeDeparture == -1:
                        print('hmm')
                    for leg in legs.keys():
                        ptDepartureTime = PTs.at[leg, 'departureTime']
                        if (ptDepartureTime >= departureTime) & (ptDepartureTime < firstPLVafterDeparture):
                            legs[leg].append((person, lastTripBeforeDeparture))
                            # personToPT[person].append(leg)
                # else:
                #     for leg in legs.keys():
                #         ptDepartureTime = PTs.at[leg, 'departureTime']
                #         if ptDepartureTime >= departureTime:
                #             legs[leg].append(person)
                            # # personToPT[person].append(leg)
            else:
                for leg in legs.keys():
                    ptDepartureTime = PTs.at[leg, 'departureTime']
                    if person in personToTripDeparture:
                        planTrips = personToTripDeparture[person]
                        tripsLeavingBeforeDeparture = [-1] + [t['planID'] for t in planTrips if
                                                              t['departureTime'] <= (departureTime + 1800)]
                    else:
                        tripsLeavingBeforeDeparture = [-1]
                    lastTripBeforeDeparture = tripsLeavingBeforeDeparture[-1]
                    if lastTripBeforeDeparture == -1:
                        print('hmm')
                    if ptDepartureTime >= departureTime:
                        legs[leg].append((person, lastTripBeforeDeparture))
                        # personToPT[person].append(leg)
        # else:
        #     print("no legs for ", vehicle)

    vehiclePathPassengerList = [(veh, pathTraversalID, passenger, planIndex) for veh, vehicleLegs in
                                vehicleToPT.items() for pathTraversalID, passengers in vehicleLegs.items() for
                                (passenger, planIndex) in passengers if len(passengers) > 0]
    vehiclePathPassenger = pd.MultiIndex.from_tuples(vehiclePathPassengerList,
                                                     name=['vehicleID', 'pathTraversalID', 'personID',
                                                           'planIndex']).to_frame()

    return vehiclePathPassenger


def collectAllData(inDirectory, outDirectory, popDirectory):
    trips, activities, personToTripDeparture = processPlans(popDirectory)

    PTs, PEVs, PLVs = processEvents(inDirectory)

    BGs = gpd.read_file('scenario/sfbay-blockgroups-2010/641aa0d4-ce5b-4a81-9c30-8790c4ab8cfb202047-1-wkkklf.j5ouj.shp')
    print("Adding blockgroups to trip origins")
    trips = addGeometryIdToDataFrame(trips, BGs, 'originX', 'originY', 'startBlockGroup')
    print("Adding blockgroups to trip destinations")
    trips = addGeometryIdToDataFrame(trips, BGs, 'destinationX', 'destinationY', 'endBlockGroup')
    print("Adding blockgroups to activities")
    activities = addGeometryIdToDataFrame(activities, BGs, 'x', 'y', 'activityBlockGroup')
    print("Adding blockgroups to path traversal origins")
    PTs = addGeometryIdToDataFrame(PTs, BGs, 'startX', 'startY', 'startBlockGroup')
    print("Adding blockgroups to path traversal destinations")
    PTs = addGeometryIdToDataFrame(PTs, BGs, 'endX', 'endY', 'endBlockGroup')
    PTs.index.set_names('PathTraversalID', inplace=True)
    print("Writing trips to ", outDirectory + 'trips.csv.gz')
    trips.to_csv(outDirectory + 'trips.csv.gz', index=True)
    PTs.to_csv(outDirectory + 'pathTraversals.csv.gz', index=True)
    activities.to_csv(outDirectory + 'activities.csv.gz', index=True)


if __name__ == '__main__':
    # directory = 'https://beam-outputs.s3.amazonaws.com/pilates-outputs/15thSep2019/c_ht/beam/sfbay-smart-c-ht' \
    #             '-pilates__2019-09-13_18-00-40/ITERS/it.15/15.'

    conn = boto.s3.connect_to_region('us-east-2')
    bucket = conn.get_bucket('beam-outputs')
    allRuns = ["sfbay-2018-base-20220327",
               "sfbay-RH_fleetsz_0.25-20220329",
               "sfbay-RH_fleetsz_0.5-20220329",
               "sfbay-RH_fleetsz_0.67-20220328-failed",
               "sfbay-RH_fleetsz_1.5-20220328",
               "sfbay-RH_fleetsz_1.75-20220329",
               "sfbay-transit_capacity_0.5-20220329",
               "sfbay-transit_frequencies_0.5-20220228",
               "sfbay-transit_frequencies_1.5-20220228",
               "sfbay-transit_frequencies_2.0-20220229",
               "sfbay-transit_speed_1.5-20220228"]
    for runName in allRuns:
        folders = bucket.list("pilates-outputs/" + runName + "/beam/", "/")
        allBeamOutputs = [folder.name for folder in folders if ('year' in folder.name) & ('final' not in folder.name)]
        yearToMaxIter = dict()
        for dir in allBeamOutputs:
            yr = dir.split('-')[-3]
            it = int(dir.split('-')[-1][:-1])
            if yr in yearToMaxIter:
                if it > yearToMaxIter[yr][0]:
                    yearToMaxIter[yr] = (it, dir)
            else:
                yearToMaxIter[yr] = (it, dir)
        for yr, (_, inDirectory) in yearToMaxIter.items():
            popDirectory = inDirectory.replace("/beam/", "/activitysim/")
            outDirectory = "s3://beam-outputs/" + "-".join(inDirectory.split("-")[:-2]) + "-final/"
            collectAllData(inDirectory, outDirectory, popDirectory)

    print('done')
