import cvxpy as cp
import numpy as np
import pandas as pd

scenario = "base"

hh = pd.read_csv(
    'https://github.com/LBNL-UCB-STI/beam-data-newyork/raw/update-calibration/urbansim_v2/13122k-NYC-all-ages/households.csv.gz')
per = pd.read_csv(
    'https://github.com/LBNL-UCB-STI/beam-data-newyork/raw/update-calibration/urbansim_v2/13122k-NYC-all-ages/persons.csv.gz')
per = per.merge(hh[['household_id', 'block_id']], on='household_id')

for ii in range(10):
    popChunk = str(ii)

    reindexed = pd.read_parquet("data/nyc-reindexed-{0}.parquet".format(popChunk))
    meanRidership = pd.read_csv("data/nyc-meanRidership.{0}.csv".format(popChunk), index_col=["TPERIOD", "STATION"])

    urbansimPath = "https://github.com/LBNL-UCB-STI/beam-data-newyork/raw/update-calibration/urbansim_v2/13122k-NYC-no-kids-sample-{0}-of-10/{1}.csv.gz"

    hh_sample = pd.read_csv(urbansimPath.format(popChunk, "households"))
    per_sample = pd.read_csv(urbansimPath.format(popChunk, "persons"))
    per_sample = per_sample.merge(hh_sample[['household_id', 'block_id']], on='household_id')
    per_sample.set_index('person_id', inplace=True)

    personidToBlockGroup = per_sample.loc[reindexed.index.values, ['block_id']].reset_index().groupby(
        ['person_id', 'block_id']).agg(
        lambda x: True).unstack(fill_value=False)

    kids_by_block_group = per.loc[(per.age <= 18) & (per.age >= 8), :].groupby('block_id').agg(
        {'person_id': len}).reindex(
        personidToBlockGroup.columns).fillna(0)

    print('stop')
    nPersons = reindexed['12AM-6AM'].shape[0]
    nStops = reindexed['12AM-6AM'].shape[1]

    A = reindexed.values
    b = meanRidership['STUDENT'].values / 10

    x = cp.Variable(nPersons)
    objective = cp.Minimize(cp.sum_squares(x @ A - b))
    constraints = [
        x >= 0,
        x @ personidToBlockGroup.values <= np.squeeze(kids_by_block_group.values) / 10.0
    ]
    prob = cp.Problem(objective, constraints)
    prob.solve(verbose=True)

    approx = np.random.poisson(np.clip(x.value, 0, None))

    agentsToDuplicate = pd.DataFrame(approx, index=reindexed.index, columns=["toDuplicate"])
    agentsToDuplicate = agentsToDuplicate.loc[agentsToDuplicate.toDuplicate > 0]

    per.set_index(['block_id', 'person_id'], inplace=True)
    kids = per.loc[(per.age <= 18) & (per.age >= 8), :]

    copiedKids = []
    copiedAdults = []

    for block_id, agentsToCopy in agentsToDuplicate.merge(per_sample, left_index=True, right_index=True).groupby(
            'block_id'):
        copiedKids.append(kids.loc[block_id].sample(agentsToCopy.toDuplicate.sum()))
        copiedAdults.append(
            agentsToCopy.loc[agentsToCopy.index.repeat(agentsToCopy.toDuplicate)].reset_index()['index']._set_name(
                "person_id"))

    copiedKids = pd.concat(copiedKids)
    copiedKids['adultPersonIdToCopy'] = pd.concat(copiedAdults).values
    copiedKids.to_csv('data/nyc-kids-{0}-{1}.csv'.format(scenario, popChunk))
    print('done')
