library(sf)
library(dplyr)
library(data.table)
library(RgoogleMaps)

# SELECT NPMRDS STATIONS
file_link = '/Users/xiaodanxu/Library/CloudStorage/GoogleDrive-arielinseu@gmail.com/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/NPMRDS/California.shp'
california_npmrds_station <- st_read(file_link)
sf_boundary <- st_read('/Users/xiaodanxu/Library/CloudStorage/GoogleDrive-arielinseu@gmail.com/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/SF_counties.geojson')
sf_boundary <- st_transform(sf_boundary, 4326)
sf_npmrds_station <- st_intersection(california_npmrds_station, sf_boundary)

setwd("/Users/xiaodanxu/Library/CloudStorage/GoogleDrive-arielinseu@gmail.com/My Drive/BEAM-CORE/BEAM Validation/sample output/SFB2018/")
selected_beam_network <- st_read('beam_network_npmrds_screenline.geojson')

beam_network_with_wrong_speed <- read.csv('selected_link_to_check.csv')
list_of_tmcs <- unique(beam_network_with_wrong_speed$Tmc)

selected_npmrds_stations <- sf_npmrds_station %>% filter(Tmc %in% list_of_tmcs)

list_of_beam_links <- unique(beam_network_with_wrong_speed$link)

selected_beam_links_wrong_speed <- selected_beam_network %>% filter(linkId %in% list_of_beam_links)

plot(st_geometry(selected_beam_network), col = 'grey', lwd = 0.3)
plot(st_geometry(selected_npmrds_stations), col = 'blue', lwd = 3, add = TRUE)
plot(st_geometry(selected_beam_links_wrong_speed), col = 'red', lwd = 1, add = TRUE)

beam_network_with_congestion <- read.csv('links_with_high_vc.csv')
list_of_cong_links <- unique(beam_network_with_congestion$link)
selected_beam_links_high_vc <- selected_beam_network %>% filter(linkId %in% list_of_cong_links)
plot(st_geometry(selected_beam_network), col = 'grey', lwd = 0.3)
plot(st_geometry(selected_npmrds_stations), col = 'blue', lwd = 3, add = TRUE)
plot(st_geometry(selected_beam_links_high_vc), col = 'red', lwd = 1, add = TRUE)
