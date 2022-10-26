# ---
# title: "Graph Functions"
# format: html
# ---


# Graph functions

# To do functions we setup a blank df, maybe df_temp

### functions then test

# Get titles for any graph

# ```{r fx_g0_titles, echo=TRUE}
fx_get_TitlesLevels_createBaseGraph_g0 <- function(df="none",y_var="generic",het="none",tit="none") {
  tmp_yvarTitleLong <<-    filter(descr,variable == y_var)[["title"]]
  tmp_yvarTitleShort <<-   filter(descr,variable == y_var)[["title_short"]]
  tmp_hetvarTitleLong <<-  filter(descr,variable == het)[["title"]]
  tmp_hetvarTitleShort <<- filter(descr,variable == het)[["title_short"]]
  tmp_yvarLOW <<-          filter(descr, variable == y_var)[["scaleLow"]]
  tmp_yvarHI <<-           filter(descr, variable == y_var)[["scaleHigh"]]
  print(tmp_yvarLOW)
  print(tmp_yvarHI)
  
# TITLE
  tmp_graphTitle <<- str_glue("{year} {categoryTitleLong} {leverTitleLong}; Outcome: {tmp_yvarTitleLong}")
    print(paste("y:",tmp_yvarTitleLong,tmp_yvarTitleShort,"het:", tmp_hetvarTitleLong,tmp_hetvarTitleShort))
# BASE BLANK plot. Use coordinate limits (scales) set by the 95% 
  tmp_g0 <- ggplot() +
    coord_cartesian(xlim = c(tmp_yvarLOW,tmp_yvarHI)) +
    labs(title = tmp_graphTitle) +
    labs(subtitle = str_glue("Heterogeneity: {tmp_hetvarTitleLong}")) +
    xlab(tmp_yvarTitleLong) + 
    ylab(" density ") +
    theme(aspect.ratio=.9)  # makes most of the graphs a little more than square
return(tmp_g0)
}
print("Defining Titles from Description File...")
print("........................................fx_g0_titles")
# ```

### test

# ```{r TEST_a, eval=FALSE, include=FALSE}
# Testing fx_get_TitlesLevels_createBaseGraph_g0
# y_var = "Potential_INEXUS_in_dollar"
#           g0tmp <- fx_get_TitlesLevels_createBaseGraph_g0(
#             y_var = "Potential_INEXUS_in_dollar")
# print(g0tmp)
# ```

# Distribution curves

## Distribution: Sub-graph

# ```{r fx_Total}
fx_graph_the_TotalDistribution <-   function(df, y_var,het = "none",nm = "n",tit = "noTitle",           ...) {
# Drop missing
    if (het != "none") { df <- df |> drop_na(paste0(het))
                  captionText <- glue("Note: dropping missing values for {het}") }     # drop obs that are missing the het var
# Base graph -- get titles etc  
    g0 <- fx_get_TitlesLevels_createBaseGraph_g0(y_var=y_var,df=df,het=het,tit=tit)
# Graph
    gseparate <- map(listleverLevels, function(.x) {
            g0 + labs(subtitle = str_glue("{leverTitleLong} {.x}")) +
            geom_density(data = df |> filter(lever_position==.x),
            mapping = aes(x = .data[[y_var]]),
            fill = "grey",color = "grey",alpha = .6    )  }  )
    gwrapped <- wrap_plots(gseparate) + plot_annotation(
            title = tmp_graphTitle,caption = captionText,
            tag_levels = 'a', tag_prefix = '   (', tag_suffix = ')') &
            theme(plot.tag.position = c(0, 1), plot.tag = element_text(size = 8, hjust = 0, vjust = 0)) &
            labs(title = "")
# Return    
    return(list(gwrapped = gwrapped,gseparate = gseparate))
    print(gwrapped)
}
print("Graph the total distribution...")
print("............................... fx_graph_the_TotalDistribution")
# ```

#### test

# ```{r TEST_b, eval=FALSE, include=FALSE}
# testing fx_graph_the_TotalDistribution
# g3 <- fx_graph_the_TotalDistribution(
#   df=df_temp,
#   y_var = "Potential_INEXUS_in_dollar",
#   het = "l_inc_HiLo10")
# print(g3)
# print(g3[["gwrapped"]])
# ```

## Distribution: Sub-graph

# ```{r fx_het_dist}
fx_graph_Distn_Internal_Heterogeneity <-   function(df, y_var,het = "none",nm = "n",tit = "noTitle",           ...) {
# Drop missing
    if (het != "none") { df <- df |> tidyr::drop_na(paste0(het))  
                  captionText <- glue("Note: dropping missing values for {het}") }     # drop obs that are missing the het var
    g0 <- fx_get_TitlesLevels_createBaseGraph_g0(y_var=y_var,df=df,het=het,tit=tit)
# Graph
    gseparate <- map(listleverLevels, function(.x) {g0 + labs(
            title = str_glue("{tmp_graphTitle}, Heterogeneity: {tmp_hetvarTitleLong} "),
            caption = captionText,
            subtitle = str_glue("{leverTitleLong} at {.x}")) +
            geom_density(data = df |> filter(lever_position==.x),
                         mapping = aes(x = .data[[y_var]],
                                       fill = .data[[het]],
                                       color = .data[[het]],
                                       group = .data[[het]] ), 
                         alpha = .3    )  }  )
    gwrapped <- wrap_plots(gseparate) + plot_annotation(
            title = tmp_graphTitle,caption = captionText,
            tag_levels = 'a', tag_prefix = '   (', tag_suffix = ')') &
            theme(plot.tag.position = c(0, 1), plot.tag = element_text(size = 8, hjust = 0, vjust = 0)) &
            labs(title = "",caption = "")
    gseparate_L <- map(listleverLevels, function(.x) {g0 + labs(
            title = str_glue("{tmp_graphTitle}, Heterogeneity: {tmp_hetvarTitleLong} "),
            caption = captionText,
            subtitle = str_glue("{leverTitleLong} at {.x}")) +
            geom_density(data = df |> filter(lever_position==.x),
                         mapping = aes(x = .data[[y_var]],
                                       fill = .data[["lever_position"]],
                                       color = .data[["lever_position"]],
                                       group = .data[["lever_position"]] ), 
                         alpha = .1    )  }  )
            #scale_fill_binned(guide = guide_colorsteps()) +
    gwrapped_L <- wrap_plots(gseparate_L) + plot_annotation(
            title = tmp_graphTitle,caption = captionText,
            tag_levels = 'a', tag_prefix = '   (', tag_suffix = ')') &
            theme(plot.tag.position = c(0, 1), plot.tag = element_text(size = 8, hjust = 0, vjust = 0)) &
            labs(title = "",caption = "")
  
    return(list(gwrapped = gwrapped,gseparate = gseparate,gseparate_L,gwrapped_L))
    print(c(gwrapped,gseparate,gseparate_L,gwrapped_L))
}
print("Heterogeneity Within One scenario...")
print(".................................... fx_graph_Distn_Internal_Heterogeneity")
# ```

#### test

# ```{r c }
# | eval: false
# | echo: false
# testing fx_graph_Distn_Internal_Heterogeneity
                                  # g3 <- fx_graph_Distn_Internal_Heterogeneity(
                                  #   df=df_temp,
                                  #   y_var = "Potential_INEXUS_in_dollar",
                                  #   het = "incomeXcar")
                                  # print(g3[["gwrapped"]])
# ```

## Distribution: Meta function

# ```{r fx_META_graph_choose}
fx_META_graph_choose <- function(df, y_var, het="none",nm="n",tit="noTitle",
                                 totalGr=TRUE, hetGr=TRUE, saveGraph=TRUE) {
  listofgraphs <- list(graphlist = "initialize")
  # Print total Desnity graph?
  if(totalGr==TRUE) { mgTot <- fx_graph_the_TotalDistribution(df=df,y_var=y_var,het=het,tit=tit) 
                        print(mgTot)
                        listofgraphs <- list_merge(listofgraphs,  mgTot) }
  if(hetGr==TRUE) { mgHet <- fx_graph_Distn_Internal_Heterogeneity(df=df,y_var=y_var,het=het,tit=tit) 
                        print(mgHet)
                        listofgraphs <- list_merge(listofgraphs,mgHet=mgHet) }
  if(saveGraph==TRUE) {   
    # ggsave(filename = paste0("test.svg"), path = figures_folder, width  = dev.size("in")[1], height = dev.size("in")[2])
    # ggsave(filename = paste0("test.png"), path = figures_folder, width  = dev.size("in")[1], height = dev.size("in")[2])
    # ggsave(filename = paste0("test.pdf"), path = figures_folder, width  = dev.size("in")[1], height = dev.size("in")[2])
}
  return(listofgraphs)
}

print("Print all of the graphs you choose, Meta function...")
print(".................................... fx_META_graph_choose")

# ```

#### test

# ```{r d, eval=FALSE, include=FALSE}
# | eval: false
# | echo: false
# testing the meta graph
                            # metag1 <- fx_META_graph_choose(df=df_temp,
                            #                       y_var = "Potential_INEXUS_in_dollar",
                            #                       het = "incomeXcar",
                            #                       totalGr = TRUE,
                            #                       hetGr=TRUE)
                            # print(metag1)
                            # print(metag1$gwrapped)
# ```

# Graph over levers

# ```{r area}
# df_graph_temp <- df_temp |> 
#   group_by(lever_position) |> 
#   rename(`Lever Position` = lever_position) |> 
#   count(mode_5catPooled)
# df_graph_tempTotal <- df_graph_temp |> 
#   mutate(`Total Trips` = sum(n)) |> 
#   mutate(`Percent of Total Trips` = n /`Total Trips` ,
#          n = NULL)
# df_graph_tempTotal <- df_graph_tempTotal |> 
#   pivot_wider(names_from = mode_5catPooled, values_from = `Percent of Total Trips`) 
# print(df_graph_tempTotal)
# ```

# ```{r area2}
fx_graph_mode <- function(df = df_summary1) {
    df_graph_temp <- df
    relative_lever <- min(df_graph_temp$`Lever Position`)
    p1 <- ggplot(df_graph_temp, aes(x = `Lever Position`))
    p1 <- p1 + 
      geom_line(aes(y = `Ride Hail Not-Pooled`  - df_graph_temp$`Ride Hail Not-Pooled`[`Lever Position`==relative_lever], color = "Ride Hail Not-Pooled")) +
      geom_line(aes(y = `Ride Hail Pooled`  - df_graph_temp$`Ride Hail Pooled`[`Lever Position`==relative_lever],     color = "Ride Hail Pooled")) +
      geom_line(aes(y = `Ride Hail Pooled` + `Ride Hail Not-Pooled`  - df_graph_temp$`Ride Hail Pooled`[`Lever Position`==relative_lever]  - df_graph_temp$`Ride Hail Not-Pooled`[`Lever Position`==relative_lever],     
                             color = "All Ride Hail"))
    print(p1)
    p5 <- p1 + geom_line(aes(y = `Walk or Bike` - df_graph_temp$`Walk or Bike`[`Lever Position`==relative_lever], color = "Walk or Bike")) +
               geom_line(aes(y = `Transit` - df_graph_temp$`Transit`[`Lever Position`==relative_lever] , color = "Transit"))
    p5 <- p5 + geom_line(aes(y = `Car`- df_graph_temp$Car[`Lever Position`==relative_lever] , color = "Car"))
    p5 <- p5 +
      theme(legend.position = "right") +
      ylab("Percentage of trips, relative to lowest lever")
    print(p5) 

# a vector of COLORS for legend
# cols <- c("Car MINUS 3000000" = "red", 
#           "Walk or Bike" = "blue", 
#           "Transit" = "darkgreen", 
#           "Ride Hail Pooled" = "orange",
#           "Ride Hail Not-Pooled" = "green")
# p5 + scale_colour_manual(values = cols)
}
# ```
