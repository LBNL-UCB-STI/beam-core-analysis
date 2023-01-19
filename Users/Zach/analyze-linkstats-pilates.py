#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 08:21:17 2022

@author: zaneedell
"""
import itertools

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point, LineString

net = pd.read_csv('data/network.csv.gz')

path = "data/pilates/linkstats-{0}-{1}.csv.gz"
years = range(2018, 2022)
iters = range(0, 6)


# %%
def getSpeeds(path, net):
    ls = pd.read_csv(path)
    ls = ls.merge(net, left_on='link', right_on='linkId', how='left')
    ls['vmt'] = ls['volume'] * ls['length'] / 1609.34
    ls['vht'] = ls['volume'] * ls['traveltime'] / 3600
    ls['vol_cap'] = ls['volume'] / ls['capacity']
    ls['max_prod'] = ls['length'] * ls['capacity'] / 1609.34
    lsGrouped = ls.groupby(['hour', 'attributeOrigType']).agg(
        {'vmt': sum, 'vht': sum, 'max_prod': sum, 'vol_cap': np.median, 'length': sum})
    lsGrouped['mph'] = lsGrouped['vmt'] / lsGrouped['vht']
    lsGrouped['vol_cap2'] = lsGrouped['vmt'] / lsGrouped['max_prod']
    lsGrouped['density'] = lsGrouped['vmt'] / lsGrouped['length']
    lsLink = ls.groupby(['link']).agg(
        {'vmt': sum, 'vht': sum, 'length': 'first'})
    return lsGrouped, lsLink


out = {}
outById = {}
for (yr, it) in itertools.product(years, iters):
    fullpath = path.format(yr, it)
    byType, byID = getSpeeds(fullpath, net)
    out[(yr, it)] = byType
    outById[(yr, it)] = byID

out = pd.concat(out)
outById = pd.concat(outById)
outJDEQ.to_csv('data/JDEQ-20iters-0.17-links-NEW.csv')

# %%
gb = out.groupby(level=[0, 1, 2, 3]).agg(sum)
gb['mph'] = gb['vmt'] / gb['vht']
spd = gb['mph'].unstack()
vmt = gb['vmt'].unstack()

# %%

# ls = pd.read_csv('http://ec2-3-129-148-87.us-east-2.compute.amazonaws.com:8000/output/sfbay/sfbay-pilates-JDEQSim-14__2022-03-10_23-06-57_lqm/ITERS/it.10/10.linkstats.csv.gz')

# %%
ls = pd.read_csv(path)
ls = ls.merge(net, left_on='link', right_on='linkId', how='left')


def getGeometry(df):
    geometry = df.apply(
        lambda x: LineString([Point(x.fromLocationX, x.fromLocationY), Point(x.toLocationX, x.toLocationY)]), axis=1)
    return geometry


def getPoint(df, x, y):
    geometry = df.apply(lambda row: Point(row[x], row[y]), axis=1)
    return geometry


subls = ls.loc[ls.hour == 6]
subls['geometry'] = getGeometry(subls)

gdf = gpd.GeoDataFrame(subls, geometry='geometry', crs="EPSG:26910")
gdf['spd'] = gdf['length'] / gdf['traveltime']
gdf.to_crs('epsg:3857', inplace=True)
