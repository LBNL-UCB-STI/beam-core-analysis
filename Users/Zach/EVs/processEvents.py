#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 09:37:01 2022

@author: zaneedell
"""
import pandas as pd
import geopandas as gpd


#%%


def processEvents(path):
    PTs = []
    RFs = []
    for chunk in pd.read_csv(path, chunksize=10000000):
        PTs.append(chunk.loc[(chunk["type"] == "PathTraversal") & 
                             (chunk["mode"] == "car"), :].dropna(
                                 how='all', axis=1))
        RFs.append(chunk.loc[(chunk["type"] == "RefuelSessionEvent"), :].dropna(
                                 how='all', axis=1))
    return pd.concat(PTs), pd.concat(RFs)

def processEventsModin(path):
    events =  pd.read_csv(path)
    PTs = events.loc[(events["type"] == "PathTraversal") & (events["mode"] == "car"), :].dropna(
            how='all', axis=1)
    RFs = events.loc[(chunk["type"] == "RefuelSessionEvent"), :].dropna(how='all', axis=1)
    return pd.concat(PTs), pd.concat(RFs)
        
#%%
if __name__ == '__main__':
    PTs, RefuelSessions = processEvents("events/events.sfbay.csv.gz")