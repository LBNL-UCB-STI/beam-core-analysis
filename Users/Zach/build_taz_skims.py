import dask.dataframe as dd
import pandas as pd


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


mapping_types = {'GEOID': str,
                 'zone_id': str
                 }
mapping = pd.read_csv('out/geoid_to_zone.csv', dtype=mapping_types)
mapping['BGID'] = mapping.GEOID.str[:-3]

skims = dd.read_csv('scenario/skims/result_skims-sfbay-*.csv', usecols=['timePeriod', 'pathType', 'origin', 'destination', 'TIME_minutes',
       'TOTIVT_IVT_minutes', 'VTOLL_FAR', 'DIST_meters', 'WACC_minutes',
       'WAUX_minutes', 'WEGR_minutes', 'DTIM_minutes', 'DDIST_meters',
       'KEYIVT_minutes', 'FERRYIVT_minutes', 'BOARDS', 'WeightedCost'], dtype=beam_skims_types)
for tp in ['EA', 'AM', 'MD', 'PM', 'EV']:
       out = skims.loc[skims.timePeriod == tp, :].merge(mapping[['BGID','zone_id']], left_on = 'origin', right_on='BGID',suffixes=(None, '_origin')).rename(columns={'zone_id':'origin_taz'})
       out = out.merge(mapping[['BGID','zone_id']], left_on = 'destination', right_on='BGID',suffixes=(None, '_destination')).rename(columns={'zone_id':'destination_taz'}).drop(columns=['BGID', 'BGID_destination','origin','destination'])
       out.groupby(['timePeriod','origin_taz','destination_taz']).agg( {'TIME_minutes':'mean', 'TOTIVT_IVT_minutes':'mean', 'VTOLL_FAR':'mean',
            'DIST_meters':'mean',
            'WACC_minutes':'mean',
            'WAUX_minutes':'mean',
            'WEGR_minutes':'mean',
            'DTIM_minutes':'mean',
            'DDIST_meters':'mean',
            'KEYIVT_minutes':'mean',
            'BOARDS':'mean'}).to_csv('out/newskims-'+tp+'-*.csv')