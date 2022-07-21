import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

taz = gpd.read_file('scenario/taz/joinedTAZs.shp')


def toTimeBin(hour: int):
    hour = hour % 24
    if hour < 3:
        return 'EVENING'
    elif hour < 6:
        return 'EARLY_AM'
    elif hour < 10:
        return 'AM_PEAK'
    elif hour < 15:
        return 'MIDDAY'
    elif hour < 19:
        return 'PM_PEAK'
    else:
        return 'EVENING'


def aggregateInTimePeriod(df, keepGeom=False):
    if df['completedRequests'].sum() > 0:
        totalCompletedRequests = df['completedRequests'].sum()
        waitTime = (df['waitTime'] * df['completedRequests']).sum() / totalCompletedRequests / 60.
        costPerMile = (df['costPerMile'] * df['completedRequests']).sum() / totalCompletedRequests
        observations = df['observations'].sum()
        unmatchedRequestPortion = 1. - totalCompletedRequests / observations
        out = {"waitTimeInMinutes": waitTime, "costPerMile": costPerMile,
               "unmatchedRequestPortion": unmatchedRequestPortion, "observations": observations,
               "completedRequests": totalCompletedRequests}
    else:
        observations = df['observations'].sum()
        out = {"waitTimeInMinutes": 6.0, "costPerMile": 5.0,
               "unmatchedRequestPortion": 1.0, "observations": observations,
               "completedRequests": 0}
    if keepGeom:
        geom = df['geometry'].iloc[0]
        out['geometry'] = geom
    return pd.Series(out)


runs = {'50pop-5veh': (0.5, 0.05),
        '50pop-10veh': (0.5, 0.1),
        '50pop-20veh': (0.5, 0.2),
        '50pop-50veh': (0.5, 0.50),
        '50pop-100veh': (0.5, 1.0),
        '100pop-20veh': (1.0, 0.2)}

index = []
skimsByDisability = []
skimsByDisabilityAndTimePeriod = []
skimsByDisabilityAndPooled = []
skimsByDisabilityAndCounty = []
skimsByDisabilityAndCountyAndTimePeriod = []
skimsByDisabilityAndTaz = []
for fname, idx in runs.items():
    skims = pd.read_csv("disability/skims-{0}.csv.gz".format(fname), dtype={'costPerMile': float}, na_values=['∞'])
    skims = skims.merge(taz, right_on='taz1454', left_on='tazId')
    skims['timePeriod'] = skims['hour'].apply(toTimeBin)
    skims['completedRequests'] = skims['observations'] * (1. - skims['unmatchedRequestsPercent'] / 100.)
    index.append(idx)  # (pd.MultiIndex.from_tuples([idx], names=["portionInWheelchair", "portionVehiclesAccessible"]))
    skimsByDisability.append(skims.groupby(['wheelchairRequired']).apply(aggregateInTimePeriod))
    skimsByDisabilityAndTimePeriod.append(
        skims.groupby(['wheelchairRequired', 'timePeriod']).apply(aggregateInTimePeriod))
    skimsByDisabilityAndPooled.append(
        skims.groupby(['wheelchairRequired', 'reservationType']).apply(aggregateInTimePeriod))
    skimsByDisabilityAndCounty.append(
        skims.groupby(['wheelchairRequired', 'reservationType', 'county']).apply(aggregateInTimePeriod))
    skimsByDisabilityAndCountyAndTimePeriod.append(
        skims.groupby(['wheelchairRequired', 'reservationType', 'county', 'timePeriod']).apply(aggregateInTimePeriod))
    skimsByDisabilityAndTaz.append(
        skims.groupby(['wheelchairRequired', 'reservationType', 'tazId']).apply(aggregateInTimePeriod, True))

skimsByDisability = pd.concat(skimsByDisability, keys=index, names=['disabilitySample', 'fleetAccessibility'])
skimsByDisabilityAndTimePeriod = pd.concat(skimsByDisabilityAndTimePeriod, keys=index,
                                           names=['disabilitySample', 'fleetAccessibility'])
skimsByDisabilityAndPooled = pd.concat(skimsByDisabilityAndPooled, keys=index,
                                       names=['disabilitySample', 'fleetAccessibility'])
skimsByDisabilityAndCounty = pd.concat(skimsByDisabilityAndCounty, keys=index,
                                       names=['disabilitySample', 'fleetAccessibility'])
skimsByDisabilityAndCountyAndTimePeriod = pd.concat(skimsByDisabilityAndCountyAndTimePeriod, keys=index,
                                                    names=['disabilitySample', 'fleetAccessibility'])
skimsByDisabilityAndTaz = pd.concat(skimsByDisabilityAndTaz, keys=index,
                                    names=['disabilitySample', 'fleetAccessibility'])

skimsByDisability.to_csv('out/disability/skims-agg.csv')
skimsByDisabilityAndTimePeriod.to_csv('out/disability/skims-agg-time-period.csv')
skimsByDisabilityAndPooled.to_csv('out/disability/skims-agg-pooled.csv')
skimsByDisabilityAndCounty.to_csv('out/disability/skims-agg-county.csv')
skimsByDisabilityAndCountyAndTimePeriod.to_csv('out/disability/skims-agg-county-time-period.csv')
# skimsByDisabilityAndTaz.to_csv('out/disability/skims-agg-taz.csv')


plt.figure(1)
plt.plot([0.05, 0.1, 0.2, 0.5, 1.0], skimsByDisabilityAndPooled.loc[
    skimsByDisabilityAndPooled.index.get_level_values('disabilitySample') == 0.5, 'waitTimeInMinutes'].unstack()[
    'Solo'].unstack().values)
plt.xlabel('Portion of fleet accessible')
plt.ylabel('Wait time in minutes')
plt.legend(['Non-wheelchair', 'Wheelchair'])
plt.title('Solo wait times')
plt.savefig('out/disability/solo-wait-times.png')

plt.figure(2)
plt.plot([0.05, 0.1, 0.2, 0.5, 1.0], skimsByDisabilityAndPooled.loc[
    skimsByDisabilityAndPooled.index.get_level_values('disabilitySample') == 0.5, 'unmatchedRequestPortion'].unstack()[
    'Solo'].unstack().values)
plt.xlabel('Portion of fleet accessible')
plt.ylabel('Solo ride portion denied')
plt.legend(['Non-wheelchair', 'Wheelchair'])
plt.title('Solo denied rides')
plt.savefig('out/disability/solo-denied-rides.png')

plt.figure(3)
plt.plot([0.05, 0.1, 0.2, 0.5, 1.0], skimsByDisabilityAndPooled.loc[
    skimsByDisabilityAndPooled.index.get_level_values('disabilitySample') == 0.5, 'waitTimeInMinutes'].unstack()[
    'Pooled'].unstack().values)
plt.xlabel('Portion of fleet accessible')
plt.ylabel('Wait time in minutes')
plt.legend(['Non-wheelchair', 'Wheelchair'])
plt.title('Pooled wait times')
plt.savefig('out/disability/pooled-wait-times.png')

plt.figure(4)
plt.plot([0.05, 0.1, 0.2, 0.5, 1.0], skimsByDisabilityAndPooled.loc[
    skimsByDisabilityAndPooled.index.get_level_values('disabilitySample') == 0.5, 'unmatchedRequestPortion'].unstack()[
    'Pooled'].unstack().values)
plt.xlabel('Portion of fleet accessible')
plt.ylabel('Solo ride portion denied')
plt.legend(['Non-wheelchair', 'Wheelchair'])
plt.title('Pooled denied rides')
plt.savefig('out/disability/pooled-denied-rides.png')


temp = skimsByDisabilityAndCounty.loc[skimsByDisabilityAndCounty.index.get_level_values('disabilitySample') == 0.5, 'unmatchedRequestPortion'].unstack(level=-2)['Solo'].unstack(level=-1)

fig, axs = plt.subplots(3, 3)
for ax, county in zip(axs.flatten(), temp.columns):
    ax.plot([0.05, 0.1, 0.2, 0.5, 1.0], temp[county].unstack().values)
    ax.set_title(county)
    ax.set_ylim(0., 0.14)
    # ax.set_ylim(0.1, 0.4)
axs[1,0].set_ylabel('Solo ride portion denied')
axs[-1,1].set_xlabel('Portion of fleet accessible')
fig.set_figwidth(10)
fig.set_figheight(8)
plt.legend(['Non-wheelchair', 'Wheelchair'])
fig.tight_layout()
plt.savefig('out/disability/solo-denied-rides-by-county.png')

temp = skimsByDisabilityAndCounty.loc[skimsByDisabilityAndCounty.index.get_level_values('disabilitySample') == 0.5, 'unmatchedRequestPortion'].unstack(level=-2)['Pooled'].unstack(level=-1)

fig, axs = plt.subplots(3, 3)
for ax, county in zip(axs.flatten(), temp.columns):
    ax.plot([0.05, 0.1, 0.2, 0.5, 1.0], temp[county].unstack().values)
    ax.set_title(county)
    # ax.set_ylim(0., 0.14)
    ax.set_ylim(0.1, 0.4)
axs[1,0].set_ylabel('Solo ride portion denied')
axs[-1,1].set_xlabel('Portion of fleet accessible')
fig.set_figwidth(10)
fig.set_figheight(8)
plt.legend(['Non-wheelchair', 'Wheelchair'])
fig.tight_layout()
plt.savefig('out/disability/pooled-denied-rides-by-county.png')

temp = skimsByDisabilityAndCounty.loc[skimsByDisabilityAndCounty.index.get_level_values('disabilitySample') == 0.5, 'waitTimeInMinutes'].unstack(level=-2)['Pooled'].unstack(level=-1)

fig, axs = plt.subplots(3, 3)
for ax, county in zip(axs.flatten(), temp.columns):
    ax.plot([0.05, 0.1, 0.2, 0.5, 1.0], temp[county].unstack().values)
    ax.set_title(county)
    ax.set_ylim(3.0, 7.0)
    # ax.set_ylim(0.1, 0.4)
axs[1,0].set_ylabel('Wait time in minutes')
axs[-1,1].set_xlabel('Portion of fleet accessible')
fig.set_figwidth(10)
fig.set_figheight(8)
plt.legend(['Non-wheelchair', 'Wheelchair'])
fig.tight_layout()
plt.savefig('out/disability/pooled-wait-times-by-county.png')

temp = skimsByDisabilityAndCounty.loc[skimsByDisabilityAndCounty.index.get_level_values('disabilitySample') == 0.5, 'waitTimeInMinutes'].unstack(level=-2)['Solo'].unstack(level=-1)

fig, axs = plt.subplots(3, 3)
for ax, county in zip(axs.flatten(), temp.columns):
    ax.plot([0.05, 0.1, 0.2, 0.5, 1.0], temp[county].unstack().values)
    ax.set_title(county)
    ax.set_ylim(1.0, 4.0)
    # ax.set_ylim(0.1, 0.4)
axs[1,0].set_ylabel('Wait time in minutes')
axs[-1,1].set_xlabel('Portion of fleet accessible')
fig.set_figwidth(10)
fig.set_figheight(8)
plt.legend(['Non-wheelchair', 'Wheelchair'])
fig.tight_layout()
plt.savefig('out/disability/solo-wait-times-by-county.png')
print('hmm')

tempWheelchair = skimsByDisabilityAndTaz.loc[skimsByDisabilityAndTaz.index.get_level_values('disabilitySample') == 0.5, 'waitTimeInMinutes'][0.5,:,:,:].unstack(level=-2)['Solo'].unstack(level=-2)[True].unstack(level=-2)
tempNoWheelchair = skimsByDisabilityAndTaz.loc[skimsByDisabilityAndTaz.index.get_level_values('disabilitySample') == 0.5, 'waitTimeInMinutes'][0.5,:,:,:].unstack(level=-2)['Solo'].unstack(level=-2)[False].unstack(level=-2)

ax = taz.merge(tempNoWheelchair, left_on='taz1454', right_index=True).plot(column=1.0, legend=True, vmin=3.0, vmax=6.0)
ax.set_ylim((37.2,38.5))
ax.set_xlim((-123.0,-121.6))
ax.get_figure().set_figheight(8)
ax.get_figure().set_figwidth(8)
ax.set_title('Solo non-wheelchair wait time, 100% accessible vehicles')
plt.savefig('out/disability/solo-wait-times-nowheelchair-100.png')

ax = taz.merge(tempWheelchair, left_on='taz1454', right_index=True).plot(column=1.0, legend=True, vmin=3.0, vmax=6.0)
ax.set_ylim((37.2,38.5))
ax.set_xlim((-123.0,-121.6))
ax.get_figure().set_figheight(8)
ax.get_figure().set_figwidth(8)
ax.set_title('Solo wheelchair wait time, 100% accessible vehicles')
plt.savefig('out/disability/solo-wait-times-wheelchair-100.png')

ax = taz.merge(tempNoWheelchair, left_on='taz1454', right_index=True).plot(column=0.05, legend=True, vmin=3.0, vmax=6.0)
ax.set_ylim((37.2,38.5))
ax.set_xlim((-123.0,-121.6))
ax.get_figure().set_figheight(8)
ax.get_figure().set_figwidth(8)
ax.set_title('Solo non-wheelchair wait time, 5% accessible vehicles')
plt.savefig('out/disability/solo-wait-times-nowheelchair-5.png')

ax = taz.merge(tempWheelchair, left_on='taz1454', right_index=True).plot(column=0.05, legend=True, vmin=3.0, vmax=6.0)
ax.set_ylim((37.2,38.5))
ax.set_xlim((-123.0,-121.6))
ax.get_figure().set_figheight(8)
ax.get_figure().set_figwidth(8)
ax.set_title('Solo wheelchair wait time, 5% accessible vehicles')
plt.savefig('out/disability/solo-wait-times-wheelchair-5.png')

ax = taz.merge(tempNoWheelchair, left_on='taz1454', right_index=True).plot(column=0.2, legend=True, vmin=3.0, vmax=6.0)
ax.set_ylim((37.2,38.5))
ax.set_xlim((-123.0,-121.6))
ax.get_figure().set_figheight(8)
ax.get_figure().set_figwidth(8)
ax.set_title('Solo non-wheelchair wait time, 20% accessible vehicles')
plt.savefig('out/disability/solo-wait-times-nowheelchair-20.png')

ax = taz.merge(tempWheelchair, left_on='taz1454', right_index=True).plot(column=0.2, legend=True, vmin=3.0, vmax=6.0)
ax.set_ylim((37.2,38.5))
ax.set_xlim((-123.0,-121.6))
ax.get_figure().set_figheight(8)
ax.get_figure().set_figwidth(8)
ax.set_title('Solo wheelchair wait time, 20% accessible vehicles')
plt.savefig('out/disability/solo-wait-times-wheelchair-20.png')






tempWheelchair = skimsByDisabilityAndTaz.loc[skimsByDisabilityAndTaz.index.get_level_values('disabilitySample') == 0.5, 'unmatchedRequestPortion'][0.5,:,:,:].unstack(level=-2)['Solo'].unstack(level=-2)[True].unstack(level=-2)
tempNoWheelchair = skimsByDisabilityAndTaz.loc[skimsByDisabilityAndTaz.index.get_level_values('disabilitySample') == 0.5, 'unmatchedRequestPortion'][0.5,:,:,:].unstack(level=-2)['Solo'].unstack(level=-2)[False].unstack(level=-2)

ax = taz.merge(tempNoWheelchair, left_on='taz1454', right_index=True).plot(column=1.0, legend=True, vmin=0.0, vmax=0.4)
ax.set_ylim((37.2,38.5))
ax.set_xlim((-123.0,-121.6))
ax.get_figure().set_figheight(8)
ax.get_figure().set_figwidth(8)
ax.set_title('Solo non-wheelchair denied rides, 100% accessible vehicles')
plt.savefig('out/disability/solo-denied-rides-nowheelchair-100.png')

ax = taz.merge(tempWheelchair, left_on='taz1454', right_index=True).plot(column=1.0, legend=True, vmin=0.0, vmax=0.4)
ax.set_ylim((37.2,38.5))
ax.set_xlim((-123.0,-121.6))
ax.get_figure().set_figheight(8)
ax.get_figure().set_figwidth(8)
ax.set_title('Solo wheelchair denied rides, 100% accessible vehicles')
plt.savefig('out/disability/solo-denied-rides-wheelchair-100.png')

ax = taz.merge(tempNoWheelchair, left_on='taz1454', right_index=True).plot(column=0.05, legend=True, vmin=0.0, vmax=0.4)
ax.set_ylim((37.2,38.5))
ax.set_xlim((-123.0,-121.6))
ax.get_figure().set_figheight(8)
ax.get_figure().set_figwidth(8)
ax.set_title('Solo non-wheelchair denied rides, 5% accessible vehicles')
plt.savefig('out/disability/solo-denied-rides-nowheelchair-5.png')

ax = taz.merge(tempWheelchair, left_on='taz1454', right_index=True).plot(column=0.05, legend=True, vmin=0.0, vmax=0.4)
ax.set_ylim((37.2,38.5))
ax.set_xlim((-123.0,-121.6))
ax.get_figure().set_figheight(8)
ax.get_figure().set_figwidth(8)
ax.set_title('Solo wheelchair denied rides, 5% accessible vehicles')
plt.savefig('out/disability/solo-denied-rides-wheelchair-5.png')

ax = taz.merge(tempNoWheelchair, left_on='taz1454', right_index=True).plot(column=0.2, legend=True, vmin=0.0, vmax=0.4)
ax.set_ylim((37.2,38.5))
ax.set_xlim((-123.0,-121.6))
ax.get_figure().set_figheight(8)
ax.get_figure().set_figwidth(8)
ax.set_title('Solo non-wheelchair denied rides, 20% accessible vehicles')
plt.savefig('out/disability/solo-denied-rides-nowheelchair-20.png')

ax = taz.merge(tempWheelchair, left_on='taz1454', right_index=True).plot(column=0.2, legend=True, vmin=0.0, vmax=0.4)
ax.set_ylim((37.2,38.5))
ax.set_xlim((-123.0,-121.6))
ax.get_figure().set_figheight(8)
ax.get_figure().set_figwidth(8)
ax.set_title('Solo wheelchair denied rides, 20% accessible vehicles')
plt.savefig('out/disability/solo-denied-rides-wheelchair-20.png')