import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PEVs = []
PLVs = []
PTs = []

# for chunk in pd.read_csv('https://beam-outputs.s3.amazonaws.com/output/newyork/nyc-600k-baseline-09__2020-10-23_21-31-11_hfa/ITERS/it.10/10.events.csv.gz', chunksize = 1000000):
# for chunk in pd.read_csv('https://beam-outputs.s3.amazonaws.com/output/newyork/nyc-600k-future-return_to_normal-5-bus_05-work_low-fear_med-triputility--5__2020-10-23_21-31-11_kto/ITERS/it.10/10.events.csv.gz', chunksize = 1000000):
# for chunk in pd.read_csv('https://beam-outputs.s3.amazonaws.com/output/newyork/nyc-600k-baseline__2020-10-22_22-20-18_mss/ITERS/it.10/10.events.csv.gz', chunksize = 1000000):
for chunk in pd.read_csv('events/newnormal-600k.csv.gz', chunksize=1000000):
    chunk['vehicle'] = chunk['vehicle'].astype(str)
    PEV = chunk.loc[(chunk.type == "PersonEntersVehicle") &
                    ~(chunk['person'].apply(str).str.contains('Agent').fillna(False)) &
                    ~(chunk['vehicle'].str.contains('rideHail').fillna(False)) &
                    ~(chunk['vehicle'].str.contains('body').fillna(False)) &
                    ~(chunk['vehicle'].str.isnumeric().fillna(False)), :].dropna(how='all', axis=1)
    PEVs.append(PEV)
    PLV = chunk.loc[(chunk.type == "PersonLeavesVehicle") &
                    ~(chunk['person'].apply(str).str.contains('Agent').fillna(False)) &
                    ~(chunk['vehicle'].str.contains('rideHail').fillna(False)) &
                    ~(chunk['vehicle'].str.contains('body').fillna(False)) &
                    ~(chunk['vehicle'].str.isnumeric().fillna(False)), :].dropna(how='all', axis=1)
    PLVs.append(PLV)
    PT = chunk.loc[(chunk['type'] == 'PathTraversal') & (chunk.vehicle.str.contains(':'))].dropna(how='all', axis=1)
    PTs.append(PT)

PEVs = pd.concat(PEVs)
PLVs = pd.concat(PLVs)
PTs = pd.concat(PTs)
PTs = PTs.loc[PTs.length > 0, :]

# %%
PEVs['personId'] = PEVs['person'].astype(int)
transitRiders = pop.merge(PEVs, how='inner', left_on='personId', right_on='personId').drop_duplicates('personId')

# %%

boardings = PEVs.value_counts(['vehicle', 'time']).rename('Boardings').reset_index()
alightings = PLVs.value_counts(['vehicle', 'time']).rename('Alightings').reset_index()

# boardings.index = boardings.index.set_levels(boardings.index.levels[-1].astype(int), level=-1)
# alightings.index = alightings.index.set_levels(alightings.index.levels[-1].astype(int), level=-1)
# %%
# PTs['time'] = PTs['time'].apply(int)
joined = PTs[
    ['vehicle', 'time', 'startX', 'startY', 'capacity', 'numPassengers', 'arrivalTime', 'departureTime']].merge(
    boardings, left_on=['vehicle', 'departureTime'], right_on=['vehicle', 'time'], how='left').merge(
    alightings, left_on=['vehicle', 'arrivalTime'], right_on=['vehicle', 'time'], how='left')

# %%


nPassengers = joined.fillna(0).groupby('vehicle').agg({'numPassengers': [np.max, np.mean]}) * 6.67
nPassengers.to_csv('out/600k-newnormal-ridership.csv.gz')

meanIncome = pop.merge(PEVs, how='inner', left_on='personId', right_on='personId').drop_duplicates(
    ['personId', 'vehicle']).groupby('vehicle').agg({'incomeValue': np.mean, 'personId': np.size}).rename(
    columns={'personId': 'uniqueRiders', 'incomeValue': 'meanIncome'})
print('Mean Income: ' + str(np.sum(meanIncome.meanIncome * meanIncome.uniqueRiders) / np.sum(meanIncome.uniqueRiders)))

meanIncome.to_csv('out/600k-newnormal-income.csv.gz')

# %%
joined.to_csv('out/600k-Baseline-Trips.csv.gz')
# %%
veh = joined.vehicle.sample(1, weights=joined.numPassengers).values[0]
# %%

rand = joined.loc[joined.vehicle == veh, :]
gdf = gpd.GeoDataFrame(rand, geometry=gpd.points_from_xy(rand.startX, rand.startY, crs="EPSG:4326"))

ax1 = plt.subplot(121)
gdf.to_crs(epsg=3857).plot(column='numPassengers', ax=ax1)
ctx.add_basemap(ax1, reset_extent=False, source=ctx.providers.Stamen.TonerLite)
plt.title(veh)

ax2 = plt.subplot(122)
ax2.plot(rand.time_x / 3600, np.cumsum(rand.Boardings.fillna(0)) * 6.67, label="Boardings")
ax2.plot(rand.time_x / 3600, np.cumsum(rand.Alightings.fillna(0)) * 6.67, label="Alightings")
ax2.plot(rand.time_x / 3600, np.cumsum(rand.Boardings.fillna(0)) * 6.67 - np.cumsum(rand.Alightings.fillna(0)) * 6.67,
         label="Occupancy")
plt.legend()
plt.xlabel('Hour of Day')


# %%
def getRoute(string):
    if string[:3] == "MTA":
        return string.split('_', 4)[-1]
        # return string.split('_')[-2]
    elif string[:5] == "NYC_S":
        return string.split('_')[-1]
    else:
        return "Other"


joined['hour'] = np.floor(joined.departureTime / 7200) * 2
joined['route'] = joined.vehicle.apply(getRoute)

# %%
byRouteAndHour = joined.groupby(['startX', 'startY', 'hour', 'route']).agg(
    {'Boardings': 'sum', 'Alightings': 'sum', 'time': 'size'}).reset_index()
byRouteAndHour = byRouteAndHour.loc[byRouteAndHour.route != 'Other']
byRouteAndHour['BoardingsPerStop'] = byRouteAndHour['Boardings'] / byRouteAndHour['time']
byRouteAndHour['AlightingsPerStop'] = byRouteAndHour['Alightings'] / byRouteAndHour['time']

# byRouteAndHour.rename(columns={'time':'observations'}).to_csv('out/600k-Baseline-BA.csv.gz')
# %%

rt = byRouteAndHour.sample(1, weights=byRouteAndHour.Boardings)
rand = byRouteAndHour.loc[(byRouteAndHour.route == rt.route.values[0]) & (byRouteAndHour.hour == rt.hour.values[0]), :]

# %%
rand = byRouteAndHour.loc[(byRouteAndHour.route == "Q58_841") & (byRouteAndHour.hour == 8) & (byRouteAndHour.time > 1),
       :]

gdf = gpd.GeoDataFrame(rand, geometry=gpd.points_from_xy(rand.startX, rand.startY, crs="EPSG:4326"))

ax1 = plt.subplot(121)
gdf.to_crs(epsg=3857).plot(column='BoardingsPerStop', ax=ax1)
ctx.add_basemap(ax1, source=ctx.providers.Stamen.TonerLite)
plt.title("Boardings " + rt.route.values[0])

ax2 = plt.subplot(122)
gdf.to_crs(epsg=3857).plot(column='AlightingsPerStop', ax=ax2)
ctx.add_basemap(ax2, source=ctx.providers.Stamen.TonerLite)
plt.title("Alightings " + rt.route.values[0])

# %%

trips_base = pd.read_csv('out/600k-Baseline-Trips.csv.gz')
trips_sep = pd.read_csv('out/600k-September-Trips.csv.gz')
trips_return = pd.read_csv('out/600k-ReturnToNormal-Trips.csv.gz')

# %%
veh = trips_base.vehicle.sample(1, weights=trips_base.numPassengers).values[0]

# %%
rand = trips_base.loc[trips_base.vehicle == veh, :]
gdf = gpd.GeoDataFrame(rand, geometry=gpd.points_from_xy(rand.startX, rand.startY, crs="EPSG:4326"))

rand['scaledPassengers'] = rand['numPassengers'] * 6.67
ax1 = plt.subplot(121)
gdf.to_crs(epsg=3857).plot(column='scaledPassengers', ax=ax1, legend=True,
                           legend_kwds={'label': "Occupancy", 'orientation': "horizontal"})
# ax1.axis("equal")
ctx.add_basemap(ax1, reset_extent=False, source=ctx.providers.Stamen.TonerLite)

ax1.set_yticks([])
ax1.set_xticks([])

ax2 = plt.subplot(122)
# ax2.plot(rand.time_x/3600, np.cumsum(rand.Boardings.fillna(0))*6.67, label="Boardings")
# ax2.plot(rand.time_x/3600, np.cumsum(rand.Alightings.fillna(0))*6.67, label="Alightings")
ax2.plot(rand.time_x / 3600, np.cumsum(rand.Boardings.fillna(0)) * 6.67 - np.cumsum(rand.Alightings.fillna(0)) * 6.67,
         label="Baseline")

plt.xlabel('Hour of Day')

rand = trips_sep.loc[trips_sep.vehicle == veh, :]
ax2.plot(rand.time_x / 3600, np.cumsum(rand.Boardings.fillna(0)) * 6.67 - np.cumsum(rand.Alightings.fillna(0)) * 6.67,
         label="September")

rand = trips_return.loc[trips_return.vehicle == veh, :]
ax2.plot(rand.time_x / 3600, np.cumsum(rand.Boardings.fillna(0)) * 6.67 - np.cumsum(rand.Alightings.fillna(0)) * 6.67,
         label="New Normal")
plt.legend()

print(veh)

# %%
