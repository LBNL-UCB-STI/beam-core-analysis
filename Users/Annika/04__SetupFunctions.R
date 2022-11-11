
### THESE ARE DEFINITIONS OF PARAMETERS

# Parameters
### Get titles for any table, graph, results of any ind


fx_proper_Names <- function(master_CSV_file = description_CSV, parameters=params) {
    paramsT <- data.table::transpose(as.data.frame.list(parameters), 
                                     keep.names = "type_title"  )
    descr <- full_join(paramsT,master_CSV_file) 
    descr <- descr |> 
        relocate("type", "title") |> 
        filter(V1 != FALSE | type_title=="generic_plot") |> 
        filter(!is.na(title) & !is.na(title_short) & !is.na(type))
    categoryTitleShort <<-    as.character(filter(descr, type == "category")["title_short"])
    leverTitleShort <<-    as.character(filter(descr, type == "lever")["title_short"])
    categoryTitleLong <<-    as.character(filter(descr, type == "category")["title"])
    leverTitleLong <<-    as.character(filter(descr, type == "lever")["title"])
    year <<-    as.character(filter(descr, type == "year")["title"])
    place <<-    as.character(filter(descr, type == "place")["title"])
    placeTitleShort <<-    gsub(" ", "", as.character(filter(descr, type == "place")["title_short"]))
    leverLevels <<-    as.character(filter(descr, type == "lever")["leverLevels"][1])
    
    descr <<- descr
    print("")
    print("Description: ")
    print(glue("Scenario: {categoryTitleLong} ({categoryTitleShort}), 
                levers: {leverTitleLong} ({leverTitleShort})
                Levels: {leverLevels}")) 
    print(descr |> select("type", "title", "variable") |> filter(type == "yvar"))
    print(descr |> select("type", "title") |> 
        filter(type != "yvar" & type != "hetvar")) 
    listY <- descr |> filter(type == "yvar")
    listY <<- as.list(listY$variable)
    listYnames <- descr |> filter(type == "yvar")
    listYnames <<- paste(as.list(listY$title)  , collapse = ",  ")
    listHet  <- descr |> filter(type == "hetvar")
    listHet <<- as.list(listHet$variable) 
    listHetnames  <- descr |> filter(type == "hetvar")
    listHetnames <<- paste(as.list(listHet$title) , collapse = ",  ")
    # yVarsStr <- paste(listY, collapse="  ")
    # yVarsStr <<- yVarsStr 
    # hetVarsStr <- paste(listHet, collapse="  ")
    # hetVarsStr <<- hetVarsStr 
    
    return(descr)
    
}

# TEST
# fx_proper_Names()

###########################################################3333
###########################################################3333
###########################################################3333
###########################################################3333
###########################################################3333
###########################################################3333
###########################################################3333
# OPEN DATA
###########################################################3333
###########################################################3333
###########################################################3333
###########################################################3333
## First, decide if we want AWS or local. Then make a List of all files -- either from AWS or locally, then (put into a dataset):

fx_tell_me_what_data_file_to_open <- function(
    useAWS=useAWStoReadWrite,scenario="",category="",lever=leverTitleShort) {
    if(params$useAWStoReadWrite==TRUE) {
        library(aws.s3)
        library(dbplyr) # to get from aws
        aws_prefix <- "deepDive/CleanData/SanFrancisco"
        Sys.setenv("AWS_DEFAULT_REGION"="us-east-2", TZ='GMT')
        awsDF <- get_bucket_df("beam-core-act", prefix = aws_prefix) # dataframe with all of the AWS files
        dataframe_of_files <- awsDF
    } else {
        dataframe_of_files <- as_tibble(list.files(path = paste0(
                              data_dir_on_this_machine,"ReadyForAnalysis/"),
                              full.names=TRUE )) |> 
        rename(Key = value)
    }
#List of files for this city (either locally or on AWS), and the stacked ones, that are not the previous files

    data_file_list_paths <- dataframe_of_files |> select(Key)
    data_file_list_paths <- data_file_list_paths |> 
              filter(grepl(pattern = "*.tacked*.",x = Key, ignore.case = TRUE))
    data_file_list_paths <- data_file_list_paths |> 
              filter(!grepl(pattern = "*.revious*.",x = Key, ignore.case = TRUE))
    # print(data_file_list_paths)
    data_file_list_paths <- data_file_list_paths |> 
              filter(grepl(pattern = paste0("*",placeTitleShort,"_","*."),
                           x = Key, ignore.case = TRUE))
    print(data_file_list_paths)
    
# Of those, the smaller List of files for this specific scenario (defined in YAML) (either locally or on AWS) . Hopefully there will be one cleaned, one cleaned subset, and one raw: , and cleaned stacked if there is one: wantSUBSETofTheVARSinsteadofAll
      data_file_list_paths <- data_file_list_paths |> 
          filter(grepl(pattern = paste0("*.",categoryTitleShort,
                                        "_",leverTitleShort),
                       x = Key, ignore.case = TRUE))
        print(data_file_list_paths)
# The list of cleaned, ready for analysis files
# not including the words old or previous
        data_file_list_analysis <- data_file_list_paths |> 
          filter(!grepl(pattern = "*.old*",x = Key, ignore.case = TRUE)) |>
          filter(!grepl(pattern = "*.previous*",x = Key, ignore.case = TRUE))  |>
          filter( grepl(pattern = "*.eadyForAnalysis*",x = Key, ignore.case = TRUE))
        data_file_list_paths <<- data_file_list_paths 
        data_file_list_analysis <<- data_file_list_analysis
        print(data_file_list_analysis)
        data_file_string_analysis <<- data_file_list_analysis$Key
        print("opening this file")
        print(data_file_string_analysis)
        return(data_file_list_analysis)
}

    
# fx_open_data()

###########################################################3333
###########################################################3333
###########################################################3333
###########################################################3333
###########################################################3333
###########################################################3333
###########################################################3333
###########################################################3333
###########################################################3333
### .


# New Vars

fx_incomeVars <- function(df_temp = df_temp) {
  df_temp <- df_temp |>
  mutate(income10levels = ntile(income_in_thousands,10))
df_temp <- df_temp  %>%
  mutate(l_inc_HiLo10 = as_factor( case_when(
    income10levels == 1 ~ "Bottom 10% Income ",
    income10levels == 10 ~ "Top 10% Income" )))
}

fx_car_ownership <- function(df_temp=df_temp) {
df_temp <- df_temp |> 
  mutate(ownCarYN = as.logical(case_when(
    auto_ownership >= 1 ~ TRUE,
    auto_ownership == 0 ~ FALSE )))
df_temp |> group_by(auto_ownership) |> summarise(n = n(), yn = mean(ownCarYN))
ungroup(df_temp)
}

fx_mode_choice <- function(df_temp = df_temp) {
levels(df_temp$mode_choice_actual_BEAM)
df_temp <- df_temp  %>%
  mutate(      mode_rh = as_factor(case_when(
    mode_choice_actual_BEAM == "ride_hail_pooled" ~ "Ride Hail Pooled",
    mode_choice_actual_BEAM == "ride_hail" ~ "Ride Hail Not-Pooled",
    mode_choice_actual_BEAM == "ride_hail_transit" ~ "Ride Hail Transit"
  )))
# With the small one?
knitr::kable(df_temp  |> count(mode_choice_actual_6,mode_choice_actual_BEAM))
df_temp <- df_temp  %>%
  mutate(
    mode_4categories = as_factor(
      case_when(
        mode_choice_actual_6 == "bike" ~ "Walk or Bike",
        mode_choice_actual_6 == "walk" ~ "Walk or Bike",
        mode_choice_actual_6 == "ride_hail" ~ "Ride Hail",
        mode_choice_actual_6 == "ride_hail_transit" ~ "Transit",
        mode_choice_actual_6 == "car" ~ "Car",
        mode_choice_actual_6 == "transit" ~ "Transit",
        TRUE ~ as.character(mode_choice_actual_6)
      )))
df_temp <- df_temp  %>%
  mutate(
    mode_planned_5 = as_factor(
      case_when(
        mode_choice_planned_BEAM == "bike"              ~ "Walk or Bike",
        mode_choice_planned_BEAM == "walk"              ~ "Walk or Bike",
        mode_choice_planned_BEAM == "ride_hail"         ~ "Ride Hail Solo",
        mode_choice_planned_BEAM == "ride_hail_pooled"  ~ "Ride Hail Pooled",
        mode_choice_planned_BEAM == "ride_hail_transit" ~ "Transit",
        mode_choice_planned_BEAM == "drive_transit"     ~ "Transit",
        mode_choice_planned_BEAM == "bike_transit"      ~ "Transit",
        mode_choice_planned_BEAM == "walk_transit"      ~ "Transit",
        mode_choice_planned_BEAM == "transit"           ~ "Transit",
        mode_choice_planned_BEAM == "car"                ~ "Car",
        mode_choice_planned_BEAM == "car_hov2"           ~ "Car",
        mode_choice_planned_BEAM == "car_hov3"           ~ "Car",
        mode_choice_planned_BEAM == "hov2_teleportation" ~ "Car",
        mode_choice_planned_BEAM == "hov3_teleportation" ~ "Car",
        TRUE ~ as.character(mode_choice_planned_BEAM)
      )))
df_temp |> count(mode_planned_5)



df_temp <- df_temp  %>%
  mutate(
    mode_5catPooled = 
      case_when(
        mode_choice_actual_BEAM == "ride_hail_pooled" ~ "Ride Hail Pooled",
        mode_choice_actual_BEAM == "ride_hail_transit" ~ "Transit",
        mode_choice_actual_BEAM == "ride_hail" ~ "Ride Hail Not-Pooled",
        TRUE ~ as.character(mode_4categories)
      ))
knitr::kable(df_temp  |> count(mode_choice_actual_BEAM,
                               mode_choice_actual_6,
                               mode_5catPooled,
                               mode_4categories))
}

