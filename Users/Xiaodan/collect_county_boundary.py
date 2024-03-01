#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 10:51:47 2024

@author: xiaodanxu
"""

from pygris import counties
import geopandas as gpd
import pandas as pd
import os

region_code = 'Seattle'
os.chdir('/Users/xiaodanxu/Documents/SynthFirm.nosync/Inputs_' + region_code)

analysis_year = 2018
selected_state = 'WA'
output_file = region_code + '_counties.geojson'
# define fips code for selected counties

fips_code = ['061', '033','035', '053']
# selected Snohomish, King, Kitsap, Pierce counties
state_counties = counties(state = selected_state, year = analysis_year)
selected_counties = state_counties.loc[state_counties['COUNTYFP'].isin(fips_code)]


selected_counties.to_file(output_file, driver="GeoJSON")

