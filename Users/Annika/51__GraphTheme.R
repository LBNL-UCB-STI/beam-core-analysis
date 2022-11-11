# ~~~~~~~~~~~~~~~~~~~~~Graph Theme~~~~~~~~~~~~~~~~~~~~~
theme_set(theme_light(base_size = 11)) # make ALL font based on this
## Title ##
theme_update(
      plot.title =
            element_text(
                  face = "bold",
                  margin = margin(0, 0, -100, 0),
                  # size = 26,
                  # family = "KyivType Sans",
                  vjust = 0,
                  color = "grey25"
            ))
## LEGENDS ##
theme_update(
      legend.justification = "center",
      legend.position = "right",
      # legend.title = element_blank(),
      legend.title = element_text(size = 7,
                                 color = "grey30"),
      # legend.text  = element_text(face = "green"),
      # +
      #   scale_color_vibrant() +
      #   scale_fill_vibrant()
      # Top-right position)
      legend.direction = "vertical", # Elements within a guide are placed one on top of other in the same column
      legend.box = "horizontal" # Different guides-legends are stacked horizontally
)
## AXIS ##
theme_update(# Light background color
      # plot.background = element_rect(fill = "#F5F4EF", color = NA),
      # plot.margin = margin(20, 30, 20, 30),
      # Customize the title. Note the new font family and its larger size.
      plot.caption = element_text(size = 8),
      # Remove titles for x and y axes.
      # axis.title = element_blank(),
      # Specify color for the tick labels along both axes
      axis.text = element_text(color = "grey40",
                               size = 8),
      # Axis titles
      axis.title = element_text(color = "grey40",
                                size = 8),
      # Specify face and color for the text on top of each panel/facet
      strip.text = element_text(face = "bold", color = "grey20")
)
## SUZE AND ASPECT RATIO
theme_update(
      aspect.ratio=.9
)


