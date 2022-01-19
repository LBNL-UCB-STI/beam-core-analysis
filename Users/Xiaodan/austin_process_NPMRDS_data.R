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
plot(plot_sample)
