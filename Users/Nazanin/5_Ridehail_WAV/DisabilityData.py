import pandas as pd
import numpy as np
import geopandas as gpd
import h5py
import boto.s3
import glob
import boto3
from zipfile import ZipFile

actloc_2018_baseline = "https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-base-20220409/activitysim/"

households = pd.read_csv(actloc_2018_baseline + 'final_households.csv')
persons = pd.read_csv(actloc_2018_baseline + 'final_persons.csv')
tours = pd.read_csv(actloc_2018_baseline +'final_tours.csv')
plans = pd.read_csv(actloc_2018_baseline +'final_plans.csv')
trips = pd.read_csv(actloc_2018_baseline + 'final_trips.csv')
landuse = pd.read_csv(actloc_2018_baseline + 'final_land_use.csv')

# PUMS data for Disability information
filename = "C:/Shared-Work/Data/Disability_PUMS/custom_mpo_06197001_model_data.h5"

with h5py.File(filename, "r") as f:
    # List all groups
    print("Keys: %s" % f.keys())
    a_group_key = list(f.keys())[0]

    # Get the data
    data = list(f[a_group_key])

# PUMS data for Disability information
person_5_year_2010 = pd.read_csv('C:/Users/nazanin/Downloads/csv_pca/ss13pca.csv')
housing_unit_5_year_2010 = pd.read_csv('C:/Users/nazanin/Downloads/csv_hca/ss13hca.csv')

# Merge PUMS households and persons 
person_5_year_2010 = person_5_year_2010.sort_values(by=['SERIALNO']).reset_index()
housing_unit_5_year_2010 = housing_unit_5_year_2010.sort_values(by=['SERIALNO']).reset_index()
hhpersons_PUMS2010 = pd.merge(left=person_5_year_2010, right=housing_unit_5_year_2010, how='left', on='SERIALNO')

# Merge BEAM households and persons 
persons = persons.sort_values(by=['household_id']).reset_index(drop=True)
households = households.sort_values(by=['household_id']).reset_index(drop=True)
hhpersons = pd.merge(left=persons, right=households, how='left', on='household_id')

# Merge Disability Columns
hhpersons_PUMS2010 = hhpersons_PUMS2010.sort_values(by=['SERIALNO', 'SPORDER']).reset_index(drop=True)
hhpersons = hhpersons.sort_values(by=['serialno', 'PNUM']).reset_index(drop=True)
hhpersonsDIS = pd.merge(hhpersons, hhpersons_PUMS2010[['SERIALNO', 'SPORDER', 'AGEP', 'SEX', 'DIS', 'HINCP', 'VEH', 'JWMNP', 'JWRIP', 'JWTR', 'RAC1P', 'RAC2P05']], how='left',left_on = ['serialno', 'PNUM'] , right_on=['SERIALNO', 'SPORDER'])