# Adding the block group information
block_info = pd.read_csv('bg_w_geog_labels.csv')

# Census block groups should have 12 digits so adding 0 to the start of it to be compatible with our block group ids
block_info['bgid'] = '0' + block_info['bgid'].astype(str)

eventsSF = pd.merge(eventsSF, block_info,  how='left',  left_on = ['BlockGroupEnd'], right_on = 'bgid',)
eventsSF = pd.merge(eventsSF, block_info,  how='left',  left_on = ['BlockGroupStart'], right_on = 'bgid',)

eventsSF.rename(columns={"bgid_x":"bgid_end"}, inplace=True) 
eventsSF.rename(columns={"bgid_y":"bgid_start"}, inplace=True) 
eventsSF.rename(columns={"tractid_x":"tractid_end"}, inplace=True)
eventsSF.rename(columns={"tractid_y":"tractid_start"}, inplace=True) 
eventsSF.rename(columns={"juris_name_x":"juris_name_end"}, inplace=True)
eventsSF.rename(columns={"juris_name_y":"juris_name_start"}, inplace=True)
eventsSF,rename(columns={"county_name_x":"county_name_end"}, inplace=True)
eventsSF.rename(columns={"county_name_y":"county_name_start"}, inplace=True)
eventsSF.rename(columns={"mpo_x":"mpo_end"}, inplace=True)
eventsSF.rename(columns={"mpo_y":"mpo_start"}, inplace=True)