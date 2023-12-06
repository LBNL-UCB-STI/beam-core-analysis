library(sf)
library(dplyr)

setwd("/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF")

ca_network <- st_read('california2017/California2017.shp')
list_of_attribute <- colnames(ca_network)
ca_network <- ca_network %>% 
  select(Route_ID, Begin_Poin, End_Point, Route_Numb, F_System, Urban_Code, County_Cod,
         Through_La, Speed_Limi, AADT, AADT_Singl, AADT_Combi, Shape_Leng)
network_crs <- st_crs(ca_network)

sf_boundary <- st_read('SF_counties.geojson')
sf_boundary <- st_transform(sf_boundary, network_crs)

list_of_sf_counties <- unique(sf_boundary$NAME)
sf_boundary <- sf_boundary %>% mutate(COUNTYFP = as.integer(COUNTYFP))
sf_boundary_df <- sf_boundary %>% st_drop_geometry()

sf_network <- merge(ca_network, sf_boundary_df, by.x = 'County_Cod', by.y = 'COUNTYFP', all.x= FALSE)

# list_of_austin_code <- unique(austin_county_code$TxDOT.County.Code)
# austin_network <- texas_network %>%
#   filter(CO %in% list_of_austin_code)
# austin_network <- merge(austin_network,y=austin_county_code,by.x= 'CO', by.y = 'TxDOT.County.Code', all.x=TRUE)
plot(st_geometry(sf_boundary), border = 'blue')
plot(st_geometry(st_zm(sf_network)), add = TRUE)
# plot(st_geometry(st_zm(austin_network)), add = TRUE)

st_write(sf_network, 'sf_hpms_inventory.geojson')
sf_network_df <- sf_network %>% st_drop_geometry()
write.csv(sf_network_df, 'sf_hpms_inventory.csv')
