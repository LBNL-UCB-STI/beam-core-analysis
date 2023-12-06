library(sf)
library(dplyr)
library(data.table)
library(RColorBrewer)

file_link <- '/Volumes/GoogleDrive/My Drive/BEAM-CORE/BEAM Validation/sample output/Oakland2021/'

beam_network_out <- st_read(paste0(file_link, "beam_network_by_county_oak.geojson"))
link_stats <- read.csv(paste0(file_link, 'processed_linkstats.csv'))

beam_network_with_stats <- merge(beam_network_out, link_stats, by.x = c('linkId', 'fromNodeId', 'toNodeId'), 
                                 by.y = c('linkId', 'fromNodeId', 'toNodeId'), all.x=FALSE)

myPal<-brewer.pal(8, "RdBu")
breaks = c(0, 10, 20, 30, 40, 50, 60, 70, 80)
ats = c(0, 10, 20, 30, 40, 50, 60, 70, 80)

for (hour in 1:24){
  print(hour)
  pic_file = paste0(file_link, 'plot/sf_speed_', hour, '.png')
  png(pic_file, width = 500, height = 400)
  speed_attr = paste0('speed_', hour)
  main_title = paste0('Network speed (mph) from hour = ', hour)
  plot(beam_network_with_stats[,speed_attr], main = main_title,
       lwd = 0.5, pal = myPal, breaks = breaks, at = ats)
  dev.off()
  #break
}


myPal<-rev(brewer.pal(8, "RdBu"))
breaks = c(0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4)
ats = c(0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4)

# roadway_type <- c('motorway_link', 'tertiary', 'secondary', 'trunk', 'secondary_link', 'trunk_link', 
#                   'primary_link', 'motorway', 'primary', 'tertiary_link')
# beam_network_with_cars <- beam_network_with_stats %>% filter(attributeOrigType %in% roadway_type)

for (hour in 1:24){
  print(hour)
  
  pic_file = paste0(file_link, 'plot/sf_volume_', hour, '.png')
  png(pic_file, width = 500, height = 400)
  volume_attr = paste0('volume_', hour)
  main_title = paste0('Network volume (veh/hr) from hour = ', hour)
  plot(beam_network_with_stats[,volume_attr], main = main_title,
       lwd = 0.5, pal = myPal, logz = TRUE, breaks = breaks, at = ats)
  dev.off()
  #break
}
