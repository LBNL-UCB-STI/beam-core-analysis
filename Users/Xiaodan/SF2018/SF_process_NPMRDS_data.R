library(sf)
library(dplyr)
library(data.table)

# SELECT AUSTIN STATIONS

#load california NPMRDS station shapefile
file_link = '/Users/xiaodanxu/Library/CloudStorage/GoogleDrive-arielinseu@gmail.com/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/NPMRDS/California.shp'
california_npmrds_station <- st_read(file_link)

# load SF boundaries
sf_boundary <- st_read('//Users/xiaodanxu/Library/CloudStorage/GoogleDrive-arielinseu@gmail.com/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/SF_counties.geojson')
sf_boundary <- st_transform(sf_boundary, 4326)
sf_npmrds_station <- st_intersection(california_npmrds_station, sf_boundary) # select TMC in SF

sf_npmrds_station_df <- sf_npmrds_station %>% st_drop_geometry()
tmc_in_sf <- unique(sf_npmrds_station_df$Tmc)


# load NPMRDS observations
data_link = '/Users/xiaodanxu/Library/CloudStorage/GoogleDrive-arielinseu@gmail.com/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/NPMRDS/al_ca_oct2018_1hr_trucks_pax.csv'
npmrds_data <- data.table::fread(data_link, h = T)

# select NPMRDS data in SF
npmrds_data <- npmrds_data %>% filter(tmc_code %in% tmc_in_sf)

write.csv(npmrds_data, '/Users/xiaodanxu/Library/CloudStorage/GoogleDrive-arielinseu@gmail.com/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/NPMRDS/sf_npmrds_data.csv')

sf_npmrds_station_df <- sf_npmrds_station %>% st_drop_geometry()
tmc_in_sf <- dplyr::pull(sf_npmrds_station_df, Tmc)

sf_npmrds_data <- npmrds_data %>% filter(tmc_code %in% tmc_in_sf)
tmc_with_data <- unique(sf_npmrds_data$tmc_code)
sf_npmrds_station_with_data <- sf_npmrds_station %>% filter(Tmc %in% tmc_with_data)

plot(st_geometry(sf_boundary), border = 'blue')
plot(st_geometry(sf_npmrds_station_with_data), add = TRUE)
st_write(sf_npmrds_station, 
         '/Users/xiaodanxu/Library/CloudStorage/GoogleDrive-arielinseu@gmail.com/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/NPMRDS/sf_NPMRDS_station.geojson')

sf_npmrds_station <- st_read('/Users/xiaodanxu/Library/CloudStorage/GoogleDrive-arielinseu@gmail.com/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/NPMRDS/sf_NPMRDS_station.geojson')
# load BEAM network
setwd("/Users/xiaodanxu/Library/CloudStorage/GoogleDrive-arielinseu@gmail.com/My Drive/BEAM-CORE/BEAM Validation/sample output/SFB2018/")
beam_network <- st_read('beam_network_by_county.geojson')
roadway_type <- c('motorway_link', 'trunk', 'trunk_link', 
                  'primary_link', 'motorway', 'primary', 'secondary', 'secondary_link')

# filter BEAM network to only include highway and major roads --> NPMRDS data only has those roads
beam_network_with_cars <- beam_network %>% filter(attributeOrigType %in% roadway_type)
beam_network_with_cars <- beam_network_with_cars %>% filter(linkModes %in% c('car;bike', 'car;walk;bike'))

# find BEAM links close to NPMRDS TMCs
beam_network_with_tmc <- st_is_within_distance(sf_npmrds_station, beam_network_with_cars, dist = 20)

sf_npmrds_station_df <- sf_npmrds_station %>% st_drop_geometry()
selected_beam_network_out <- NULL

# format output
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

