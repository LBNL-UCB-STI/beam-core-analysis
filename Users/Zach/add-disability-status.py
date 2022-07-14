import pandas as pd
import numpy as np
import geopandas as gpd
import h5py
# import boto.s3
import glob
# import boto3
from zipfile import ZipFile

filename = "data/pipeline-sfbay-baseline.h5"

persons = pd.read_hdf(filename, '/persons/trip_mode_choice')
households = pd.read_hdf(filename, '/households/trip_mode_choice')
hhpums = pd.read_csv('data/ss13hca.csv')
perpums = pd.read_csv('data/ss13pca.csv')

per2 = pd.read_csv('https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-2018-baseline-20220704/activitysim/final_persons.csv')
hh2 = pd.read_csv('https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-2018-baseline-20220704/activitysim/final_households.csv')

perpums = perpums.sort_values(by=['SERIALNO']).reset_index()
hhpums = hhpums.sort_values(by=['SERIALNO']).reset_index()
hhpersons_PUMS2010 = pd.merge(left=perpums, right=hhpums, how='left', on='SERIALNO')

per2 = per2.sort_values(by=['household_id']).reset_index(drop=True).drop(columns=['TAZ'])
hh2 = hh2.sort_values(by=['household_id']).reset_index(drop=True)
hhpersons = pd.merge(left=per2, right=hh2, how='left', on='household_id')

# Merge Disability Columns
hhpersons_PUMS2010 = hhpersons_PUMS2010.sort_values(by=['SERIALNO', 'SPORDER']).reset_index(drop=True)
hhpersons = hhpersons.sort_values(by=['serialno', 'PNUM']).reset_index(drop=True)
hhpersonsDIS = pd.merge(hhpersons, hhpersons_PUMS2010[['SERIALNO', 'SPORDER', 'AGEP', 'SEX', 'DIS', 'HINCP', 'VEH', 'JWMNP', 'JWRIP', 'JWTR', 'RAC1P', 'RAC2P05']], how='left',left_on = ['serialno', 'PNUM'] , right_on=['SERIALNO', 'SPORDER'])

hhpersonsDIS[hh2.columns].groupby('household_id').agg('first').to_csv('disability/households.csv.gz')
hhpersonsDIS['in_wheelchair'] = hhpersonsDIS['DIS'] == 2
per_100 = hhpersonsDIS[list(per2.columns) + ['in_wheelchair']]



def downsamplePersons(persons, fractionToKeep):
    dis_idx = np.where(persons['in_wheelchair'] == 1)[0]
    persons_out = persons.copy()
    numberToRemove = int(len(dis_idx) * (1.0 - fractionToKeep))
    idx_to_remove = np.random.choice(dis_idx, numberToRemove, replace=False)
    persons_out.iloc[idx_to_remove, persons_out.columns.get_loc('in_wheelchair')] = False
    return persons_out

per_100.to_csv('disability/persons_100pct.csv.gz')
downsamplePersons(per_100, 0.5).to_csv('disability/persons_50pct.csv.gz')
downsamplePersons(per_100, 0.2).to_csv('disability/persons_20pct.csv.gz')
downsamplePersons(per_100, 0.05).to_csv('disability/persons_5pct.csv.gz')


print('done')