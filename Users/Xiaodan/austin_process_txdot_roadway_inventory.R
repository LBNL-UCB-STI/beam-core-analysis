library(sf)
library(dplyr)

setwd("/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/Austin")

texas_network <- st_read('TxDOT_Roadway_Inventory_2018/TxDOT_Roadway_Inventory_Linework_wAssets.shp')
list_of_attribute <- colnames(texas_network)
texas_network <- texas_network %>% 
  select(REC, HSUF, DIR_TRAV, STE_NAM, DI, CO, CITY, MPA, RU, ADMIN, F_SYSTEM, RU_F_SYSTE,
         SEC_TRK, SEC_BIC, FRGHT_NTWR, HWY_STAT, SPD_MAX, SPD_MIN, TOLL_NM, TOLL_FACIL, TOLL_LANE_,
         NUM_LANES, ADT_YEAR, ADT_CUR, ADT_ADJ, TRK_AADT_P, AADT_TRUCK, LEN_SEC, LN_MILES, DVMT, DTRKVMT)
network_crs <- st_crs(texas_network)

austin_boundary <- st_read('austin_counties.shp')
austin_boundary <- st_transform(austin_boundary, network_crs)

list_of_austin_countie <- unique(austin_boundary$name)
tx_county_code <- read.csv('txdot_county_code.csv')
austin_county_code <- tx_county_code %>%
  filter(County.Name %in% list_of_austin_countie)

list_of_austin_code <- unique(austin_county_code$TxDOT.County.Code)
austin_network <- texas_network %>%
  filter(CO %in% list_of_austin_code)
austin_network <- merge(austin_network,y=austin_county_code,by.x= 'CO', by.y = 'TxDOT.County.Code', all.x=TRUE)
plot(st_geometry(austin_boundary), border = 'blue')
plot(st_geometry(st_zm(austin_network)), add = TRUE)

st_write(austin_network, 'txdot_austin_inventory.geojson')
