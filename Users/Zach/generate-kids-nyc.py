import cvxpy as cp
import numpy as np
import pandas as pd


def solve(popChunkInt, scenario, per):
    popChunk = str(popChunkInt)

    print("Loading data for chunk {0}".format(popChunk))
    reindexed = pd.read_parquet('data/nyc-reindexed-{0}-{1}.parquet'.format(scenario, popChunk))
    meanRidership = pd.read_csv('data/nyc-meanRidership-{0}.csv'.format(scenario), index_col=["TPERIOD", "STATION"])

    urbansimPath = "https://github.com/LBNL-UCB-STI/beam-data-newyork/raw/update-calibration/urbansim_v2/13122k-NYC-no-kids-sample-{0}-of-10/{1}.csv.gz"
    
    hh_sample = pd.read_csv(urbansimPath.format(popChunk, "households"))
    per_sample = pd.read_csv(urbansimPath.format(popChunk, "persons"))
    per_sample = per_sample.merge(hh_sample[['household_id', 'block_id']], on='household_id').reset_index()
    per_sample.set_index(['block_id','person_id'], inplace=True)

    personAndBlockGroup = per_sample.index.to_frame().set_index('person_id')

    personidToBlockGroup = personAndBlockGroup.loc[reindexed.index.values, ['block_id']].reset_index().groupby(
        ['person_id', 'block_id']).agg(
        lambda x: True).unstack(fill_value=False)

    kids_by_block_group = per.loc[(per.age <= 16) & (per.age >= 8), :].groupby('block_id').agg(
            {'household_id': len}).reindex(
        personidToBlockGroup.columns).fillna(0)

    nPersons = reindexed['12AM-6AM'].shape[0]
    nStops = reindexed['12AM-6AM'].shape[1]

    A = reindexed.values
    b = meanRidership['STUDENT'].values / 10

    x = cp.Variable(nPersons)
    objective = cp.Minimize(cp.sum_squares(x @ A - b) + 5 * cp.sum(x))
    constraints = [
        x >= 0,
        x <= 2,
        x @ personidToBlockGroup.values <= np.squeeze(kids_by_block_group.values) / 12.0
    ]
    prob = cp.Problem(objective, constraints)
    prob.solve(verbose=False)
    print(vars(prob.solver_stats))

    approx = np.floor(x.value) + np.random.binomial(1, x.value % 1.0)


    agentsToDuplicate = pd.DataFrame(approx, index=reindexed.index, columns=["toDuplicate"])
    agentsToDuplicate = agentsToDuplicate.loc[agentsToDuplicate.toDuplicate > 0]

    print("Sampling agents for {0} kids in chunk {1}".format(agentsToDuplicate.shape, popChunk))

    kids = per.loc[(per.age <= 16) & (per.age >= 8) & (per.household_id.isin(per_sample.household_id.unique())), :]

    copiedKids = []
    copiedAdults = []

    totalKids = 0
    droppedKids = 0

    #for block_id, agentsToCopy in agentsToDuplicate.merge(per_sample, left_index=True, right_index=True).groupby(
    #        'block_id'):
    for block_id, agentsToCopy in agentsToDuplicate.merge(per_sample.reset_index(), left_index=True, right_on='person_id').groupby(
            'block_id'):
        totalKids += agentsToCopy.toDuplicate.sum()
        if block_id in kids.index.get_level_values(0):
            if agentsToCopy.toDuplicate.sum() > len(kids.loc[block_id]):
                copiedKids.append(kids.loc[block_id])
                #print("Kids in block: {0}, kids to sample {1}".format(len(kids.loc[block_id]), agentsToCopy.toDuplicate.sum()))
                copiedAdults.append(
                    agentsToCopy.loc[agentsToCopy.index.repeat(agentsToCopy.toDuplicate)]['person_id']._set_name(
                        "person_id").iloc[:len(kids.loc[block_id])])
                droppedKids += (agentsToCopy.toDuplicate.sum() - len(kids.loc[block_id]))
            else:
                copiedKids.append(kids.loc[block_id].sample(int(agentsToCopy.toDuplicate.sum())))
                copiedAdults.append(
                    agentsToCopy.loc[agentsToCopy.index.repeat(agentsToCopy.toDuplicate)]['person_id']._set_name(
                        "person_id"))
        else:
            # print("Dropping {0} kids from bg {1}".format(agentsToCopy.toDuplicate.sum(), block_id))
            droppedKids += agentsToCopy.toDuplicate.sum()

    print("Lost {0} out of a total of {1} kids in sampling".format(droppedKids, totalKids))

    copiedKids = pd.concat(copiedKids)
    copiedKids['adultPersonIdToCopy'] = pd.concat(copiedAdults).values
    copiedKids.to_csv('data/nyc-kids-{0}-{1}.csv'.format(scenario, popChunk))
    print("Saving data for chunk {0}".format(popChunk))
    return copiedKids


scenario = "base"
print("Loading urbansim data")
hh = pd.read_csv('households.csv.gz')
per = pd.read_csv('persons.csv.gz')
per = per.merge(hh[['household_id', 'block_id']], on='household_id')
per.set_index(['block_id', 'person_id'], inplace=True)

per.set_index(['block_id', 'person_id'], inplace=True)

print("Starting workers")
allKids = [solve(ii, scenario, per) for ii in range(10)]

pd.concat(allKids).to_csv('data/nyc-kids-{0}.csv'.format(scenario))

