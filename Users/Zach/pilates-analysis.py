import itertools

import geopandas as gpd
import numpy as np
import pandas as pd
from joblib import Parallel, delayed

# path = "https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-2018-baseline-20220704/activitysim/year-{0}-iteration-{1}/plans.csv.gz"
# linkstatsPath = "https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-2018-baseline-20220704/beam/year-{0}-iteration-{1}/ITERS/it.0/0.linkstats.csv.gz"
# skimsPath = "https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-2018-baseline-20220704/beam/year-{0}-iteration-{1}/ITERS/it.0/0.activitySimODSkims_current.csv.gz"

path = "https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-RH_fleetsz_0.5-20220408/activitysim/year-{0}-iteration-{1}/plans.csv.gz"
linkstatsPath = "https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-RH_fleetsz_0.5-20220408/beam/year-{0}-iteration-{1}/ITERS/it.0/0.linkstats.csv.gz"
skimsPath = "https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-RH_fleetsz_0.5-20220408/beam/year-{0}-iteration-{1}/ITERS/it.0/0.activitySimODSkims_current.csv.gz"

years = range(2018, 2022)
iters = range(0, 6)

plans = dict()
linkstats = dict()

modeTransform = {'BIKE': 'Bike',
                 'DRIVEALONEFREE': 'SOV',
                 'DRIVEALONEPAY': 'SOV',
                 'DRIVE_COM': 'DriveTransit',
                 'DRIVE_EXP': 'DriveTransit',
                 'DRIVE_HVY': 'DriveTransit',
                 'DRIVE_LOC': 'DriveTransit',
                 'DRIVE_LRF': 'DriveTransit',
                 'SHARED2FREE': 'HOV',
                 'SHARED2PAY': 'HOV',
                 'SHARED3FREE': 'HOV',
                 'SHARED3PAY': 'HOV',
                 'TAXI': 'Taxi/TNC',
                 'TNC_SHARED': 'Taxi/TNC',
                 'TNC_SINGLE': 'Taxi/TNC',
                 'WALK': 'Walk',
                 'WALK_COM': 'WalkTransit',
                 'WALK_EXP': 'WalkTransit',
                 'WALK_HVY': 'WalkTransit',
                 'WALK_LOC': 'WalkTransit',
                 'WALK_LRF': 'WalkTransit',
                 }

for yr in years:
    for it in iters:
        # print(path.format(yr, it))
        # df = pd.read_csv(path.format(yr, it))
        # plans[(yr, it)] = df
        # df.to_csv("data/pilates/plans-fastertransit-{0}-{1}.csv.gz".format(yr, it), index=False)
        if it >= 0:
            # df = pd.read_csv(linkstatsPath.format(yr, it))
            # linkstats[(yr, it)] = df
            # df.to_csv("data/pilates/linkstats-fastertransit-{0}-{1}.csv.gz".format(yr, it), index=False)
            df = pd.read_csv(skimsPath.format(yr, it))
            # linkstats[(yr, it)] = df
            df.to_csv("data/pilates/skims-lessrh-{0}-{1}.csv.gz".format(yr, it), index=False)


def addGeometryIdToDataFrame(df, gdf, xcol, ycol, idColumn="geometry", df_geom='epsg:4326'):
    gdf_data = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[xcol], df[ycol]), crs=df_geom)
    gdf_data.set_crs(df_geom)
    joined = gpd.sjoin(gdf_data.to_crs('epsg:26910'), gdf.to_crs('epsg:26910'))
    gdf_data = gdf_data.merge(joined['taz1454'], left_index=True, right_index=True, how="left")
    gdf_data.rename(columns={'taz1454': idColumn}, inplace=True)
    df = pd.DataFrame(gdf_data.drop(columns='geometry'))
    df.drop(columns=[xcol, ycol], inplace=True)
    return df.loc[~df.index.duplicated(keep='first'), :]


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
    plans.loc[:, 'tripPurpose'] = np.nan
    plans.iloc[legInds, plans.columns.get_loc('tripPurpose')] = plans['ActivityType'].iloc[legInds + 1].copy()
    return plans


taz = gpd.read_file('scenario/taz/joinedTAZs.shp')

for yr in years:
    for it in iters:
        pl = pd.read_csv("data/pilates/plans-lessrh-{0}-{1}.csv.gz".format(yr, it))
        pl = addTimesToPlans(pl)
        trips = pl.loc[(pl['ActivityElement'].str.lower().str.contains('leg'))].dropna(how='all', axis=1)
        processed_list = Parallel(n_jobs=-1)(
            delayed(addGeometryIdToDataFrame)(t, taz, "originX", "originY", "originTAZ") for t in
            np.array_split(trips, 100))
        # trips = addGeometryIdToDataFrame(trips, taz, "originX", "originY", "originTAZ")
        processed_list2 = Parallel(n_jobs=-1)(
            delayed(addGeometryIdToDataFrame)(t, taz, "destinationX", "destinationY", "destinationTAZ") for t in
            processed_list)
        trips = pd.concat(processed_list2)
        # trips = addGeometryIdToDataFrame(trips, taz, "destinationX", "destinationY", "destinationTAZ")
        trips['mode'] = trips['trip_mode'].apply(lambda x: modeTransform[x])
        # plans[(yr, it)] = trips
        trips.to_csv("data/pilates/trips-lessrh-{0}-{1}.csv.gz".format(yr, it), index=False)

gb = trips.groupby(['originTAZ', 'destinationTAZ', 'mode']).agg({'person_id': 'size'}).unstack().fillna(0.0)[
    'person_id']

odflows = {(yr, it): pd.read_csv("data/pilates/trips-{0}-{1}.csv.gz".format(yr, it)).groupby(
    ['originTAZ', 'destinationTAZ', 'mode']).agg({'person_id': 'size'}).unstack().fillna(0.0)[
    'person_id'] for (yr, it) in itertools.product(years, iters)}
combined = pd.concat(odflows, axis=1).fillna(0.0)

allskims = {(yr, it): pd.read_csv("data/pilates/skims-{0}-{1}.csv.gz".format(yr, it)).groupby(
    ['timePeriod', 'pathType', 'origin', 'destination']).agg('first').fillna(0.0) for (yr, it) in
            itertools.product(years, iters)}
combinedSkims = pd.concat(allskims, axis=1)

mseSOV = np.array([np.sqrt(
    np.nanmean((combined.loc[:, pd.IndexSlice[:, :, "SOV"]].iloc[:, idx] - combined.loc[:,
                                                                           pd.IndexSlice[:, :, "SOV"]].iloc[:,
                                                                           idx + 1]) ** 2.0))
    for
    idx in range(27)])

mseWT = np.array([np.sqrt(
    np.nanmean((combined.loc[:, pd.IndexSlice[:, :, "WalkTransit"]].iloc[:, idx] - combined.loc[:,
                                                                                   pd.IndexSlice[:, :,
                                                                                   "WalkTransit"]].iloc[:,
                                                                                   idx + 1]) ** 2.0))
    for
    idx in range(27)])

mseWALK = np.array([np.sqrt(
    np.nanmean((combined.loc[:, pd.IndexSlice[:, :, "Walk"]].iloc[:, idx] - combined.loc[:,
                                                                            pd.IndexSlice[:, :,
                                                                            "Walk"]].iloc[:,
                                                                            idx + 1]) ** 2.0))
    for
    idx in range(27)])

mseDT = [
    np.sqrt(
        np.nanmean(
            (combined.loc[:,
             pd.IndexSlice[idx, "DriveTransit"]] - combined.loc[:,
                                                   pd.IndexSlice[idx + 1, "DriveTransit"]]) ** 2.0)) for idx in
    range(5)]

mseHOV = [
    np.sqrt(
        np.nanmean(
            (combined.loc[:,
             pd.IndexSlice[idx, "HOV"]] - combined.loc[:,
                                          pd.IndexSlice[idx + 1, "HOV"]]) ** 2.0)) for idx in range(5)]

mseTAXI = [
    np.sqrt(
        np.nanmean(
            (combined.loc[:,
             pd.IndexSlice[idx, "Taxi/TNC"]] - combined.loc[:,
                                               pd.IndexSlice[idx + 1, "Taxi/TNC"]]) ** 2.0)) for idx in range(5)]

plt.hist(combined.loc[:, pd.IndexSlice[0, "Walk"]] - combined.loc[:, pd.IndexSlice[1, "Walk"]], bins=range(-60, 60),
         histtype='step')

print('done')

odflows = {s: pd.read_csv("data/pilates/trips-{0}-{1}-{2}transit.csv.gz".format(2020, 2, s)).groupby(
    ['originTAZ', 'destinationTAZ', 'mode']).agg({'person_id': 'size'}).unstack().fillna(0.0)[
    'person_id'] for s in ['more', 'same']}
combined = pd.concat(odflows, axis=1).fillna(0.0)

combined.columns

diff = combined.loc[:, pd.IndexSlice["more", "WalkTransit"]] - combined.loc[:, pd.IndexSlice["same", "WalkTransit"]]
changeByOrigin = diff.unstack().sum(axis=1)
changeByOrigin._set_name("ChangeByOrigin", inplace=True)

allskims = {s: pd.read_csv("data/pilates/skims-{0}-{1}-{2}transit.csv.gz".format(2018, 0, s)).groupby(
    ['timePeriod', 'pathType', 'origin', 'destination']).agg('first').fillna(0.0) for s in ['more', 'same']}
combinedSkims = pd.concat(allskims, axis=1)
