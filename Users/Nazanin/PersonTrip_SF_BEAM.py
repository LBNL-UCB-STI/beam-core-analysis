import pandas as pd
import numpy as np
# File location on S3 (The address should be updated depending on the version of the code using)
loc_2018_baseline = "https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-base-20220409/beam/year-2018-iteration-5/ITERS/it.0/"
# Reading the events file
dtypes = {
    "time": "float32",
    "type": "category",
    "legMode": "category",
    "actType": "category", 
    "primaryFuelLevel": "float64",
    "legMode": "category",
    "chargingPointType":"category",
    "pricingModel":"category",
    "parkingType":"category",
    "mode":"category",
    "personalVehicleAvailable": "category",
    "person": "object",
    "driver": "object",
    "riders": "object"
}
# Use list comprehension to remove the unwanted column in **usecol**
eventsSF = pd.read_csv(loc_2018_baseline + '0.events.csv.gz', compression = 'gzip', dtype = dtypes)
# Rename the "mode" column
eventsSF.rename(columns={"mode":"modeBEAM"}, inplace=True) 
# Replace "Work" with "work" in the "actType" column
eventsSF["actType"].replace({"Work": "work"}, inplace=True)
# Remove person = TransitDriver or RidehailDriver because there are no agent information in these rows
eventsSF = eventsSF[~eventsSF.person.str.contains("Agent", na=False)].reset_index(drop=True)

# Adding the IDMerged Column
eventsSF['UniqueID'] = eventsSF['person'] #make a copy of the person column
eventsSF['personID'] = np.where(eventsSF['person'].isin(eventsSF['driver']), eventsSF['person'], np.nan) 
eventsSF['driverID'] = np.where(eventsSF['driver'].isin(eventsSF['person']), eventsSF['driver'], np.nan)
# Merging person and driver ids in one column
eventsSF['IDMerged'] = eventsSF['personID'].combine_first(eventsSF['driverID'])
eventsSF['IDMerged'] = eventsSF['UniqueID'].combine_first(eventsSF['IDMerged'])
# Dropping unused columns
eventsSF = eventsSF.drop(['personID','driverID','UniqueID'], axis=1) 

# Split the "riders' column and replicated rows for every rider
eventsSF['riders'] = eventsSF['riders'].str.split(':')
eventsSF = eventsSF.explode('riders')
# Combine riderID with IDMerged
eventsSF['riderID'] = np.where(eventsSF['riders'].isin(eventsSF['person']), eventsSF['riders'], np.nan)
eventsSF['IDMerged'] = eventsSF['riderID'].combine_first(eventsSF['IDMerged'])
# Dropping unused columns
eventsSF = eventsSF.drop(['riderID'], axis=1)

# Remove driver = TransitDriver or RidehailDriver for IDMerged = NAN because there are no agent information in these rows 
eventsSF = eventsSF[~((eventsSF.driver.str.contains("Agent", na=False))&(eventsSF.IDMerged.isna()))].reset_index(drop=True)

# Filling NANs in ID related to charging events
eventsSF["chargeID"] = eventsSF.groupby('vehicle')['IDMerged'].transform(lambda x: x.ffill().bfill())
# Combining chargeID with IDMerged so no NANs anymore
eventsSF['IDMerged'] = eventsSF['chargeID'].combine_first(eventsSF['IDMerged'])
# Dropping unused columns
eventsSF = eventsSF.drop(['chargeID'], axis=1) 

# Change the IDMerged column type to numeric
eventsSF["IDMerged"] = pd.to_numeric(eventsSF.IDMerged)

# Sort by IDMerged and time columns
eventsSF = eventsSF.sort_values(['IDMerged','time']).reset_index(drop=True)

# We assume that the number of passengers is 1 for ride_hail_pooled
eventsSF['modeBEAM_rh'] = np.where(eventsSF.driver.str.contains("rideHailAgent", na=False), 'ride_hail' , eventsSF['modeBEAM'])

# Adding teleportation mode to the type = TeleportationEvent row 
eventsSF["modeBEAM_rh"] = np.where(eventsSF['type']=='TeleportationEvent', eventsSF.modeBEAM_rh.fillna(method='ffill'), eventsSF["modeBEAM_rh"])
eventsSF['modeBEAM_rh_pooled'] = np.where((eventsSF['type'] == 'PersonCost') & (eventsSF['modeBEAM'] == 'ride_hail_pooled'), 'ride_hail_pooled', np.nan)
eventsSF['modeBEAM_rh_ride_hail_transit'] = np.where((eventsSF['type'] == 'PersonCost') & (eventsSF['modeBEAM'] == 'ride_hail_transit'), 'ride_hail_transit', np.nan)
eventsSF['modeBEAM_rh_pooled'] = eventsSF['modeBEAM_rh_pooled'].shift(+1)
eventsSF['modeBEAM_rh_ride_hail_transit'] = eventsSF['modeBEAM_rh_ride_hail_transit'].shift(+1)
eventsSF['modeBEAM_rh'] = np.where((eventsSF['type'] == 'PathTraversal') & (eventsSF['modeBEAM'] == 'car') & (eventsSF['driver'].str.contains("rideHailAgent", na=False)) & (eventsSF['modeBEAM_rh_pooled'] != 'nan'), eventsSF['modeBEAM_rh_pooled'], eventsSF['modeBEAM_rh'])
# We don't know if ridehail_transit is ride_hail or ride_hail_pooled
eventsSF['modeBEAM_rh'] = np.where((eventsSF['type'] == 'PathTraversal') & (eventsSF['modeBEAM'] == 'car') & (eventsSF['driver'].str.contains("rideHailAgent", na=False)) & (eventsSF['modeBEAM_rh_ride_hail_transit'] != 'nan'), eventsSF['modeBEAM_rh_ride_hail_transit'], eventsSF['modeBEAM_rh'])
# Dropping the temporary columns
eventsSF = eventsSF.drop(['modeBEAM_rh_pooled'], axis=1)
eventsSF = eventsSF.drop(['modeBEAM_rh_ride_hail_transit'], axis=1)

#Adding new columns
eventsSF['actEndTime'] = np.where(eventsSF['type']=='actend', eventsSF['time'], np.nan)
eventsSF['actStartTime'] = np.where(eventsSF['type']=='actstart', eventsSF['time'], np.nan)
eventsSF['travelTime'] = np.where((eventsSF['type']=='PathTraversal')|(eventsSF['type']=='TeleportationEvent')
                     , eventsSF['arrivalTime'] - eventsSF['departureTime'], np.nan)
eventsSF['travelDistance'] = np.where((eventsSF['type']=='PathTraversal')|((eventsSF['type']=='ModeChoice')&((eventsSF['modeBEAM']=='hov2_teleportation')|(eventsSF['modeBEAM']=='hov3_teleportation'))), eventsSF['length'], np.nan)
eventsSF['length_mode_choice'] = np.where(eventsSF['type']=='ModeChoice', eventsSF['length'], np.nan)
eventsSF['duration_walking'] = np.where(eventsSF['modeBEAM']=='walk', eventsSF['travelTime'], np.nan)
eventsSF['distance_walking'] = np.where(eventsSF['modeBEAM']=='walk', eventsSF['travelDistance'], np.nan)
eventsSF['duration_on_bike'] = np.where(eventsSF['modeBEAM']=='bike', eventsSF['travelTime'], np.nan)
eventsSF['distance_bike'] = np.where(eventsSF['modeBEAM']=='bike', eventsSF['travelDistance'], np.nan)
eventsSF['duration_in_ridehail'] = np.where(eventsSF['modeBEAM_rh']=='ride_hail', eventsSF['travelTime'], np.nan)
eventsSF['distance_ridehail'] = np.where(eventsSF['modeBEAM_rh']=='ride_hail', eventsSF['travelDistance'], np.nan)
eventsSF['duration_in_privateCar'] = np.where((eventsSF['modeBEAM_rh']=='car')|(eventsSF['modeBEAM_rh']=='car_hov3')|(eventsSF['modeBEAM_rh']=='car_hov2')|
                                              (eventsSF['modeBEAM_rh']=='hov2_teleportation')|(eventsSF['modeBEAM_rh']=='hov3_teleportation') 
                                              , eventsSF['travelTime'], np.nan)
eventsSF['distance_privateCar'] = np.where((eventsSF['modeBEAM_rh']=='car')|(eventsSF['modeBEAM_rh']=='car_hov3')|(eventsSF['modeBEAM_rh']=='car_hov2')|
                                              (eventsSF['modeBEAM_rh']=='hov2_teleportation')|(eventsSF['modeBEAM_rh']=='hov3_teleportation'), eventsSF['travelDistance'], np.nan)
eventsSF['duration_in_transit'] = np.where((eventsSF['modeBEAM']=='bike_transit')|(eventsSF['modeBEAM']=='drive_transit')|
                                           (eventsSF['modeBEAM']=='walk_transit')|(eventsSF['modeBEAM']=='bus')|
                                           (eventsSF['modeBEAM']=='tram')|(eventsSF['modeBEAM']=='subway')|
                                           (eventsSF['modeBEAM']=='rail')|(eventsSF['modeBEAM']=='cable_car')|
                                           (eventsSF['modeBEAM']=='ride_hail_transit'), eventsSF['travelTime'], np.nan)
eventsSF['distance_transit'] = np.where((eventsSF['modeBEAM']=='bike_transit')|(eventsSF['modeBEAM']=='drive_transit')|
                                        (eventsSF['modeBEAM']=='walk_transit')|(eventsSF['modeBEAM']=='bus')|
                                        (eventsSF['modeBEAM']=='tram')|(eventsSF['modeBEAM']=='subway')|
                                        (eventsSF['modeBEAM']=='rail')|(eventsSF['modeBEAM']=='cable_car')|
                                        (eventsSF['modeBEAM']=='ride_hail_transit'), eventsSF['travelDistance'], np.nan)
# Removing the extra tour index happening after replanning events
eventsSF['replanningTime'] = np.where(eventsSF['type'] == 'Replanning', eventsSF['time'], np.nan)
eventsSF['replanningTime'] = eventsSF['replanningTime'].shift(+1)
eventsSF['tourIndex_fixed'] = np.where((eventsSF['type'] == 'ModeChoice')&(eventsSF['replanningTime'].notna()), np.nan, eventsSF['tourIndex'])
eventsSF['actEndType'] = np.where(eventsSF['type']=='actend', eventsSF['actType'], "")
eventsSF['actStartType'] = np.where(eventsSF['type']=='actstart', eventsSF['actType'], "")

#TripIndex
eventsSF["tripIndex"] = eventsSF.groupby("IDMerged")["tourIndex_fixed"].rank(method="first", ascending=True)
eventsSF["tripIndex"] = eventsSF.tripIndex.fillna(method='ffill')


# Mode Choice planned and actual
eventsSF['mode_choice_actual_BEAM'] = eventsSF.groupby(['IDMerged','tripIndex', 'type'])['modeBEAM'].transform('last')
eventsSF['mode_choice_planned_BEAM'] = eventsSF.groupby(['IDMerged','tripIndex', 'type'])['modeBEAM'].transform('first')
eventsSF['mode_choice_actual_BEAM'] = np.where(eventsSF['type'] != 'ModeChoice' , np.nan, eventsSF['mode_choice_actual_BEAM'])
eventsSF['mode_choice_planned_BEAM'] = np.where(eventsSF['type'] != 'ModeChoice' , np.nan, eventsSF['mode_choice_planned_BEAM'])

# Rename the "netCost" column
eventsSF.rename(columns={"netCost":"cost_BEAM"}, inplace=True)

# Replanning events = 1, the rest = 0
eventsSF['replanning_status'] = np.where(eventsSF['type']=='Replanning', 1, 0)

#Summarised table
Person_Trip_eventsSF = pd.pivot_table(
   eventsSF,
   index=['IDMerged','tripIndex'],
   aggfunc={'actStartTime': np.sum, 'actEndTime': np.sum, 'travelTime': np.sum, 'cost_BEAM': np.sum, 'actStartType': np.sum, 
            'actEndType': np.sum, 'duration_walking': np.sum, 'duration_in_privateCar': np.sum, 'duration_on_bike': np.sum, 
            'duration_in_ridehail': np.sum, 'travelDistance': np.sum, 'duration_in_transit': np.sum, 'distance_walking': np.sum, 
            'distance_bike': np.sum, 'distance_ridehail': np.sum, 'distance_privateCar': np.sum, 'distance_transit': np.sum, 
            'legVehicleIds': np.sum, 
            'mode_choice_planned_BEAM':lambda x: ', '.join(set(x.dropna().astype(str))),
            'mode_choice_actual_BEAM':lambda x: ', '.join(set(x.dropna().astype(str))),
            'tripId': np.sum, 
            'vehicle': lambda x: ', '.join(set(x.dropna().astype(str))),
            'numPassengers': lambda x: ', '.join(list(x.dropna().astype(str))),
            'length_mode_choice': np.sum, 
            'replanning_status': np.sum,
            'reason': lambda x: ', '.join(list(x.dropna().astype(str)))}).reset_index()   

Person_Trip_eventsSF['door_to_door_time'] = Person_Trip_eventsSF['actStartTime'] - Person_Trip_eventsSF['actEndTime'] 
Person_Trip_eventsSF['waitTime'] = Person_Trip_eventsSF['door_to_door_time'] - Person_Trip_eventsSF['travelTime'] 
Person_Trip_eventsSF['actPurpose'] = Person_Trip_eventsSF['actEndType'].astype(str) + "_to_" + Person_Trip_eventsSF['actStartType'].astype(str)
Person_Trip_eventsSF.rename(columns={"legVehicleIds":"legVehicleIds_estimate"}, inplace=True) 
Person_Trip_eventsSF.rename(columns={"vehicle":"vehicleIds"}, inplace=True) 


# Merging with activity sim persons and housholds files
actloc_2018 = "https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-2018-base-20220327/activitysim/"
households = pd.read_csv(actloc_2018 + 'final_households.csv')
persons = pd.read_csv(actloc_2018 + 'final_persons.csv')
tours = pd.read_csv(actloc_2018 +'final_tours.csv')
plans = pd.read_csv(actloc_2018 +'final_plans.csv')
trips = pd.read_csv(actloc_2018 + 'final_trips.csv')

# Merge households and persons 
persons = persons.sort_values(by=['household_id'])
households = households.sort_values(by=['household_id'])
hhpersons = pd.merge(left=persons, right=households, how='left', on='household_id')

# Merge tours, households and persons
tours = tours.sort_values(by=['person_id'])
hhpersons = hhpersons.sort_values(by=['person_id'])
hhperTours = pd.merge(left=tours, right=hhpersons, how='left', on='person_id')

# Merge trips, tours, households and persons
trips = trips.sort_values(by=['person_id', 'tour_id'])
hhperTours = hhperTours.sort_values(by=['person_id','tour_id'])
tourTripsMerged = pd.merge(left=trips, right=hhperTours, how='left', on=['person_id','tour_id'])

# Merge person_trip level BEAM with activity sim merged files
tourTripsMerged = tourTripsMerged.sort_values(by=['person_id', 'trip_id'])
Person_Trip_eventsSF = Person_Trip_eventsSF.sort_values(by=['IDMerged','tripId'])
eventsASim = pd.merge(left=Person_Trip_eventsSF, right=tourTripsMerged, how='left', left_on=["IDMerged", 'tripId'], right_on=['person_id', 'trip_id'])

eventsASim.rename(columns={"mode_choice_logsum_y":"logsum_tours_mode_AS_tours"}, inplace=True)
eventsASim.rename(columns={"tour_mode":"tour_mode_AS_tours"}, inplace=True)
eventsASim.rename(columns={"mode_choice_logsum_x":"logsum_trip_mode_AS_trips"}, inplace=True)
eventsASim.rename(columns={"trip_mode":"trip_mode_AS_trips"}, inplace=True)