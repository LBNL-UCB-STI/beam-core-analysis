


def mergeSkims(df):
    if len(df) > 1:
        nObservations = df['observations'].sum()
        travelTimeInS = (df['travelTimeInS'] * df['observations']).sum() / nObservations
        generalizedTimeInS = (df['generalizedTimeInS'] * df['observations']).sum() / nObservations
        cost = (df['cost'] * df['observations']).sum() / nObservations
        generalizedCost = (df['generalizedCost'] * df['observations']).sum() / nObservations
        distanceInM = (df['distanceInM'] * df['observations']).sum() / nObservations
        payloadWeightInKg = (df['payloadWeightInKg'] * df['observations']).sum() / nObservations
        energy = (df['energy'] * df['observations']).sum() / nObservations
        crowdingLevel = (df['crowdingLevel'] * df['observations']).sum() / nObservations
        level4CavTravelTimeScalingFactor = (df['level4CavTravelTimeScalingFactor'] * df[
            'observations']).sum() / nObservations
        failedTrips = df['failedTrips'].sum()
        observations = df['observations'].sum()
        iterations = df['iterations'].max()

        out = dd.Series({"nObservations": nObservations,
                         "travelTimeInS": travelTimeInS,
                         "generalizedTimeInS": generalizedTimeInS,
                         "cost": cost,
                         "generalizedCost": generalizedCost,
                         "distanceInM": distanceInM,
                         "payloadWeightInKg": payloadWeightInKg,
                         "energy": energy,
                         "crowdingLevel": crowdingLevel,
                         "level4CavTravelTimeScalingFactor": level4CavTravelTimeScalingFactor,
                         "failedTrips": failedTrips,
                         "observations": observations,
                         "iterations": iterations,
                         })
    else:
        out = df.squeeze()
    return out



import dask.dataframe as dd


df = dd.read_csv('data/nyc-baseline-skims-*-of-10.csv.gz', dtype={'costPerMile': float, 'destTaz': 'object', 'origTaz': 'object'})
# df.origTaz = dd.to_numeric(df['origTaz'], errors='coerce')
# df.destTaz = dd.to_numeric(df['destTaz'], errors='coerce')

df['weightedTravelTime'] = df['travelTimeInS'] * df['observations']
df['weightedGeneralizedTime'] = df['generalizedTimeInS'] * df['observations']
df['weightedCost'] = df['cost'] * df['observations']
df['weightedGeneralizedCost'] = df['generalizedCost'] * df['observations']
df['weightedDistanceInM'] = df['distanceInM'] * df['observations']
df['weightedPayloadWeightInKg'] = df['payloadWeightInKg'] * df['observations']
df['weightedEnergy'] = df['energy'] * df['observations']
df['weightedCrowdingLevel'] = df['crowdingLevel'] * df['observations']
df['weightedLevel4'] = df['level4CavTravelTimeScalingFactor'] * df['observations']


df2 = df.groupby(['hour','mode','origTaz','destTaz']).agg({'weightedTravelTime':'sum',
                                                           'weightedGeneralizedTime':'sum',
                                                           'weightedCost':'sum',
                                                           'weightedGeneralizedCost':'sum',
                                                           'weightedDistanceInM':'sum',
                                                           'weightedPayloadWeightInKg':'sum',
                                                           'weightedEnergy':'sum',
                                                           'weightedCrowdingLevel':'sum',
                                                           'weightedLevel4':'sum',
                                                           'observations':'sum',
                                                           'iterations':'first'})

df2['travelTimeInS'] = df2['weightedTravelTime'] / df2['observations']
df2['generalizedTimeInS'] = df2['weightedGeneralizedTime'] / df2['observations']
df2['cost'] = df2['weightedCost'] / df2['observations']
df2['generalizedCost'] = df2['weightedGeneralizedCost'] / df2['observations']
df2['distanceInM'] = df2['weightedDistanceInM'] / df2['observations']
df2['payloadWeightInKg'] = df2['weightedPayloadWeightInKg'] / df2['observations']
df2['energy'] = df2['weightedEnergy'] / df2['observations']
df2['crowdingLevel'] = df2['weightedCrowdingLevel'] / df2['observations']
df2['level4CavTravelTimeScalingFactor'] = df2['weightedLevel4'] / df2['observations']
out = df2.compute(num_workers=8)
out = out.reset_index()
out = out[['hour', 'mode', 'origTaz', 'destTaz', 'observations', 'iterations',
       'travelTimeInS', 'generalizedTimeInS', 'cost', 'generalizedCost',
       'distanceInM', 'payloadWeightInKg', 'energy', 'crowdingLevel',
       'level4CavTravelTimeScalingFactor']]
# out['destTaz'] = out['destTaz'].astype(pd.Int64Dtype())
# out['origTaz'] = out['origTaz'].astype(pd.Int64Dtype())
out.to_csv('data/nyc-baseline-skims-all.csv.gz')

# old is 9.87 million
