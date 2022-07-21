#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 08:21:17 2022

@author: zaneedell
"""
import pandas as pd
import numpy as np
net = pd.read_csv('data/network.csv.gz')


#%%
def getSpeeds(path, net):
    ls = pd.read_csv(path)
    ls = ls.merge(net, left_on='link', right_on='linkId', how='left')
    ls['vmt'] = ls['volume'] * ls['length'] / 1609.34
    ls['vht'] = ls['volume'] * ls['traveltime'] / 3600
    ls['vol_cap'] = ls['volume'] / ls['capacity']
    ls['max_prod'] = ls['length'] * ls['capacity'] / 1609.34
    lsGrouped = ls.groupby(['hour', 'attributeOrigType']).agg({'vmt':sum,'vht':sum, 'max_prod':sum, 'vol_cap':np.median, 'length':sum})
    lsGrouped['mph'] = lsGrouped['vmt'] / lsGrouped['vht']
    lsGrouped['vol_cap2'] = lsGrouped['vmt'] / lsGrouped['max_prod']
    lsGrouped['density'] = lsGrouped['vmt'] / lsGrouped['length']
    return lsGrouped
    
out = {}
# aws = "http://ec2-18-224-96-83.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-JDEQSim__2022-03-09_04-02-37_kzy/ITERS/it.{0}/{0}.linkstats.csv.gz"
# aws = "http://ec2-18-116-241-216.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-JDEQSim__2022-03-09_18-36-13_vqn/ITERS/it.{0}/{0}.linkstats.csv.gz"
# aws = "http://ec2-18-191-173-45.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-JDEQSim__2022-03-09_18-36-34_rkd/ITERS/it.{0}/{0}.linkstats.csv.gz"
#JDEQ -0.15
#aws = "http://ec2-18-191-67-239.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-JDEQSim-15__2022-03-10_23-07-13_jhk/ITERS/it.{0}/{0}.linkstats.csv.gz"
#JDEQ -0.14
# aws = "http://ec2-18-221-25-187.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-JDEQSim-14__2022-03-10_17-13-40_mje/ITERS/it.{0}/{0}.linkstats.csv.gz"

#JDEQ -0.15 warmstart
#aws = "http://ec2-52-15-67-159.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-JDEQSim-15__2022-03-11_20-11-09_fqv/ITERS/it.{0}/{0}.linkstats.csv.gz"


#BPR -12 oldmap
# aws = "http://ec2-18-191-255-2.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-PARBPRSim-oldmap-12__2022-03-10_21-27-25_yer/ITERS/it.{0}/{0}.linkstats.csv.gz"

# aws = "http://ec2-18-216-146-126.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-JDEQSim__2022-03-08_21-39-36_jvm/ITERS/it.{0}/{0}.linkstats.csv.gz"
#aws = "http://ec2-18-191-169-158.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-ParBPRSim__2022-03-08_01-14-20_buo/ITERS/it.{0}/{0}.linkstats.csv.gz"
#aws = "http://ec2-3-144-44-112.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-JDEQSim__2022-03-08_18-11-50_xbj/ITERS/it.{0}/{0}.linkstats.csv.gz"

# PILATES
# aws = "https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-2018-base-20220313/beam/year-{0}-iteration-{1}/ITERS/it.0/0.linkstats.csv.gz"

# JDEQ 0.15 adjusted max speed
#aws = "http://ec2-3-141-8-105.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-JDEQSim-15__2022-03-15_18-21-58_wmx/ITERS/it.{0}/{0}.linkstats.csv.gz"

#BPRSIM -0.1
#aws = 'http://ec2-3-16-129-134.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-PARBPRSim-oldmap-10__2022-03-15_16-33-38_igb/ITERS/it.{0}/{0}.linkstats.csv.gz'


# PILATES 2
#aws = "https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-2018-base-snappedToLink-20220321/beam/year-{0}-iteration-{1}/ITERS/it.0/0.linkstats.csv.gz"
#https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-2018-base-snappedToLink-20220321/beam/year-2018-iteration-0/ITERS/it.0/0.linkstats.csv.gz
#aws = "https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-2018-bprsim-20220321/beam/year-{0}-iteration-{1}/ITERS/it.0/0.linkstats.csv.gz"
#https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-2018-bprsim-20220321/beam/year-2018-iteration-0/ITERS/it.0/0.linkstats.csv.gz

#JDEQ 0.17-speedlimits
# aws = "http://ec2-18-117-226-198.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-JDEQSim-15__2022-03-16_18-32-48_ymj/ITERS/it.{0}/{0}.linkstats.csv.gz"
aws = "http://ec2-18-191-163-136.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-PARBPRSim-oldmap-07__2022-06-14_22-34-54_ixb/ITERS/it.{0}/{0}.linkstats.csv.gz"
#BPRSIM -0.09
#aws = 'http://ec2-3-15-159-238.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-PARBPRSim-oldmap-09__2022-03-16_18-32-49_vif/ITERS/it.{0}/{0}.linkstats.csv.gz'


for ii in range(0,16,1):
    path = aws.format(ii)
    out[ii] = getSpeeds(path, net)

# for yr in range(2018, 2022):
#     for it in range(7):
#         path = aws.format(yr, it)
#         out[(yr, it)] = getSpeeds(path, net)


outJDEQ = pd.concat(out)
outJDEQ.to_csv('data/JDEQ-20iters-0.17-links-NEW.csv')

#%%
gb = outJDEQ.groupby(level=[0,2]).agg(sum)
gb['mph'] = gb['vmt'] / gb['vht']
spd = gb['mph'].unstack()


#%%
from shapely.geometry import Point, LineString
import contextily as ctx
import geopandas as gpd
# ls = pd.read_csv('http://ec2-3-129-148-87.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-JDEQSim-14__2022-03-10_23-06-57_lqm/ITERS/it.10/10.linkstats.csv.gz')

#%%
ls = pd.read_csv(path)
ls = ls.merge(net, left_on='link', right_on='linkId', how='left')

def getGeometry(df):
    geometry = df.apply(lambda x: LineString([Point(x.fromLocationX, x.fromLocationY), Point(x.toLocationX, x.toLocationY)]), axis=1)
    return geometry

def getPoint(df, x, y):
    geometry = df.apply(lambda row: Point(row[x], row[y]), axis=1)
    return geometry

subls = ls.loc[ls.hour==6]
subls['geometry'] = getGeometry(subls)

gdf = gpd.GeoDataFrame(subls, geometry='geometry', crs="EPSG:26910")
gdf['spd'] = gdf['length']/gdf['traveltime']
gdf.to_crs('epsg:3857', inplace=True)