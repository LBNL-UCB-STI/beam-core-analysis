# ---
# title: "Tables Stats functions"
# format: html
# ---

## Tables

# ```{r}
# listleverLevels <- as.list(levels(as_factor(df_temp$lever_position)))
# as.character(listleverLevels)
#   knitr::kable(levels(as_factor(df_temp$lever_position)))
# 
#   knitr::kable(df_temp  |> count(auto_ownership, ownCarYNLabel))
# 
#   
#   knitr::kable(df_temp  |> group_by(lever_position) |> 
#           count(ownCarYNLabel))
#   knitr::kable(df_temp  |>
#           filter(lever_position==1) |> 
#           group_by(lever_position,l_inc_HiLo10) |> 
#           count(ownCarYNLabel, mode_4categories))
#                 
#   knitr::kable(
#     df_temp  |>
#           filter(lever_position==1) |> 
#           group_by(income10levels) |> 
#           summarise(pot = mean(Potential_INEXUS_in_dollar),
#                   timeDtoD = mean(duration_door_to_door),
#                   time = mean(duration),
#                   modecar = mean(mode_4categories=="Car"),
#           modePub = mean(mode_4categories=="Transit"),
#           modeRH = mean(mode_4categories=="Ride Hail"),
#           modeWalkB = mean(mode_4categories=="Walk or Bike")
#           ))
#   knitr::kable(df_temp  |> group_by(lever_position) |> 
#           count(ownCarYNLabel))
  
  
  # print(levels(df_temp$mandatoryType))
  # print(levels(df_temp$mandatoryCat))
  

# ```

### descr?

# ```{r}
# print(levels(df_temp$mandatoryType))
#   print(levels(df_temp$mandatoryCat))
#   print(df_temp |> count(mandatoryCat))
  # print(levels(as_factor(df_temp$income10levels)))
  # print(df_temp |> count(income10levels))
  # print(levels(as_factor(df_temp$ownCarYNLabel)))
  # print(df_temp |> count(ownCarYNLabel))
  # print(df_temp |> count(auto_ownership))
  # print(levels(df_temp$l_inc_HiLo10))
  # print(df_temp |> count(mode_choice_actual_6))
  # print(levels(df_temp$incomeXcar))
  # print(df_temp |> count(mode_choice_actual_6))
  # print(levels(df_temp$mode_4categories))
  # print(df_temp |> count(mode_4categories))
  # print(levels(df_temp$mode_choice_actual_6))
  # print(df_temp |> count(mode_choice_actual_6))
  # print(levels(df_temp$scenario))
  
  
  # print(levels(df_temp$category))
# ```



# ```{r ..}
# knitr::knit_exit()
# ```

