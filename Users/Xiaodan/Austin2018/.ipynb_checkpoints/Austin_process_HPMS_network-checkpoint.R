library(sf)
library(dplyr)

setwd("/Users/xiaodanxu/Library/CloudStorage/GoogleDrive-arielinseu@gmail.com/My Drive/BEAM-CORE/BEAM Validation/data for validation/Austin")

tx_network <- st_read('texas2017/Texas2017.geojson')
list_of_attribute <- colnames(tx_network)
tx_network <- tx_network %>% 
  select(Route_ID, Begin_Poin, End_Point, Route_Numb, F_System, Urban_Code, County_Cod,
         Through_La, Speed_Limi, AADT, AADT_Singl, AADT_Combi, Shape_Leng)
network_crs <- st_crs(tx_network)

austin_boundary <- st_read('austin_counties.shp')
austin_boundary <- st_transform(austin_boundary, network_crs)

list_of_counties <- unique(austin_boundary$fips_code)

austin_boundary_df <- austin_boundary %>% st_drop_geometry()
austin_boundary_df <- austin_boundary_df %>% select(name, fips_code) %>% mutate(fips_code = as.integer(fips_code))
austin_network <- merge(tx_network, austin_boundary_df, by.x = 'County_Cod', by.y = 'fips_code', all.x= FALSE)
austin_network$length <- st_length(austin_network)
# list_of_austin_code <- unique(austin_county_code$TxDOT.County.Code)
# austin_network <- texas_network %>%
#   filter(CO %in% list_of_austin_code)
# austin_network <- merge(austin_network,y=austin_county_code,by.x= 'CO', by.y = 'TxDOT.County.Code', all.x=TRUE)
plot(st_geometry(austin_boundary), border = 'blue')
plot(st_geometry(st_zm(austin_network)), add = TRUE)
# plot(st_geometry(st_zm(austin_network)), add = TRUE)

st_write(austin_network, 'austin_hpms_inventory.geojson')
austin_network_df <- austin_network %>% st_drop_geometry()
write.csv(austin_network_df, 'austin_hpms_inventory.csv')
