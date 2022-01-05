import pandas as pd


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
    gdf_data.crs = {'init': df_geom}
    joined = gpd.sjoin(gdf_data.to_crs('epsg:26910'), gdf.to_crs('epsg:26910'))
    gdf_data = gdf_data.merge(joined['blkgrpid'], left_index=True, right_index=True, how="left")
    gdf_data.rename(columns={'blkgrpid': idColumn}, inplace=True)
    df = pd.DataFrame(gdf_data.drop(columns='geometry'))
    df.drop(columns=[xcol, ycol], inplace=True)
    return df.loc[~df.index.duplicated(keep='first'), :]


def processEvents(directory):
    fullPath = directory + 'events.csv.gz'
    PTs = []
    PEVs = []
    PLVs = []
    print('Reading ', fullPath)
    for chunk in pd.read_csv(fullPath, chunksize=500000):
        if sum((chunk['type'] == 'PathTraversal')) > 0:
            chunk['vehicle'] = chunk['vehicle'].astype(str)
            PT = chunk.loc[(chunk['type'] == 'PathTraversal') & (chunk['length'] > 0)].dropna(how='all', axis=1)
            PT['departureTime'] = PT['departureTime'].astype(int)
            PT['arrivalTime'] = PT['arrivalTime'].astype(int)
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


def createLabeledNetwork(networkPath, gdf):
    network = pd.read_csv(networkPath)[['linkId', 'fromLocationX', 'fromLocationY']]
    network = gpd.GeoDataFrame(network, geometry=gpd.points_from_xy(network.fromLocationX, network.fromLocationY))
    network.crs = {'init': 'epsg:26910'}
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


def processPlans(directory):
    fullPath = directory + 'plans.csv.gz'
    trips = []
    activities = []
    personToTripDeparture = {}
    print('Reading ', fullPath)
    for chunk in pd.read_csv(fullPath, chunksize=100000):
        legs = chunk.loc[(chunk['planElementType'].str.lower().str.contains('leg')) & chunk['planSelected']].dropna(
            how='all', axis=1)
        legsSub = legs[['personId', 'legMode', 'legDepartureTime', 'legTravelTime', 'planIndex', 'planElementIndex']]
        for rowID, val in legsSub.iterrows():
            personToTripDeparture.setdefault(val.personId, []).append(
                {"planID": (val.planIndex, val.planElementIndex), "departureTime": val.legDepartureTime,
                 "travelTime": val.legTravelTime})
        trips.append(legsSub)
        acts = chunk.loc[
            (chunk['planElementType'].str.lower().str.contains('activity')) & chunk['planSelected']].dropna(how='all',
                                                                                                            axis=1)

        actsSub = acts[['personId', 'activityType', 'activityLocationX', 'activityLocationY', 'activityEndTime']]
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
                    tripsLeavingBeforeDeparture = [(-1, -1)] + [t['planID'] for t in planTrips if
                                                                t['departureTime'] <= (departureTime + 1800)]
                else:
                    tripsLeavingBeforeDeparture = [(-1, -1)]
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
                        tripsLeavingBeforeDeparture = [(-1, -1)] + [t['planID'] for t in planTrips if
                                                                    t['departureTime'] <= (departureTime + 1800)]
                    else:
                        tripsLeavingBeforeDeparture = [(-1, -1)]
                    lastTripBeforeDeparture = tripsLeavingBeforeDeparture[-1]
                    if lastTripBeforeDeparture == -1:
                        print('hmm')
                    if (ptDepartureTime >= departureTime):
                        legs[leg].append((person, lastTripBeforeDeparture))
                        # personToPT[person].append(leg)
        # else:
        #     print("no legs for ", vehicle)

    vehiclePathPassengerList = [(veh, pathTraversalID, passenger, planIndex, planElementIndex) for veh, vehicleLegs in
                                vehicleToPT.items() for pathTraversalID, passengers in vehicleLegs.items() for
                                (passenger, (planIndex, planElementIndex)) in passengers if len(passengers) > 0]
    vehiclePathPassenger = pd.MultiIndex.from_tuples(vehiclePathPassengerList,
                                                     name=['vehicleID', 'pathTraversalID', 'personID',
                                                           'planIndex', 'planElementIndex']).to_frame()

    return vehiclePathPassenger


def collectAllData(inDirectory, outDirectory, prefix):
    filePath = inDirectory + '/' + prefix + '.'

    trips, activities, personToTripDeparture = processPlans(filePath)

    PTs, PEVs, PLVs = processEvents(filePath)
    # personToPathTraversal(PTs, PEVs, PLVs, personToTripDeparture)
    vehiclePathPassenger = personToPathTraversal(PTs, PEVs, PLVs, personToTripDeparture)
    # BGs = gpd.read_file('scenario/sfbay-blockg  roups-2010.zip')

    if False:
        BGs = gpd.read_file('scenario/block_groups_austin/block_groups_austin.shp')

        network = createLabeledNetwork('data/austin.network.csv.gz', BGs)
        trips = labelTrips(trips, network)
        activities = addGeometryIdToDataFrame(activities, BGs, 'activityLocationX', 'activityLocationY',
                                              'activityBlockGroup', df_geom='epsg:26910')

        PTs = addGeometryIdToDataFrame(PTs, BGs, 'startX', 'startY', 'startBlockGroup')
        PTs = addGeometryIdToDataFrame(PTs, BGs, 'endX', 'endY', 'endBlockGroup')
        PTs.index.set_names('PathTraversalID', inplace=True)

    trips.to_csv(outDirectory + '/' + prefix + '.trips.csv', index=True)
    vehiclePathPassenger.to_csv(outDirectory + '/' + prefix + '.passengerToPathTraversal.csv', index=False)
    PTs.to_csv(outDirectory + '/' + prefix + '.pathTraversals.csv', index=True)
    activities.to_csv(outDirectory + '/' + prefix + '.activities.csv', index=True)


if __name__ == '__main__':
    inDirectory = 'https://beam-outputs.s3.amazonaws.com/pilates-outputs/austin-2010-2018-central/2018/beam_outputs'
    prefixes = ['austin-pilates-base__2021-12-16_00-35-49_vre/ITERS/it.0/0']
    outDirectory = 'out/austin-pilates'
    for prefix in prefixes:
        collectAllData(inDirectory, outDirectory, prefix)

    print('done')
