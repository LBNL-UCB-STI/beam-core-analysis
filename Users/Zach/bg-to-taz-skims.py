import geopandas as gpd

bg = gpd.read_file('/Users/zaneedell/Desktop/git/beam-core-analysis/Users/Zach/scenario/sfbay-blockgroups-2010.zip')

taz = gpd.read_file('/Users/zaneedell/Desktop/git/beam-core-analysis/Users/Zach/scenario/taz/joinedTAZs.shp')

bg['bg_centroid'] = bg.geometry.to_crs('epsg:26910').centroid.to_crs('epsg:4326')

bg.set_geometry('bg_centroid', inplace=True)

gpd.sjoin(bg[['blkgrpid','bg_centroid']], taz[['taz1454','geometry']], predicate='intersects', how='left').to_csv('/Users/zaneedell/Desktop/git/beam-core-analysis/Users/Zach/out/bg-to-taz.csv')

#%%

beam_skims_types = {'timePeriod': str,
                    'pathType': str,
                    'origin': str,
                    'destination': str,
                    'TIME_minutes': float,
                    'TOTIVT_IVT_minutes': float,
                    'VTOLL_FAR': float,
                    'DIST_meters': float,
                    'WACC_minutes': float,
                    'WAUX_minutes': float,
                    'WEGR_minutes': float,
                    'DTIM_minutes': float,
                    'DDIST_meters': float,
                    'KEYIVT_minutes': float,
                    'FERRYIVT_minutes': float,
                    'BOARDS': float
                    }


mapping_types = {'blkgrpid': str,
                 'taz1454': str
                 }
mapping = pd.read_csv('/Users/zaneedell/Desktop/git/beam-core-analysis/Users/Zach/out/bg-to-taz.csv', dtype=mapping_types)

skims = dd.read_csv('scenario/skims/result_skims-sfbay-00.csv', usecols=['timePeriod', 'pathType', 'origin', 'destination', 'TIME_minutes',
       'TOTIVT_IVT_minutes', 'VTOLL_FAR', 'DIST_meters', 'WACC_minutes',
       'WAUX_minutes', 'WEGR_minutes', 'DTIM_minutes', 'DDIST_meters',
       'KEYIVT_minutes', 'FERRYIVT_minutes', 'BOARDS', 'WeightedCost'], dtype=beam_skims_types)
out = skims.merge(mapping[['blkgrpid','taz1454']], left_on = 'origin', right_on='blkgrpid',suffixes=(None, '_origin')).rename(columns={'taz1454':'origin_taz'})
out = out.merge(mapping[['blkgrpid','taz1454']], left_on = 'destination', right_on='blkgrpid',suffixes=(None, '_destination')).rename(columns={'taz1454':'destination_taz'}).drop(columns=['blkgrpid', 'blkgrpid_destination','origin','destination'])
final = out.groupby(['timePeriod','origin_taz','destination_taz']).agg(
    {'TIME_minutes':'mean',
     'TOTIVT_IVT_minutes':'mean',
     'VTOLL_FAR':'mean',
     'DIST_meters':'mean',
     'WACC_minutes':'mean',
     'WAUX_minutes':'mean',
     'WEGR_minutes':'mean',
     'DTIM_minutes':'mean',
     'DDIST_meters':'mean',
     'KEYIVT_minutes':'mean',
     'BOARDS':'mean',
     })