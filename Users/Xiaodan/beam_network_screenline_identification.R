library(sf)
library(leaflet)
library(mapview)
library(dplyr)
setwd("/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/Austin/traffic count/Austin data")
detector_location <- read.csv("detector_location.csv")
detector_location_sf = st_as_sf(detector_location, coords = c('LOCATION_LONGITUDE', 'LOCATION_LATITUDE'), 
                            crs = 4326, agr = "constant")

bbox <- st_bbox(detector_location_sf)%>% as.vector()
detector_map <- leaflet(detector_location_sf) %>% addProviderTiles(providers$Stamen.TonerLite) %>% addCircleMarkers()
mapshot(detector_map, file = "detector_location.png")

st_write(detector_location_sf, 'detector_location.geojson')

setwd("/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/sample output/AUS2018/")
beam_network <- st_read('beam_network_by_county.geojson')
roadway_type <- c('motorway_link', 'tertiary', 'secondary', 'trunk', 'secondary_link', 'trunk_link', 
                  'primary_link', 'motorway', 'primary', 'tertiary_link')
# beam_network_with_cars <- beam_network %>% filter(linkModes %in% c('car;bike', 'car;walk;bike'))
beam_network_with_cars <- beam_network %>% filter(attributeOrigType %in% roadway_type)
beam_network_with_radar <- st_is_within_distance(detector_location_sf, beam_network_with_cars, dist = 50)
# beam_network_with_radar <- st_join(detector_location_sf, beam_network_with_cars, join = st_is_within_distance(dist = 100))

selected_beam_network_out <- NULL
for (row in 1:nrow(beam_network_with_radar)) {
  list_of_links = beam_network_with_radar[row][[1]]
  selected_beam_network <- beam_network_with_cars[list_of_links,]
  radar_id <- as.numeric(detector_location_sf[row, 'KITS_ID'])
  selected_beam_network$KITS_ID <- radar_id
  selected_beam_network_out <-  rbind(selected_beam_network_out, selected_beam_network)
  #print(list_of_links)
}



plot(st_geometry(selected_beam_network_out), col = 'blue')
plot(st_geometry(detector_location_sf[5,]))
plot(st_geometry(detector_location_sf), col = 'red', add = TRUE)
st_write(selected_beam_network_out, 'BEAM_network_screenlines.geojson')

selected_beam_network_out_df <- selected_beam_network_out %>% st_drop_geometry()
write.csv(selected_beam_network_out_df, 'BEAM_network_screenlines.csv')
