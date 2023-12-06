library(sf)
library(dplyr)
library(data.table)

# SELECT AUSTIN STATIONS
file_link = '/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/Austin/NPMRDS/Texas.shp'
texas_npmrds_station <- st_read(file_link)
austin_boundary <- st_read('/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/Austin/austin_counties.shp')
austin_boundary <- st_transform(austin_boundary, 4326)

austin_npmrds_station <- st_intersection(texas_npmrds_station, austin_boundary)

plot(st_geometry(austin_boundary), border = 'blue')
plot(st_geometry(austin_npmrds_station), add = TRUE)
st_write(austin_npmrds_station, 
         '/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/Austin/NPMRDS/austin_NPMRDS_station.geojson')


# load BEAM network
setwd("/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/sample output/AUS2018/")
beam_network <- st_read('beam_network_by_county.geojson')
roadway_type <- c('motorway_link', 'trunk', 'trunk_link', 
                  'primary_link', 'motorway', 'primary', 'secondary', 'secondary_link')

beam_network_with_cars <- beam_network %>% filter(attributeOrigType %in% roadway_type)
beam_network_with_cars <- beam_network_with_cars %>% filter(linkModes %in% c('car;bike', 'car;walk;bike'))
beam_network_with_tmc <- st_is_within_distance(austin_npmrds_station, beam_network_with_cars, dist = 50)

austin_npmrds_station_df <- austin_npmrds_station %>% st_drop_geometry()
selected_beam_network_out <- NULL
for (row in 1:nrow(beam_network_with_tmc)) {
  list_of_links = beam_network_with_tmc[row][[1]]
  if (length(list_of_links) == 0){
    next
  }
  selected_beam_network <- beam_network_with_cars[list_of_links,]
  selected_tmc <- austin_npmrds_station[row,]
  tmc_id <- toString(austin_npmrds_station_df[row, 'Tmc'])
  print(tmc_id)
  selected_beam_network$Tmc <- tmc_id
  selected_beam_network$dist_to_tmc <- st_distance(selected_beam_network, selected_tmc)
  selected_beam_network_out <-  rbind(selected_beam_network_out, selected_beam_network)
  #print(list_of_links)
}

# remove duplicated links and keep closest TMC (there are duplicates because 1 link can be close to multiple TMCs)
selected_beam_network_filtered <- selected_beam_network_out %>%
  group_by(linkId) %>%
  slice(which.min(dist_to_tmc))

plot(st_geometry(selected_beam_network_filtered), col = 'blue')
plot(st_geometry(austin_npmrds_station), col = 'red', lwd = 0.5, add = TRUE)

selected_beam_network_filtered_df <- selected_beam_network_filtered %>% st_drop_geometry()

st_write(selected_beam_network_filtered, 'beam_network_npmrds_screenline.geojson')
write.csv(selected_beam_network_filtered_df, 'beam_network_npmrds_screenline.csv')
# SELECT AUSTIN SPEED DATA
data_link = '/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/Austin/NPMRDS/MFD.VolDens.sc_ut_oct2018_1hr.RData'
load(data_link)

austin_npmrds_station <- austin_npmrds_station %>% 
  select(Tmc, TmcType, RoadNumber, RoadName, IsPrimary, FirstName, Zip, StartLat, StartLong, EndLat, EndLong, FRC,
  Urban_Code, FacilType, ThruLanes, Route_Numb,
         Route_Sign, Route_Qual, AADT_Singl, AADT_Combi, Truck, shape_area, shape_leng)
austin_npmrds_data <- merge(all, austin_npmrds_station, 
                            by = 'Tmc', all.x=FALSE)

plot_sample <- austin_npmrds_data[austin_npmrds_data$hour==18,]
plot(plot_sample[,'mean.spd'])

austin_npmrds_data_out <- austin_npmrds_data %>% select(Tmc, fips, f_sys, station, dir, month, day, hour, flow_per_lane,
                                                        speed, state, ThruLanes.x, Miles, mean.spd, GEOID, County, AADT,
                                                        density_per_lane, StartLat, StartLong, EndLat, EndLong, Truck)
write.csv(austin_npmrds_data_out, '/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/Austin/NPMRDS/austin_NPMRDS.csv')
