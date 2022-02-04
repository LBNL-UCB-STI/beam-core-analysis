library(sf)
library(dplyr)
library(data.table)
file_link <- '/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/sample output/SFB2010/'
beam_network <-read.csv(paste0(file_link, 'network.csv.gz'))
beam_network_onode_sf = st_as_sf(beam_network, coords = c('fromLocationX', 'fromLocationY'), 
                                crs = 26910, agr = "constant")
beam_network_onode_sf <- beam_network_onode_sf %>% select(linkId,  linkLength, linkFreeSpeed, linkCapacity, numberOfLanes, linkModes, attributeOrigId,
attributeOrigType, fromNodeId, toNodeId)
plot(st_geometry(beam_network_onode_sf))
beam_network_dnode_sf = st_as_sf(beam_network, coords = c('toLocationX', 'toLocationY'), 
                                 crs = 26910, agr = "constant")
beam_network_dnode_sf <- beam_network_dnode_sf %>% select(linkId,  linkLength, linkFreeSpeed, linkCapacity, numberOfLanes, linkModes, attributeOrigId,
                                 attributeOrigType, fromNodeId, toNodeId)


pair <- rbind(beam_network_onode_sf, beam_network_dnode_sf)
line <- pair %>% 
  group_by(linkId)  %>% 
  summarize(linkLength = mean(linkLength), linkFreeSpeed = mean(linkFreeSpeed), linkCapacity = mean(linkCapacity), 
            numberOfLanes = mean(numberOfLanes), linkModes = first(linkModes), attributeOrigId = first(attributeOrigId),
            attributeOrigType = first(attributeOrigType), fromNodeId = mean(fromNodeId), toNodeId = mean(toNodeId), do_union = FALSE) %>% 
  st_cast("LINESTRING")

plot(st_geometry(line))

beam_network_out <- st_transform(line, crs = 4326)
st_write(beam_network_out, paste0(file_link, "beam_network_out.geojson"), append=FALSE)


#### clean up beam network and assign county ####

beam_network_out <- st_read(paste0(file_link, "beam_network_out.geojson"))
sf_boundary <- st_read('/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/data for validation/SF/SF_counties.geojson')
sf_boundary <- st_transform(sf_boundary, 4326)

beam_network_splits <- st_intersection(beam_network_out, sf_boundary)
# beam_network_splits$length <- st_length(beam_network_splits)
plot(st_geometry(sf_boundary), border = 'blue')
plot(st_geometry(beam_network_splits), add = TRUE)

beam_network_splits <- beam_network_splits %>%
  select(linkId, linkLength, linkFreeSpeed, linkCapacity, numberOfLanes, linkModes, 
         attributeOrigId, attributeOrigType,
         fromNodeId, toNodeId, GEOID, NAME, NAMELSAD, CLASSFP)

beam_network_splits <- beam_network_splits %>% filter(linkLength > 0.001)
plot(beam_network_splits[, 'NAME'], axes = TRUE, key.pos = 4, key.width = lcm(4.5))

beam_network_splits_df <- beam_network_splits %>% st_drop_geometry()
write.csv(beam_network_splits_df, paste0(file_link, "beam_network_by_county.csv"))
st_write(beam_network_splits, paste0(file_link, "beam_network_by_county.geojson"))
