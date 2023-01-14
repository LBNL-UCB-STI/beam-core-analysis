import os

import numpy as np
import pandas as pd

filename = "~/Downloads/nyc-final-events-base-1.csv.gz"

ev = pd.read_csv(filename, nrows=5000000)

ev['vehicle'] = ev['vehicle'].astype(str)
PEV = ev.loc[(ev.type == "PersonEntersVehicle") &
             ~(ev['person'].apply(str).str.contains('Agent').fillna(False)) &
             ~(ev['vehicle'].str.contains('rideHail').fillna(False)) &
             ~(ev['vehicle'].str.contains('body').fillna(False)) &
             ~(ev['vehicle'].str.contains('emergency').fillna(False)) &
             ~(ev['vehicle'].str.isnumeric().fillna(False)), :].dropna(how='all', axis=1)

PLV = ev.loc[(ev.type == "PersonLeavesVehicle") &
             ~(ev['person'].apply(str).str.contains('Agent').fillna(False)) &
             ~(ev['vehicle'].str.contains('rideHail').fillna(False)) &
             ~(ev['vehicle'].str.contains('body').fillna(False)) &
             ~(ev['vehicle'].str.contains('emergency').fillna(False)) &
             ~(ev['vehicle'].str.isnumeric().fillna(False)), :].dropna(how='all', axis=1)

PEV['personId'] = PEV['person'].astype(int)

boardings = PEV.value_counts(['vehicle', 'time']).rename('Boardings').reset_index()
alightings = PLV.value_counts(['vehicle', 'time']).rename('Alightings').reset_index()

PTs = ev.loc[(ev.type == "PathTraversal") &
             (ev.vehicle.str.startswith("MTA") | ev.vehicle.str.startswith("NYC") |
              ev.vehicle.str.startswith("NJ") | ev.vehicle.str.startswith("NICE") |
              ev.vehicle.str.startswith("Long") | ev.vehicle.str.startswith("JFK") |
              ev.vehicle.str.startswith("Metro") | ev.vehicle.str.startswith("151") |
              ev.vehicle.str.startswith("Staten"))].dropna(how='all', axis=1)


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


combined = PEV.sort_values(['person', 'time'])
combined['vehicleType'] = combined.vehicle.apply(agencyFromVehicle)
samePersonPrevious = combined.iloc[1:]['person'].values == combined.iloc[:-1]['person'].values
transferEligible = (combined.iloc[1:]['vehicleType'].values == 0) & (combined.iloc[:-1]['vehicleType'].values == 0)

toDelete = np.concatenate([[False], transferEligible & samePersonPrevious])
combined = combined.loc[~toDelete]

combined['trip_id'] = combined['vehicle'].str.split(':', expand=True)[1]

combined = combined.merge(PTs[['time', 'vehicle', 'toStopIndex']], on=['time', 'vehicle']).rename(
    columns={"toStopIndex": "stop_sequence"})

gtfsDirs = [f for f in os.walk("GTFS/")][0][1]
stops = []
stopTimes = []
trips = []
for dir in gtfsDirs:
    stops.append(pd.read_csv(os.path.join("GTFS", dir, "stops.txt")).dropna(how='all', axis=1))
    trips.append(pd.read_csv(os.path.join("GTFS", dir, "trips.txt")).dropna(how='all', axis=1))
    stopTimes.append(pd.read_csv(os.path.join("GTFS", dir, "stop_times.txt"),
                                 usecols=['trip_id', 'stop_id', 'stop_sequence']).dropna(how='all', axis=1))

stops = pd.concat(stops)
stopTimes = pd.concat(stopTimes)
trips = pd.concat(trips)

combined = combined.merge(stopTimes, on=['trip_id', 'stop_sequence'])
combined = combined.merge(stops[["stop_id", "stop_name"]], on="stop_id")
combined = combined.merge(trips[["trip_id", "route_id"]], on="trip_id")

combined['fare_id'] = combined['stop_name'].copy()
combined.loc[combined.vehicleType == 0, "fare_id"] = combined.loc[combined.vehicleType == 0, "route_id"].copy()

mat = combined.groupby(['personId', 'fare_id']).size().unstack(fill_value=0)

print('stop')
nPersons = mat.shape[0]
nStops = mat.shape[1]
import cvxpy as cp

b = np.floor(np.random.lognormal(0.5, 1, nStops))

x = cp.Variable(nPersons, nonneg=True)
objective = cp.Minimize(cp.sum_squares(x @ mat.values - b) + 0 * cp.sum_squares(x))
prob = cp.Problem(objective)
prob.solve()
