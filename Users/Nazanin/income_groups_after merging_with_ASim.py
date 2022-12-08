
# Add a column of income quartiles
quartiles = eventsASim['income'].quantile([0,.25, .5, .75,1]).tolist()
# Add income deciles
conditions  = [(eventsASim['income'] >= quartiles[0]) & (eventsASim['income'] < quartiles[1]), 
               (eventsASim['income'] >= quartiles[1]) & (eventsASim['income'] < quartiles[2]),
               (eventsASim['income'] >=  quartiles[2]) & (eventsASim['income'] < quartiles[3]),
               (eventsASim['income'] >= quartiles[3]) & (eventsASim['income'] <= quartiles[4])]

choices = [ '1stQ', '2ndQ', '3rdQ', '4thD']
eventsASim['income_quartiles'] = np.select(conditions, choices, default=None)
# Add a column of income deciles
deciles = eventsASim['income'].quantile([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]).tolist()
# Add income deciles
conditions  = [(eventsASim['income'] >= deciles[0]) & (eventsASim['income'] < deciles[1]), 
               (eventsASim['income'] >= deciles[1]) & (eventsASim['income'] < deciles[2]),
               (eventsASim['income'] >=  deciles[2]) & (eventsASim['income'] < deciles[3]),
               (eventsASim['income'] >= deciles[3]) & (eventsASim['income'] < deciles[4]), 
               (eventsASim['income'] >=  deciles[4]) & (eventsASim['income'] < deciles[5]),
               (eventsASim['income'] >=  deciles[5]) & (eventsASim['income'] < deciles[6]),
               (eventsASim['income'] >=  deciles[6]) & (eventsASim['income'] < deciles[7]),
               (eventsASim['income'] >=  deciles[7]) & (eventsASim['income'] < deciles[8]),
               (eventsASim['income'] >=  deciles[8]) & (eventsASim['income'] < deciles[9]),
               (eventsASim['income'] >=  deciles[9]) & (eventsASim['income'] <= deciles[10])]

choices = [ '1stD', '2ndD', '3rdD', 
           '4thD', '5thD', '6thD', '7thD', '8thD', '9thD','10thD']

eventsASim['income_deciles'] = np.select(conditions, choices, default=None)