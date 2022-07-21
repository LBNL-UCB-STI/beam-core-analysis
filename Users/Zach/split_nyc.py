import pandas as pd
import os

per_full = pd.read_csv('../../../beam/production/newyork/urbansim_v2/13122k-NYC-no-kids/persons.csv.gz')
hh_full = pd.read_csv('../../../beam/production/newyork/urbansim_v2/13122k-NYC-no-kids/households.csv.gz')
plans_full = pd.read_csv('../../../beam/production/newyork/urbansim_v2/13122k-NYC-no-kids/plans.csv.gz')


hh_full = hh_full.sample(frac=1).reset_index(drop=True)

nChunks = 10

for i in range(nChunks):
    path = '../../../beam/production/newyork/urbansim_v2/13122k-NYC-no-kids-sample-{0}-of-{1}'.format(i, nChunks)
    os.mkdir(path)
    sample = (hh_full.index % nChunks == i)
    hh_out = hh_full.loc[sample].reset_index(drop=True)
    per_out = per_full.loc[per_full.household_id.isin(hh_out.household_id)].reset_index(drop=True)
    plans_out = plans_full.loc[plans_full.person_id.isin(per_out.person_id)].reset_index(drop=True)
    hh_out.to_csv(os.path.join(path, 'households.csv.gz'), index=False)
    per_out.to_csv(os.path.join(path, 'persons.csv.gz'), index=False)
    plans_out.to_csv(os.path.join(path, 'plans.csv.gz'), index=False)

print('done')