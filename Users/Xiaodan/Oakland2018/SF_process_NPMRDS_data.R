library(sf)
library(dplyr)
library(data.table)

# SELECT AUSTIN STATIONS
file_link = '/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/NPMRDS/California.shp'
california_npmrds_station <- st_read(file_link)
sf_boundary <- st_read('/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/SF_counties.geojson')
sf_boundary <- st_transform(sf_boundary, 4326)
sf_npmrds_station <- st_intersection(california_npmrds_station, sf_boundary)


sf_npmrds_station_df <- sf_npmrds_station %>% st_drop_geometry()
tmc_in_sf <- unique(sf_npmrds_station_df$Tmc)

data_link = '/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/NPMRDS/al_ca_oct2018_1hr_trucks_pax.csv'
npmrds_data <- data.table::fread(data_link, h = T)
npmrds_data <- npmrds_data %>% filter(tmc_code %in% tmc_in_sf)

write.csv(npmrds_data, '/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/NPMRDS/sf_npmrds_data.csv')
tmc_with_data = unique(all$Tmc)

sf_npmrds_station_df <- sf_npmrds_station %>% st_drop_geometry()
tmc_in_sf <- dplyr::pull(sf_npmrds_station_df, Tmc)

sf_npmrds_data <- npmrds_data %>% filter(tmc_code %in% tmc_in_sf)

sf_npmrds_station_with_data <- sf_npmrds_station %>% filter(Tmc %in% tmc_with_data)

plot(st_geometry(sf_boundary), border = 'blue')
plot(st_geometry(sf_npmrds_station_with_data), add = TRUE)
st_write(sf_npmrds_station, 
         '/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/NPMRDS/sf_NPMRDS_station.geojson')




# load BEAM network
setwd("/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/sample output/SFB2010V2/")
beam_network <- st_read('beam_network_by_county.geojson')
roadway_type <- c('motorway_link', 'trunk', 'trunk_link', 
                  'primary_link', 'motorway', 'primary', 'secondary', 'secondary_link')

beam_network_with_cars <- beam_network %>% filter(attributeOrigType %in% roadway_type)
beam_network_with_cars <- beam_network_with_cars %>% filter(linkModes %in% c('car;bike', 'car;walk;bike'))
beam_network_with_tmc <- st_is_within_distance(sf_npmrds_station, beam_network_with_cars, dist = 20)

sf_npmrds_station_df <- sf_npmrds_station %>% st_drop_geometry()
selected_beam_network_out <- NULL
for (row in 1:nrow(beam_network_with_tmc)) {
  list_of_links = beam_network_with_tmc[row][[1]]
  if (length(list_of_links) == 0){
    next
  }
  selected_beam_network <- beam_network_with_cars[list_of_links,]
  selected_tmc <- sf_npmrds_station[row,]
  tmc_id <- toString(sf_npmrds_station_df[row, 'Tmc'])
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
plot(st_geometry(sf_npmrds_station), col = 'red', lwd = 0.5, add = TRUE)

selected_beam_network_filtered_df <- selected_beam_network_filtered %>% st_drop_geometry()

st_write(selected_beam_network_filtered, 'beam_network_npmrds_screenline.geojson')
write.csv(selected_beam_network_filtered_df, 'beam_network_npmrds_screenline.csv')
# SELECT AUSTIN SPEED DATA


# select oakland + alameda npmrds stations
processed_sf_npmrds_stations <- st_read('/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/NPMRDS/sf_NPMRDS_station.geojson')
oakland_boundary <- st_read('/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/Oakland+Alameda+TAZ/Transportation_Analysis_Zones.shp')

oakland_boundary_combined <- st_union(oakland_boundary)
plot(oakland_boundary_combined)
oakland_npmrds_stations <- st_intersection(processed_sf_npmrds_stations, oakland_boundary_combined)
plot(st_geometry(oakland_npmrds_stations), col = 'green', add = TRUE)

st_write(oakland_npmrds_stations, "/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/NPMRDS/oakland_npmrds_stations.geojson")

oakland_npmrds_stations_df <- oakland_npmrds_stations %>% st_drop_geometry()
write.csv(oakland_npmrds_stations_df, "/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/NPMRDS/oakland_npmrds_stations.csv")

setwd("/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/sample output/Oakland2021/")
selected_beam_network_filtered_df <- data.table::fread('beam_network_npmrds_screenline.csv', h = T)

oakland_tmc <- unique(oakland_npmrds_stations_df$Tmc)
oakland_beam_network_filtered_df <- selected_beam_network_filtered_df %>% filter(Tmc %in% oakland_tmc)
write.csv(oakland_beam_network_filtered_df, "beam_network_npmrds_screenline_oak.csv")

beam_network_screenline <- st_read('beam_network_npmrds_screenline.geojson')
beam_network_screenline_oakland <- beam_network_screenline %>% filter(Tmc  %in% oakland_tmc)
plot(st_geometry(beam_network_screenline_oakland), lty = 3, col = 'violet', lwd = 1, add = TRUE)

