
# Read in files
library(readr)
library(aws.s3)
library(dbplyr) # to get from aws
library(fst) # open and close files

# Data wrangling
library(tidyverse)
library(glue)
library(stringr) # for strings
library(codebookr) # codebook?

# Display graphs and tables
library(ggplot2)
# library(gt)  # tables but doesn't really work
library(khroma)
library(ggridges)
library(patchwork) # lay out plots next to each other
library(Hmisc)
library(purrr)
library(dplyr)
library(glue)
library(readr)
library(forcats)
library(aws.s3) # to open aws
library(dbplyr) # to open aws
# library(tikzDevice) # to get really really good looking things use dev tikz
# library(kableExtra)
# library(Cairo)
# library(tinytex)
# library(reader)
# cairo_null_device(4, 3.2)
# library(flextable)
# library(magick)
# library(patchwork)
# library(flexdashboard)
# library(ggExtra) # marginal plots
# library(ggrepel) # make labels not overlap
# library(cowplot) 
# library(scales)
# library(plotly) # make interactive!
# library(Hmisc)
# library(stargazer)
# library(svglite)
# library(dplyr)
# library(tidyverse)
# library(ggplot2)
# library(gghighlight)    # highlight one part of plot
# library(usethis)
gc()
print("Attached packages")
print(.packages())

