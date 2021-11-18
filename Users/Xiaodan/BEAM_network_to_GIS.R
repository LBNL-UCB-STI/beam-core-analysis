library(sf)
library(dplyr)
library(data.table)
file_link <- '/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/sample output/'
beam_network <-read.csv(paste0(file_link, 'network.csv'))
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
st_write(beam_network_out, paste0(file_link, "beam_network_out.geojson"))
