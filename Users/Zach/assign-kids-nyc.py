import difflib
from io import BytesIO
from zipfile import ZipFile

import numpy as np
import pandas as pd
import requests


def agencyFromVehicle(vehicle):
    agencyIndex = {"MTA-subway": 0, "MTA-bus": 1, "NJ": 2, "NICE": 3, "Long": 4, "JFK": 5, "Metro-North": 6, "151": 7,
                   "WCDOT": 8}
    relevant = vehicle.split('_', 3)[:3]
    if relevant[0] == "MTA":
        return 1
    elif relevant[0] == "NYC":
        if relevant[1] == "Subway":
            return 0
        else:
            return 1
    elif relevant[0] == "Staten":
        return 1
    else:
        return agencyIndex.get(relevant[0], 9)


def calcRidership(scenario, trips, stops, stopTimes):
    print("Mapping MTA stations to GTFS stops")
    ridership = pd.read_excel('data/STD_Ridership_by_stn_timeperiod.xlsx')
    ridership['STATION'] = ridership['STATION'].str.split('(', expand=True)[0]
    mta_stations = ridership['STATION'].unique()

    combined = stopTimes.merge(trips, on="trip_id").merge(stops, on="stop_id")
    combined['fare_id'] = combined['stop_name'].copy()
    combined.loc[combined['route_id'] == "SI", "fare_id"] = 'SIR'

    gtfs_stations = combined['fare_id'].unique()
    mtaToGTFS = dict()
    for stop in mta_stations:
        matches = difflib.get_close_matches(stop, gtfs_stations)
        if len(matches) > 0:
            mtaToGTFS[stop] = matches[0]

    mtaToGTFS['West 4 St-Washington Sq '] = 'W 4 St - Wash Sq'
    mtaToGTFS['Beach 67 St-Arverne By The Sea '] = 'Beach 67 St'
    mtaToGTFS['Briarwood-Van Wyck Blvd '] = 'Briarwood'
    mtaToGTFS['Bushwick Av-Aberdeen St '] = 'Bushwick Av - Aberdeen St'
    mtaToGTFS['Aqueduct-North Conduit Av '] = 'Aqueduct - N Conduit Av'

    ridership['STATION'].replace(mtaToGTFS, inplace=True)

    meanRidership = ridership.groupby(['R_DATE', 'TPERIOD', 'STATION', 'CTGRY']).agg(sum).unstack('R_DATE',
                                                                                                  fill_value=0).mean(
        axis=1).unstack(-1, fill_value=0)
    meanRidership.to_csv('data/nyc-meanRidership-{0}.csv'.format(scenario))
    return meanRidership


scenario = "august2020"

s3eventsPath = {
    "base": "https://beam-outputs.s3.amazonaws.com/output/newyork/new-york-baseline-{0}-of-10__{1}/ITERS/it.5/5.events.csv.gz",
    "august2020": "https://beam-outputs.s3.amazonaws.com/output/newyork/new-york-august2020-{0}-of-10__{1}/ITERS/it.5/5.events.csv.gz"}
s3strings = {"base": [
    "2023-01-03_19-59-12_nwn",
    "2023-01-03_19-59-13_jgp",
    "2023-01-03_19-59-06_brm",
    "2023-01-03_19-59-07_kqr",
    "2023-01-03_19-59-09_fbb",
    "2023-01-03_19-59-11_tjh",
    "2023-01-03_19-59-12_zwm",
    "2023-01-03_19-59-19_bcr",
    "2023-01-03_19-59-14_olx",
    "2023-01-03_19-59-07_xcc"
],
    "august2020": [
        "2023-01-10_16-52-48_lgr",  # 0
        "2023-01-10_16-52-46_gib",  # 1
        "2023-01-14_21-19-56_ito",  # 2
        "2023-01-15_01-54-50_lcs",  # 3
        "2023-01-10_16-52-43_rio",  # 4
        "2023-01-10_16-53-00_vjr",  # 5
        "2023-01-10_16-52-53_bhh",  # 6
        "2023-01-10_16-53-01_drt",  # 7
        "2023-01-10_16-53-15_qgy",  # 8
        "2023-01-10_16-53-14_pdt"  # 9
    ]}

gtfsTemplate = "https://github.com/LBNL-UCB-STI/beam-data-newyork/raw/update-calibration/r5-prod/{0}.zip"

gtfsDirs = [
    "MTA_Bronx_20200121",
    "MTA_Brooklyn_20200118",
    "MTA_Manhattan_20200123",
    "MTA_Queens_20200118",
    "MTA_Staten_Island_20200118",
    "NYC_Bus_Company_20200104",
    "NYC_Subway_20200109"
]

stops = []
stopTimes = []
trips = []
print("Loading GTFS")
for dir in gtfsDirs:
    print("Download GTFS: {0}".format(dir))
    r = requests.get(gtfsTemplate.format(dir))
    files = ZipFile(BytesIO(r.content))
    stops.append(pd.read_csv(files.open("stops.txt")).dropna(how='all', axis=1))
    trips.append(pd.read_csv(files.open("trips.txt")).dropna(how='all', axis=1))
    stopTimes.append(pd.read_csv(files.open("stop_times.txt"),
                                 usecols=['trip_id', 'stop_id', 'stop_sequence']).dropna(how='all', axis=1))

stops = pd.concat(stops)
stopTimes = pd.concat(stopTimes)
trips = pd.concat(trips)

meanRidership = calcRidership(scenario, trips, stops, stopTimes)


def definePersonProfiles(popChunkInt, s3string):
    print("Starting on population chunk {0}".format(popChunkInt))
    popChunk = str(popChunkInt)
    filename = s3eventsPath[scenario].format(popChunk, s3string)

    PEVs = []
    PTs = []
    for chunk in pd.read_csv(filename, chunksize=2000000):
        chunk['vehicle'] = chunk['vehicle'].astype(str)
        PEV = chunk.loc[(chunk.type == "PersonEntersVehicle") &
                        ~(chunk['person'].apply(str).str.contains('Agent').fillna(False)) &
                        ~(chunk['vehicle'].str.contains('rideHail').fillna(False)) &
                        ~(chunk['vehicle'].str.contains('body').fillna(False)) &
                        ~(chunk['vehicle'].str.contains('emergency').fillna(False)) &
                        ~(chunk['vehicle'].str.isnumeric().fillna(False)), :].dropna(how='all', axis=1)

        PEV['personId'] = PEV['person'].astype(int)
        PEVs.append(PEV)

        PT = chunk.loc[(chunk.type == "PathTraversal") &
                       (chunk.vehicle.str.startswith("MTA") | chunk.vehicle.str.startswith("NYC") |
                        chunk.vehicle.str.startswith("NJ") | chunk.vehicle.str.startswith("NICE") |
                        chunk.vehicle.str.startswith("Long") | chunk.vehicle.str.startswith("JFK") |
                        chunk.vehicle.str.startswith("Staten"))].dropna(how='all', axis=1)
        PTs.append(PT)

    print("Done loading events file for population chunk {0}".format(popChunkInt))
    PEVs = pd.concat(PEVs)
    PTs = pd.concat(PTs)
    PTs = PTs.loc[PTs.length > 0, :]

    combined = PEVs.sort_values(['person', 'time'])
    combined['vehicleType'] = combined.vehicle.apply(agencyFromVehicle)
    samePersonPrevious = combined.iloc[1:]['person'].values == combined.iloc[:-1]['person'].values
    transferEligible = (combined.iloc[1:]['vehicleType'].values == 0) & (combined.iloc[:-1]['vehicleType'].values == 0)

    toDelete = np.concatenate([[False], transferEligible & samePersonPrevious])
    combined = combined.loc[~toDelete]
    combined = combined.loc[(combined.vehicleType == 0), :]
    combined['hour'] = np.floor(combined.time / 3600)
    combined['TimePeriod'] = '12AM-6AM'
    combined.loc[combined.hour >= 6.0, 'TimePeriod'] = '6AM-9AM'
    combined.loc[combined.hour >= 9.0, 'TimePeriod'] = '9AM-4PM'
    combined.loc[combined.hour >= 16.0, 'TimePeriod'] = '4PM-7PM'
    combined.loc[combined.hour >= 19.0, 'TimePeriod'] = '7PM-12AM'

    combined['trip_id'] = combined['vehicle'].str.split(':', expand=True)[1]

    combined = combined.merge(PTs[['time', 'vehicle', 'toStopIndex']], on=['time', 'vehicle']).rename(
        columns={"toStopIndex": "stop_sequence"})

    combined = combined.merge(stopTimes, on=['trip_id', 'stop_sequence'])
    combined = combined.merge(stops[["stop_id", "stop_name"]], on="stop_id")
    combined = combined.merge(trips[["trip_id", "route_id"]], on="trip_id")

    combined['fare_id'] = combined['stop_name'].copy()
    combined.loc[combined['route_id'] == "SI", "fare_id"] = 'SIR'

    mat = combined.groupby(['personId', 'fare_id', 'TimePeriod']).size().unstack(fill_value=0).unstack(fill_value=0)

    reindexed = mat.reindex(meanRidership.index, axis=1).fillna(0)

    reindexed.to_parquet('data/nyc-reindexed-{0}-{1}.parquet'.format(scenario, popChunk))
    print("Done saving output file for population chunk {0}".format(popChunkInt))


[definePersonProfiles(ii, s3string) for ii, s3string in enumerate(s3strings[scenario])]
