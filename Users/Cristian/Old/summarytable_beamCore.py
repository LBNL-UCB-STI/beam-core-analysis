import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gzip
import time
#Compare pathtraversal share per different scenario
#Check speeds only for durations >0

start = time.time()
print('Start time',start, 's')

nRows = None #None for all rows
print('Read events...')
# ~ filepath = "https://beam-outputs.s3.amazonaws.com/pilates-outputs/sfbay-base-20220409/beam/"
filepath = '/Users/cpoliziani/Downloads/Data/PILATES/'

filepath_res = '/Users/cpoliziani/Downloads/BEAM-CORE/Results/'
data_names = ['/testVN.csv.gz']
# ~ data_names = ['/Baseline.csv.gz',  '/RHsz0.125.csv.gz',  '/RHsz0.25.csv.gz',  '/RHsz0.5.csv.gz', 
	 # ~ 'RHsz1.75.csv.gz',  'TRfr0.5.csv.gz',  'TRfr0.5cp.csv.gz','TRfr1.5.csv.gz',  
	 # ~ 'TRfr1.5cp.csv.gz','TRfr2.0.csv.gz', 'TRfr2.0cp.csv.gz',]
# ~ filepath = '/Users/cpoliziani/Downloads/'
# ~ data_names = ['/Baseline.csv.gz',  '/RHsz0.125.csv.gz',  '/RHsz0.25.csv.gz',  '/RHsz0.5.csv.gz', 
	 # ~ '/RHsz1.75.csv.gz',  '/TRfr0.5.csv.gz',  '/TRfr1.5.csv.gz',  '/TRfr2.0.csv.gz', ]
# ~ data_names = ['year-2018-iteration-0/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2018-iteration-1/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2018-iteration-2/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2018-iteration-3/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2018-iteration-4/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2018-iteration-5/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2019-iteration-0/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2019-iteration-1/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2019-iteration-2/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2019-iteration-3/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2019-iteration-4/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2019-iteration-5/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2020-iteration-0/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2020-iteration-1/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2020-iteration-2/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2020-iteration-3/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2020-iteration-4/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2020-iteration-5/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2021-iteration-0/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2021-iteration-1/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2021-iteration-2/ITERS/it.0/0.events.csv.gz',
			  # ~ 'year-2021-iteration-2/ITERS/it.0/0.events.csv.gz',
			  # ~ ]
# ~ names = ['Baseline','Ride Hail Fleet 12.5%','Ride Hail Fleet 25%','Ride Hail Fleet 50%','Ride Hail Fleet 175%',
			# ~ 'Transit Frequency 0.5 (80%)','NEW Transit Frequency 0.5 (80%)','Transit Frequency 1.5 (120%)','NEW Transit Frequency 1.5 (120%)',
			# ~ 'Transit Frequency 2.0 (150%)', 'NEW Transit Frequency 2.0 (150%)']
names = data_names

pathTraversalColumns = [
		'vehicle','time','type','mode','length','vehicleType',
		'endY','endX',	'startY','startX','arrivalTime','departureTime','secondaryFuelLevel',
		'primaryFuelLevel','driver','toStopIndex','fromStopIndex','seatingCapacity','tollPaid',
		'capacity','linkTravelTime','secondaryFuel','primaryFuelType','links','numPassengers','primaryFuel',
		]
ModeChoiceColumns = ['person',	'time',	'type',	'mode',	'currentTourMode',	
	'availableAlternatives','location',	'personalVehicleAvailable',	'length',	
	'tourIndex',	'legModes',	 'legVehicleIds',	'currentActivity',	
	'nextActivity',	'tripId']


summaryTable = pd.DataFrame()

pathTraversalModes = np.array(['walk','bike','car','car_RideHail','car_RideHail_empty','car_CAV','car_hov2','car_hov3','bus','tram','rail','subway','cable_car','ferry','bus_empty','tram_empty','rail_empty','subway_empty','cable_car_empty','ferry_empty'])
pathTraversalModesNames = ['Walk','Bike','Car','Ride Hail','Empty Ride Hail','CAV','Car HOV2','Car HOV3','Bus','Tram','Rail','Subway','Cable Car','Ferry','Empty Bus','Empty Tram','Empty Rail','Empty Subway','Empty Cable Car','Empty Ferry',]
transitCompanies = ['3D','AC','AM','AY','BA','CC','CE','CM','CT','DE','EM','GG','HF','MA','PE','RV','SC','SF','SM','SO','SR','ST','VC','VN','VT','WC','WH']
modeChoiceModes = np.array([ 'bus', 'subway', 'tram', 'rail', 'car', 'hov3_teleportation', 'bike', 'hov2_teleportation', 'walk', 'car_hov2', 'car_hov3', 'walk_transit', 'ride_hail', 'ride_hail_transit', 'ride_hail_pooled', 'drive_transit', 'cable_car','bike_transit'])
modeChoiceNames = [ 'Bus', 'Subway', 'Tram', 'Rail', 'Car', 'HOV3 Passenger', 'Bike', 'HOV2 Passenger', 'Walk', 'HOV2 Driver', 'HOV3 Driver', 'Walk-Transit', 'Ride Hail', 'Ride Hail-transit', 'Ride Hail Pooled', 'Drive-transit', 'Cable Car', 'Bike-Transit']
primaryFuelTypes =['Biodiesel','Diesel','Gasoline','Electricity','Food']
print('Start Summary Table...')

for data_name, name in zip(data_names, names):
	
	print(filepath+data_name)
	data = 0.

	start_read = time.time()
	data = pd.read_csv(filepath+data_name, 
		nrows=nRows, 
		#index_col = eventColumns, 
		compression='gzip',
		)
	end_read = time.time()
	print('*_*_*_*__Read event file', end_read - start_read, 's')
	
	PersonEntersVehicle = data[data['type'] == 'PersonEntersVehicle'][['vehicle']]
	pathTraversal = data[(data['type'] == 'PathTraversal')][pathTraversalColumns]
	# ~ pathTraversal.to_csv('/Users/cpoliziani/Downloads/pathTraversal+.csv')
	
	pathTraversal['occupancy'] = pathTraversal['numPassengers']
	pathTraversal.loc[pathTraversal['mode'] == 'car', 'occupancy'] += 1
	pathTraversal.loc[pathTraversal['mode'] == 'car_hov2', 'occupancy'] += 1
	pathTraversal.loc[pathTraversal['mode'] == 'car_hov3', 'occupancy'] += 1
	pathTraversal.loc[pathTraversal['mode'] == 'walk', 'occupancy'] = 1
	pathTraversal.loc[pathTraversal['mode'] == 'bike', 'occupancy'] = 1
	
	
	pathTraversal.loc[pathTraversal['mode'] == 'car', 'capacity'] += 1.5
	pathTraversal.loc[pathTraversal['mode'] == 'car_hov2', 'capacity'] += 1.5
	pathTraversal.loc[pathTraversal['mode'] == 'car_hov3', 'capacity'] += 1.5
	pathTraversal.loc[pathTraversal['mode'] == 'walk', 'capacity'] = 1
	pathTraversal.loc[pathTraversal['mode'] == 'bike', 'capacity'] = 1
	
	# ~ pathTraversal.loc[pathTraversal['mode'] == 'walk', 'numPassengers'] = 1
	# ~ pathTraversal.loc[pathTraversal['mode'] == 'bike', 'numPassengers'] = 1
	pathTraversal['isRH'] = pathTraversal['vehicle'].str.contains('rideHail')
	pathTraversal['isbus'] = pathTraversal['mode'].str.contains('bus')
	pathTraversal['istram'] = pathTraversal['mode'].str.contains('tram')
	pathTraversal['israil'] = pathTraversal['mode'].str.contains('rail')
	pathTraversal['issubway'] = pathTraversal['mode'].str.contains('subway')
	pathTraversal['iscable'] = pathTraversal['mode'].str.contains('cable_car')
	pathTraversal['isferry'] = pathTraversal['mode'].str.contains('ferry')

	pathTraversal['is_empty'] = pathTraversal['numPassengers'] == 0
	
	pathTraversal['is_RHempty'] = pathTraversal['isRH']*pathTraversal['is_empty']
	pathTraversal['is_bus_empty'] = pathTraversal['isbus']*pathTraversal['is_empty']
	pathTraversal['is_tram_empty'] = pathTraversal['istram']*pathTraversal['is_empty']
	pathTraversal['is_rail_empty'] = pathTraversal['israil']*pathTraversal['is_empty']
	pathTraversal['is_subway_empty'] = pathTraversal['issubway']*pathTraversal['is_empty']
	pathTraversal['is_cable_empty'] = pathTraversal['iscable']*pathTraversal['is_empty']
	pathTraversal['is_rail_empty'] = pathTraversal['isferry']*pathTraversal['is_empty']

	pathTraversal['isCAV'] = pathTraversal['vehicleType'].str.contains('L5')
	pathTraversal.loc[pathTraversal['isRH'], 'mode'] += '_RideHail'
	pathTraversal.loc[pathTraversal['isCAV'], 'mode'] += '_CAV'
	pathTraversal.loc[pathTraversal['is_RHempty'], 'mode'] += '_empty'
	pathTraversal.loc[pathTraversal['is_bus_empty'], 'mode'] += '_empty'
	pathTraversal.loc[pathTraversal['is_tram_empty'], 'mode'] += '_empty'
	pathTraversal.loc[pathTraversal['is_rail_empty'], 'mode'] += '_empty'
	pathTraversal.loc[pathTraversal['is_subway_empty'], 'mode'] += '_empty'
	pathTraversal.loc[pathTraversal['is_cable_empty'], 'mode'] += '_empty'
	pathTraversal.loc[pathTraversal['is_rail_empty'], 'mode'] += '_empty'

	modeChoice = data[(data['type'] == 'ModeChoice')][ModeChoiceColumns]
	
	vehicles_2 = []
	vehicles = pathTraversal['vehicle']
	for vehicle in vehicles:
		vehicles_2.append(vehicle[:2])
	vehicles_2 = np.array(vehicles_2)
	
	vehicles_3 = []
	vehicles = PersonEntersVehicle['vehicle']
	for vehicle in vehicles:
		vehicles_3.append(vehicle[:2])
	vehicles_3 = np.array(vehicles_3)
	
	
	
	

	print('Add vehicle trips...',name)
	start_trips = time.time()
	#Add vehicle trips
	totalTrips_vehicle = len(pathTraversal['mode'])
	totalTrips_mode = len(modeChoice['mode'])
	
	print('Number Trips...',name)
#----------Number Trips

	summaryTable.at['Trip Vehicle Total ', name] = totalTrips_vehicle
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		summaryTable.at['Trip Vehicle '+pathTraversalModesName, name] = len(pathTraversal['mode'][(pathTraversal['mode'] == pathTraversalMode)])
	summaryTable.at['Trip Mode Total ', name] = totalTrips_mode
	for modeChoiceMode, modeChoiceName in zip(modeChoiceModes, modeChoiceNames):
		summaryTable.at['Trip Mode '+modeChoiceName, name] = len(modeChoice['mode'][(modeChoice['mode'] == modeChoiceMode)])
	for primaryFuelType in primaryFuelTypes:
		summaryTable.at['Trip Vehicle '+primaryFuelType, name] = len(pathTraversal['primaryFuelType'][(pathTraversal['primaryFuelType'] == primaryFuelType)])
#----------Share Trips
	print('Share Trips...',name)

	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		summaryTable.at['Trip Vehicle Share '+pathTraversalModesName, name] = len(pathTraversal['mode'][(pathTraversal['mode'] == pathTraversalMode)])/totalTrips_vehicle
	for modeChoiceMode, modeChoiceName in zip(modeChoiceModes, modeChoiceNames):
		summaryTable.at['Trip Mode Share '+modeChoiceName, name] = len(modeChoice['mode'][(modeChoice['mode'] == modeChoiceMode)])/totalTrips_mode
	for primaryFuelType in primaryFuelTypes:
		summaryTable.at['Trip Vehicle Share '+primaryFuelType, name] = len(pathTraversal['primaryFuelType'][(pathTraversal['primaryFuelType'] == primaryFuelType)])/totalTrips_vehicle
	
	print('*_*_*_*__Trips comp time =', time.time()-start_trips, 's')
#----------Active Vehicles
	# ~ summaryTable.at['Active Vehicle Total'] = len(pd.unique(pathTraversal['vehicle']))
	# ~ for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		# ~ summaryTable.at['Active Vehicle '+pathTraversalModesName] = len(pd.unique(pathTraversal['vehicle'][(pathTraversal['mode'] == pathTraversalMode)]))
#----------Active Person
	# ~ summaryTable.at['Active Mode Person Total'] = len(pd.unique(modeChoice['person']))
	# ~ for modeChoiceMode, modeChoiceModesName in zip(modeChoiceModes, modeChoiceNames):
		# ~ summaryTable.at['Active Mode Person '+modeChoiceModesName] = len(pd.unique(modeChoice['person'][(modeChoice['mode'] == modeChoiceMode)]))
#----------Trip lengths
#----------------------Vehicles
	start_lengths =  time.time()

	print('Lengths Vehicles...',name)

	lengths = pathTraversal['length']/1000.
	summaryTable.at['Length Vehicle Total [km]', name] = np.sum(lengths)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		lengths_mode = lengths[(pathTraversal['mode'] == pathTraversalMode)]
		summaryTable.at['Length Vehicle Total '+pathTraversalModesName+' [km]', name] = np.sum(lengths_mode)
	for company in transitCompanies:
		lengths_company = lengths[(vehicles_2 == company)]
		summaryTable.at['Length Vehicle Total '+company+' [km]', name] = np.sum(lengths_company)
	for primaryFuelType in primaryFuelTypes:
		lengths_fueltype = lengths[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		summaryTable.at['Length Vehicle Total '+primaryFuelType+' [km]', name] = np.sum(lengths_fueltype)
	summaryTable.at['Length Vehicle Average [km]', name] = np.mean(lengths)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		lengths_mode = lengths[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(lengths_mode) > 0:
			summaryTable.at['Length Vehicle Average '+pathTraversalModesName+' [km]', name] = np.mean(lengths_mode)
	for company in transitCompanies:
		lengths_company = lengths[(vehicles_2 == company)]
		if np.sum(lengths_company) > 0:
			summaryTable.at['Length Vehicle Average '+company+' [km]', name] = np.mean(lengths_company)
	for primaryFuelType in primaryFuelTypes:
		lengths_fueltype = lengths[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(lengths_fueltype) > 0:
			summaryTable.at['Length Vehicle Average '+primaryFuelType+' [km]', name] = np.mean(lengths_fueltype)
	summaryTable.at['Length Vehicle Std [km]', name] = np.std(lengths)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		lengths_mode = lengths[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(lengths_mode) > 0:
			summaryTable.at['Length Vehicle Std '+pathTraversalModesName+' [km]', name] = np.std(lengths_mode)
	for company in transitCompanies:
		lengths_company = lengths[(vehicles_2 == company)]
		if np.sum(lengths_company) > 0:
			summaryTable.at['Length Vehicle Std '+company+' [km]', name] = np.std(lengths_company)
	for primaryFuelType in primaryFuelTypes:
		lengths_fueltype = lengths[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(lengths_fueltype) > 0:
			summaryTable.at['Length Vehicle Std '+primaryFuelType+' [km]', name] = np.std(lengths_fueltype)
	summaryTable.at['Length Vehicle 1stQ [km]', name] = np.percentile(lengths,25)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		lengths_mode = lengths[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(lengths_mode) > 0:
			summaryTable.at['Length Vehicle 1stQ '+pathTraversalModesName+' [km]', name] = np.percentile(lengths_mode,25)
	for company in transitCompanies:
		lengths_company = lengths[(vehicles_2 == company)]
		if np.sum(lengths_company) > 0:
			summaryTable.at['Length Vehicle 1stQ '+company+' [km]', name] = np.percentile(lengths_company,25)
	for primaryFuelType in primaryFuelTypes:
		lengths_fueltype = lengths[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(lengths_fueltype) > 0:
			summaryTable.at['Length Vehicle 1stQ '+primaryFuelType+' [km]', name] = np.percentile(lengths_fueltype,25)
	summaryTable.at['Length Vehicle 2ndQ [km]', name] = np.percentile(lengths,50)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		lengths_mode = lengths[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(lengths_mode) > 0:
			summaryTable.at['Length Vehicle 2ndQ '+pathTraversalModesName+' [km]', name] = np.percentile(lengths_mode, 50)
	for company in transitCompanies:
		lengths_company = lengths[(vehicles_2 == company)]
		if np.sum(lengths_company) > 0:
			summaryTable.at['Length Vehicle 2ndQ '+company+' [km]', name] = np.percentile(lengths_company, 50)
	for primaryFuelType in primaryFuelTypes:
		lengths_fueltype = lengths[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(lengths_fueltype) > 0:
			summaryTable.at['Length Vehicle 2ndQ '+primaryFuelType+' [km]', name] = np.percentile(lengths_fueltype, 50)
	summaryTable.at['Length Vehicle 3rdQ [km]', name] = np.percentile(lengths,75)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		lengths_mode = lengths[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(lengths_mode) > 0:
			summaryTable.at['Length Vehicle 3rdQ '+pathTraversalModesName+' [km]', name] = np.percentile(lengths_mode, 75)
	for company in transitCompanies:
		lengths_company = lengths[(vehicles_2 == company)]
		if np.sum(lengths_company) > 0:
			summaryTable.at['Length Vehicle 3rdQ '+company+' [km]', name] = np.percentile(lengths_company, 75)	
	for primaryFuelType in primaryFuelTypes:
		lengths_fueltype = lengths[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(lengths_fueltype) > 0:
			summaryTable.at['Length Vehicle 3rdQ '+primaryFuelType+' [km]', name] = np.percentile(lengths_fueltype, 75)
#----------------------Modes
	print('Lengths Modes...',name)

	lengths_modes = modeChoice['length']/1000.
	summaryTable.at['Length Mode Total [km]', name] = np.sum(lengths_modes)
	for modeChoiceMode, modeChoiceModesName in zip(modeChoiceModes, modeChoiceNames):
		lengths_modes_mode = lengths_modes[(modeChoice['mode'] == modeChoiceMode)]
		summaryTable.at['Length Mode Total '+modeChoiceModesName+' [km]', name] = np.sum(lengths_modes_mode)
	summaryTable.at['Length Mode Average [km]', name] = np.mean(lengths_modes)
	for modeChoiceMode, modeChoiceModesName in zip(modeChoiceModes, modeChoiceNames):
		lengths_modes_mode = lengths_modes[(modeChoice['mode'] == modeChoiceMode)]
		if np.sum(lengths_modes_mode) > 0:
			summaryTable.at['Length Mode Average '+modeChoiceModesName+' [km]', name] = np.mean(lengths_modes_mode)
	summaryTable.at['Length Mode Std [km]', name] = np.std(lengths_modes)
	for modeChoiceMode, modeChoiceModesName in zip(modeChoiceModes, modeChoiceNames):
		lengths_modes_mode = lengths_modes[(modeChoice['mode'] == modeChoiceMode)]
		if np.sum(lengths_modes_mode) > 0:
			summaryTable.at['Length Mode Std '+modeChoiceModesName+' [km]', name] = np.std(lengths_modes_mode)
	summaryTable.at['Length Mode 1stQ [km]', name] = np.percentile(lengths_modes,25)
	for modeChoiceMode, modeChoiceModesName in zip(modeChoiceModes, modeChoiceNames):
		lengths_modes_mode = lengths_modes[(modeChoice['mode'] == modeChoiceMode)]
		if np.sum(lengths_modes_mode) > 0:
			summaryTable.at['Length Mode 1stQ '+modeChoiceModesName+' [km]', name] = np.percentile(lengths_modes_mode,25)
	summaryTable.at['Length Mode 2ndQ [km]', name] = np.percentile(lengths_modes,50)
	for modeChoiceMode, modeChoiceModesName in zip(modeChoiceModes, modeChoiceNames):
		lengths_modes_mode = lengths_modes[(modeChoice['mode'] == modeChoiceMode)]
		if np.sum(lengths_modes_mode) > 0:
			summaryTable.at['Length Mode 2ndQ '+modeChoiceModesName+' [km]', name] = np.percentile(lengths_modes_mode, 50)
	summaryTable.at['Length Mode 3rdQ [km]', name] = np.percentile(lengths_modes,75)
	for modeChoiceMode, modeChoiceModesName in zip(modeChoiceModes, modeChoiceNames):
		lengths_modes_mode = lengths_modes[(modeChoice['mode'] == modeChoiceMode)]
		if np.sum(lengths_modes_mode) > 0:
			summaryTable.at['Length Mode 3rdQ '+modeChoiceModesName+' [km]', name] = np.percentile(lengths_modes_mode, 75)
	
	print('*_*_*_*__Lengths comp time =', time.time()-start_lengths, 's')

#----------Trip durations
	print('Trip durations...',name)
	start_durations = time.time()
	
	durations = pathTraversal['arrivalTime']/3600.-pathTraversal['departureTime']/3600.
	summaryTable.at['Duration Vehicle Total [h]', name] = np.sum(durations)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		durations_mode = durations[(pathTraversal['mode'] == pathTraversalMode)]
		summaryTable.at['Duration Vehicle Total '+pathTraversalModesName+' [h]', name] = np.sum(durations_mode)
	for company in transitCompanies:
		durations_company = durations[(vehicles_2 == company)]
		summaryTable.at['Duration Vehicle Total '+company+' [h]', name] = np.sum(durations_company)
	for primaryFuelType in primaryFuelTypes:
		durations_fueltype = durations[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		summaryTable.at['Duration Vehicle Total '+primaryFuelType+' [h]', name] = np.sum(durations_fueltype)
	summaryTable.at['Duration Vehicle Average [h]', name] = np.mean(durations)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		durations_mode = durations[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(durations_mode) > 0:
			summaryTable.at['Duration Vehicle Average '+pathTraversalModesName+' [h]', name] = np.mean(durations_mode)
	for company in transitCompanies:
		durations_company = durations[(vehicles_2 == company)]
		if np.sum(durations_company) > 0:
			summaryTable.at['Duration Vehicle Average '+company+' [h]', name] = np.mean(durations_company)
	for primaryFuelType in primaryFuelTypes:
		durations_fueltype = durations[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(durations_fueltype) > 0:
			summaryTable.at['Duration Vehicle Average '+primaryFuelType+' [h]', name] = np.mean(durations_fueltype)
	summaryTable.at['Duration Vehicle Std [h]', name] = np.std(durations)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		durations_mode = durations[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(durations_mode) > 0:
			summaryTable.at['Duration Vehicle Std '+pathTraversalModesName+' [h]', name] = np.std(durations_mode)
	for company in transitCompanies:
		durations_company = durations[(vehicles_2 == company)]
		if np.sum(durations_company) > 0:
			summaryTable.at['Duration Vehicle Std '+company+' [h]', name] = np.std(durations_company)
	for primaryFuelType in primaryFuelTypes:
		durations_fueltype = durations[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(durations_fueltype) > 0:
			summaryTable.at['Duration Vehicle Std '+primaryFuelType+' [h]', name] = np.std(durations_fueltype)
	summaryTable.at['Duration Vehicle 1stQ [h]', name] = np.percentile(durations,25)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		durations_mode = durations[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(durations_mode) > 0:
			summaryTable.at['Duration Vehicle 1stQ '+pathTraversalModesName+' [h]', name] = np.percentile(durations_mode,25)
	for company in transitCompanies:
		durations_company = durations[(vehicles_2 == company)]
		if np.sum(durations_company) > 0:
			summaryTable.at['Duration Vehicle 1stQ '+company+' [h]', name] = np.percentile(durations_company,25)
	for primaryFuelType in primaryFuelTypes:
		durations_fueltype = durations[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(durations_fueltype) > 0:
			summaryTable.at['Duration Vehicle 1stQ '+primaryFuelType+' [h]', name] = np.percentile(durations_fueltype,25)
	summaryTable.at['Duration Vehicle 2ndQ [h]', name] = np.percentile(durations,50)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		durations_mode = durations[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(durations_mode) > 0:
			summaryTable.at['Duration Vehicle 2ndQ '+pathTraversalModesName+' [h]', name] = np.percentile(durations_mode, 50)
	for company in transitCompanies:
		durations_company = durations[(vehicles_2 == company)]
		if np.sum(durations_company) > 0:
			summaryTable.at['Duration Vehicle 2ndQ '+company+' [h]', name] = np.percentile(durations_company, 50)
	for primaryFuelType in primaryFuelTypes:
		durations_fueltype = durations[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(durations_fueltype) > 0:
			summaryTable.at['Duration Vehicle 2ndQ '+primaryFuelType+' [h]', name] = np.percentile(durations_fueltype, 50)
	summaryTable.at['Duration Vehicle 3rdQ [h]', name] = np.percentile(durations,75)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		durations_mode = durations[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(durations_mode) > 0:
			summaryTable.at['Duration Vehicle 3rdQ '+pathTraversalModesName+' [h]', name] = np.percentile(durations_mode, 75)		
	for company in transitCompanies:
		durations_company = durations[(vehicles_2 == company)]
		if np.sum(durations_company) > 0:
			summaryTable.at['Duration Vehicle 3rdQ '+company+' [h]', name] = np.percentile(durations_company, 75)
	for primaryFuelType in primaryFuelTypes:
		durations_fueltype = durations[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(durations_fueltype) > 0:
			summaryTable.at['Duration Vehicle 3rdQ '+primaryFuelType+' [h]', name] = np.percentile(durations_fueltype, 75)
# ~ #----------Trip speeds
	# ~ print('Trip speeds...',name)

	# ~ speeds = lengths/durations[(durations>0)]
	# ~ print('Null durations for %s'%(name), len(lengths/durations[(durations<=0)]))
	
	# ~ summaryTable.at['Speed Vehicle Average [km/h]', name] = np.mean(speeds)
	# ~ for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		# ~ speeds_mode = speeds[(pathTraversal['mode'][(durations>0)] == pathTraversalMode)]
		# ~ if np.sum(speeds_mode) > 0:
			# ~ summaryTable.at['Speed Vehicle Average '+pathTraversalModesName+' [km/h]', name] = np.mean(speeds_mode)
	# ~ for company in transitCompanies:
		# ~ speeds_company = speeds[(vehicles_2[(durations>0)] == company)]
		# ~ if np.sum(speeds_company) > 0:
			# ~ summaryTable.at['Speed Vehicle Average '+company+' [km/h]', name] = np.mean(speeds_company)
	# ~ for primaryFuelType in primaryFuelTypes:
		# ~ speeds_fueltype = speeds[(pathTraversal['primaryFuelType'][(durations>0)] == primaryFuelType)]
		# ~ if np.sum(speeds_fueltype) > 0:
			# ~ summaryTable.at['Speed Vehicle Average '+primaryFuelType+' [km/h]', name] = np.mean(speeds_fueltype)
	# ~ summaryTable.at['Speed Vehicle Std [km/h]', name] = np.std(speeds)
	# ~ for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		# ~ if np.sum(speeds_mode) > 0:
			# ~ summaryTable.at['Speed Vehicle Std '+pathTraversalModesName+' [km/h]', name] = np.std(speeds_mode)
	# ~ for company in transitCompanies:
		# ~ if np.sum(speeds_company) > 0:
			# ~ summaryTable.at['Speed Vehicle Std '+company+' [km/h]', name] = np.std(speeds_company)
	# ~ for primaryFuelType in primaryFuelTypes:
		# ~ if np.sum(speeds_fueltype) > 0:
			# ~ summaryTable.at['Speed Vehicle Std '+primaryFuelType+' [km/h]', name] = np.std(speeds_fueltype)
	# ~ summaryTable.at['Speed Vehicle 1stQ [km/h]', name] = np.percentile(speeds,25)
	# ~ for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		# ~ if np.sum(speeds_mode) > 0:
			# ~ summaryTable.at['Speed Vehicle 1stQ '+pathTraversalModesName+' [km/h]', name] = np.percentile(speeds_mode,25)
	# ~ for company in transitCompanies:
		# ~ if np.sum(speeds_company) > 0:
			# ~ summaryTable.at['Speed Vehicle 1stQ '+company+' [km/h]', name] = np.percentile(speeds_company,25)
	# ~ for primaryFuelType in primaryFuelTypes:
		# ~ if np.sum(speeds_fueltype) > 0:
			# ~ summaryTable.at['Speed Vehicle 1stQ '+primaryFuelType+' [km/h]', name] = np.percentile(speeds_fueltype,25)
	# ~ summaryTable.at['Speed Vehicle 2ndQ [km/h]', name] = np.percentile(speeds,50)
	# ~ for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		# ~ if np.sum(speeds_mode) > 0:
			# ~ summaryTable.at['Speed Vehicle 2ndQ '+pathTraversalModesName+' [km/h]', name] = np.percentile(speeds_mode, 50)
	# ~ for company in transitCompanies:
		# ~ if np.sum(speeds_company) > 0:
			# ~ summaryTable.at['Speed Vehicle 2ndQ '+company+' [km/h]', name] = np.percentile(speeds_company, 50)
	# ~ for primaryFuelType in primaryFuelTypes:
		# ~ if np.sum(speeds_fueltype) > 0:
			# ~ summaryTable.at['Speed Vehicle 2ndQ '+primaryFuelType+' [km/h]', name] = np.percentile(speeds_fueltype, 50)
	# ~ summaryTable.at['Speed Vehicle 3rdQ [km/h]', name] = np.percentile(speeds,75)
	# ~ for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		# ~ if np.sum(speeds_mode) > 0:
			# ~ summaryTable.at['Speed Vehicle 3rdQ '+pathTraversalModesName+' [km/h]', name] = np.percentile(speeds_mode, 75)
	# ~ for company in transitCompanies:
		# ~ if np.sum(speeds_company) > 0:
			# ~ summaryTable.at['Speed Vehicle 3rdQ '+company+' [km/h]', name] = np.percentile(speeds_company, 75)
	# ~ for primaryFuelType in primaryFuelTypes:
		# ~ if np.sum(speeds_fueltype) > 0:
			# ~ summaryTable.at['Speed Vehicle 3rdQ '+primaryFuelType+' [km/h]', name] = np.percentile(speeds_fueltype, 75)
	print('*_*_*_*__Durations comp time =', time.time()-start_durations, 's')

#----------Energy  Usage
	print('Energy  Usage...',name)
	start_energy = time.time()

	energies = pathTraversal['primaryFuel']/1000000000.+pathTraversal['secondaryFuel']/1000000000.
	summaryTable.at['Energy Vehicle Total [GJ]', name] = np.sum(energies)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		energies_mode = energies[(pathTraversal['mode'] == pathTraversalMode)]
		summaryTable.at['Energy Vehicle Total '+pathTraversalModesName+' [GJ]', name] = np.sum(energies_mode)
	for company in transitCompanies:
		energies_company = energies[(vehicles_2 == company)]
		summaryTable.at['Energy Vehicle Total '+company+' [GJ]', name] = np.sum(energies_company)
	for primaryFuelType in primaryFuelTypes:
		energies_fueltype = energies[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		summaryTable.at['Energy Vehicle Total '+primaryFuelType+' [GJ]', name] = np.sum(energies_fueltype)
	summaryTable.at['Energy Vehicle Average [GJ]', name] = np.mean(energies)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		energies_mode = energies[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(energies_mode) > 0:
			summaryTable.at['Energy Vehicle Average '+pathTraversalModesName+' [GJ]', name] = np.mean(energies_mode)
	for company in transitCompanies:
		energies_company = energies[(vehicles_2 == company)]
		if np.sum(energies_company) > 0:
			summaryTable.at['Energy Vehicle Average '+company+' [GJ]', name] = np.mean(energies_company)
	for primaryFuelType in primaryFuelTypes:
		energies_fueltype = energies[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(energies_fueltype) > 0:
			summaryTable.at['Energy Vehicle Average '+primaryFuelType+' [GJ]', name] = np.mean(energies_fueltype)
	summaryTable.at['Energy Vehicle Std [GJ]', name] = np.std(energies)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		energies_mode = energies[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(energies_mode) > 0:
			summaryTable.at['Energy Vehicle Std '+pathTraversalModesName+' [GJ]', name] = np.std(energies_mode)
	for company in transitCompanies:
		energies_company = energies[(vehicles_2 == company)]
		if np.sum(energies_company) > 0:
			summaryTable.at['Energy Vehicle Std '+company+' [GJ]', name] = np.std(energies_company)
	for primaryFuelType in primaryFuelTypes:
		energies_fueltype = energies[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(energies_fueltype) > 0:
			summaryTable.at['Energy Vehicle Std '+primaryFuelType+' [GJ]', name] = np.std(energies_fueltype)
	summaryTable.at['Energy Vehicle 1stQ [GJ]', name] = np.percentile(energies,25)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		energies_mode = energies[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(energies_mode) > 0:
			summaryTable.at['Energy Vehicle 1stQ '+pathTraversalModesName+' [GJ]', name] = np.percentile(energies_mode,25)
	for company in transitCompanies:
		energies_company = energies[(vehicles_2 == company)]
		if np.sum(energies_company) > 0:
			summaryTable.at['Energy Vehicle 1stQ '+company+' [GJ]', name] = np.percentile(energies_company,25)
	for primaryFuelType in primaryFuelTypes:
		energies_fueltype = energies[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(energies_fueltype) > 0:
			summaryTable.at['Energy Vehicle 1stQ '+primaryFuelType+' [GJ]', name] = np.percentile(energies_fueltype,25)
	summaryTable.at['Energy Vehicle 2ndQ [GJ]', name] = np.percentile(energies,50)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		energies_mode = energies[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(energies_mode) > 0:
			summaryTable.at['Energy Vehicle 2ndQ '+pathTraversalModesName+' [GJ]', name] = np.percentile(energies_mode, 50)
	for company in transitCompanies:
		energies_company = energies[(vehicles_2 == company)]
		if np.sum(energies_company) > 0:
			summaryTable.at['Energy Vehicle 2ndQ '+company+' [GJ]', name] = np.percentile(energies_company, 50)
	for primaryFuelType in primaryFuelTypes:
		energies_fueltype = energies[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(energies_fueltype) > 0:
			summaryTable.at['Energy Vehicle 2ndQ '+primaryFuelType+' [GJ]', name] = np.percentile(energies_fueltype, 50)
	summaryTable.at['Energy Vehicle 3rdQ [GJ]', name] = np.percentile(energies,75)
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		energies_mode = energies[(pathTraversal['mode'] == pathTraversalMode)]
		if np.sum(energies_mode) > 0:
			summaryTable.at['Energy Vehicle 3rdQ '+pathTraversalModesName+' [GJ]', name] = np.percentile(energies_mode, 75)
	for company in transitCompanies:
		energies_company = energies[(vehicles_2 == company)]
		if np.sum(energies_company) > 0:
			summaryTable.at['Energy Vehicle 3rdQ '+company+' [GJ]', name] = np.percentile(energies_company, 75)
	for primaryFuelType in primaryFuelTypes:
		energies_fueltype = energies[(pathTraversal['primaryFuelType'] == primaryFuelType)]
		if np.sum(energies_fueltype) > 0:
			summaryTable.at['Energy Vehicle 3rdQ '+primaryFuelType+' [GJ]', name] = np.percentile(energies_fueltype, 75)
			
	print('*_*_*_*__Energies comp time =', time.time()-start_energy, 's')

#----------Occupancy
	print('Occupancy...',name)
	start_occupancy = time.time()

	passengers = pathTraversal['occupancy']
	capacities = pathTraversal['capacity']

	#include car driver
	# ~ passengers[(pathTraversal['mode'])=='car'] += 1
	# ~ passengers[(pathTraversal['mode'])=='car_hov2'] += 1
	# ~ passengers[(pathTraversal['mode'])=='car_hov3'] += 1

	# ~ capacities[(pathTraversal['mode'])=='car'] += 1
	# ~ capacities[(pathTraversal['mode'])=='car_hov2'] += 1
	# ~ capacities[(pathTraversal['mode'])=='car_hov3'] += 1

	for company in transitCompanies:
		passenger_company = passengers[(vehicles_2 == company)]
		summaryTable.at['Vehicle Passengers stops '+company, name] = np.sum(passenger_company)
		
	for company in transitCompanies:
		passenger_company = passengers[(vehicles_2 == company)]
		lengths_company = lengths[(vehicles_2 == company)]
		summaryTable.at['Vehicle Passengers km '+company, name] = np.sum(passenger_company*lengths_company)
		
	for company in transitCompanies:
		lengths_company = lengths[(vehicles_2 == company)]
		capacities_company = capacities[(vehicles_2 == company)]
		summaryTable.at['Vehicle Capacity km '+company, name] = np.sum(capacities_company*lengths_company)
		
	for company in transitCompanies:
		passenger_company = passengers[(vehicles_2 == company)]
		lengths_company = lengths[(vehicles_2 == company)]
		capacities_company = capacities[(vehicles_2 == company)]
		if np.sum(capacities_company*lengths_company)>0:
			summaryTable.at['Vehicle Load Factor '+company, name] = np.sum(passenger_company*lengths_company)/np.sum(capacities_company*lengths_company)
		
	summaryTable.at['Vehicle Person km Total ', name] = np.sum(lengths*passengers)

	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		if pathTraversalMode != 'bike' and pathTraversalMode != 'walk':
			lengths_mode = lengths[(pathTraversal['mode'] == pathTraversalMode)]
			passengers_mode = passengers[(pathTraversal['mode'] == pathTraversalMode)] 
			summaryTable.at['Vehicle Person km '+pathTraversalModesName, name] = np.sum(lengths_mode*passengers_mode)
		
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		if pathTraversalMode != 'bike' and pathTraversalMode != 'walk':
			lengths_mode = lengths[(pathTraversal['mode'] == pathTraversalMode)]
			capacities_mode = capacities[(pathTraversal['mode'] == pathTraversalMode)] 
			summaryTable.at['Vehicle Capacity km '+pathTraversalModesName, name] = np.sum(lengths_mode*capacities_mode)
		
	for pathTraversalMode, pathTraversalModesName in zip(pathTraversalModes, pathTraversalModesNames):
		if pathTraversalMode != 'bike' and pathTraversalMode != 'walk':
			lengths_mode = lengths[(pathTraversal['mode'] == pathTraversalMode)]
			passengers_mode = passengers[(pathTraversal['mode'] == pathTraversalMode)] 
			capacities_mode = capacities[(pathTraversal['mode'] == pathTraversalMode)] 
			if np.sum(lengths_mode*capacities_mode)>0:
				summaryTable.at['Vehicle Load Factor '+pathTraversalModesName, name] = np.sum(lengths_mode*passengers_mode)/np.sum(lengths_mode*capacities_mode)
	
	print('*_*_*_*__Occupancies comp time =', time.time()-start_occupancy, 's')

#----------Ridership
	print('Ridership...',name)

	start_ridership = time.time()
	
	for company in transitCompanies:
		ridership_company = len(PersonEntersVehicle['vehicle'][(vehicles_3 == company)])
		summaryTable.at['Ridership '+company, name] = ridership_company
		
	print('*_*_*_*__Ridership comp time =', time.time()-start_ridership, 's')

#----------RH
	start_RH = time.time()
	print('Ride hail...',name)

	pathtraversalRH = pathTraversal[pathTraversal['isRH']]
	summaryTable.at['Empty Trips RH', name] = len(pathtraversalRH['vehicle'][pathtraversalRH['numPassengers']==0])
	summaryTable.at['Not Empty Trips RH', name] = len(pathtraversalRH['vehicle'][pathtraversalRH['numPassengers']>0])
	summaryTable.at['Empty Trips RH Share', name] = len(pathtraversalRH['vehicle'][pathtraversalRH['numPassengers']==0])/len(pathtraversalRH['vehicle'])
	summaryTable.at['Not Empty Trips RH Share', name] = len(pathtraversalRH['vehicle'][pathtraversalRH['numPassengers']>0])/len(pathtraversalRH['vehicle'])
	summaryTable.at['Av Trips per RH Vehicle', name] = np.mean((pathtraversalRH['vehicle']).value_counts())
	summaryTable.at['Std Trips per RH Vehicle', name] = np.std((pathtraversalRH['vehicle']).value_counts())
	summaryTable.at['1stQ Trips per RH Vehicle', name] = np.percentile((pathtraversalRH['vehicle']).value_counts(),25)
	summaryTable.at['2ndQ Trips per RH Vehicle', name] = np.percentile((pathtraversalRH['vehicle']).value_counts(),50)
	summaryTable.at['3rdQ Trips per RH Vehicle', name] = np.percentile((pathtraversalRH['vehicle']).value_counts(),75)
	summaryTable.at['Max Trips per RH Vehicle', name] = np.max((pathtraversalRH['vehicle']).value_counts())
	rh_vehicles = pd.unique(pathtraversalRH['vehicle'])
	n_empty = []
	n_notempty = []
	first_trip = []
	last_trip = []
	for rh_vehicle in rh_vehicles:
		pathTraversal_rh_vehicle = pathtraversalRH[pathtraversalRH['vehicle']==rh_vehicle]
		n_empty.append(len(pathTraversal_rh_vehicle['vehicle'][pathTraversal_rh_vehicle['numPassengers']==0]))
		n_notempty.append(len(pathTraversal_rh_vehicle['vehicle'][pathTraversal_rh_vehicle['numPassengers']>0]))
		# ~ print(pathTraversal_rh_vehicle[['vehicle', 'time', 'numPassengers']])
		# ~ share_empty = np.array(n_empty)/(np.array(n_empty)+np.array(n_notempty))
		share_empty = np.array(n_empty)-np.array(n_notempty)
		pathTraversal_rh_vehicle = pathTraversal_rh_vehicle.sort_values(by='time', ascending=True)
		first_trip.append(list(pathTraversal_rh_vehicle['numPassengers'])[0])
		last_trip.append(list(pathTraversal_rh_vehicle['numPassengers'])[-1])

	summaryTable.at['Av RH Vehicle Empty - not Empty Trips', name] = np.mean(share_empty)
	summaryTable.at['Std RH Vehicle Empty - not Empty Trips', name] = np.std(share_empty)
	summaryTable.at['1stQ RH Vehicle Empty - not Empty Trips', name] = np.percentile(share_empty,25)
	summaryTable.at['2ndQ RH Vehicle Empty - not Empty Trips', name] = np.percentile(share_empty,50)
	summaryTable.at['3rdQ RH Vehicle Empty - not Empty Trips', name] = np.percentile(share_empty,75)
	summaryTable.at['Max RH Vehicle Empty - not Empty Trips', name] = np.max(share_empty)
	
	summaryTable.at['RH Empty Share Firts Trip', name] = np.count_nonzero(np.array(first_trip) == 0)/len(first_trip)
	summaryTable.at['RH Empty Share Last Trip', name] = np.count_nonzero(np.array(last_trip) == 0)/len(first_trip)
	summaryTable.at['RH not Empty Share Firts Trip', name] = np.count_nonzero(np.array(first_trip) == 1)/len(first_trip)
	summaryTable.at['RH not Empty Share Last Trip', name] = np.count_nonzero(np.array(last_trip) == 1)/len(first_trip)
	
	print('*_*_*_*__RH comp time =', time.time()-start_RH, 's')

	summaryTable.to_csv(filepath_res+'/summaryTable1.0.csv')
	print(summaryTable[-60:],'Number of attributes',len(summaryTable))	
	print('*_*_*_*__Compile Summary table ', time.time()-end_read, 's')
	
summaryTable['code'] = range(len(summaryTable[summaryTable.keys()[0]]))
print(summaryTable[-60:],'Number of attributes',len(summaryTable))

end = time.time()
print('*_*_*_*__Total time',end-start, 's')





#radar con pass per time

	
