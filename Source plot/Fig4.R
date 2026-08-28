library(ggplot2)

load("fig4.RData")

plot_p <- function(df, type, y_label, y_tick = TRUE, cenline=FALSE) {
  df$Time_num <- c(1, 1.7, 3, 1, 1.7, 3)
  p <- ggplot(df, aes(x = Time_num, y = Mean, group = Group, color = Group)) +
    geom_errorbar(aes(ymin = lower, ymax = upper),width = 0.06,linewidth = 1.0) +
    geom_line(linewidth = 1.6) +
    geom_point(size = 10)+
    labs(x = "",y = y_label,color = "") +
    theme_minimal(base_size = 11) +
    theme(
      legend.position = "none",
      panel.grid = element_blank(),
      axis.text.y = element_blank(),
      axis.ticks.y = element_blank(),
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      axis.title.x = element_blank(),
      axis.title.y = element_text(size = 30, color = "black", margin = margin(r = 30)),
      plot.margin = if (y_tick) margin(t = 60, r = 5, b = 50, l = 5) else margin(t = 60, r = 55, b = 50, l = 50),
      text = element_text(face = "plain"),
      panel.background = element_rect(fill = "transparent", colour = NA),
      plot.background = element_rect(fill = "transparent", colour = NA),
    ) +
    coord_cartesian(ylim = c(0, 10),clip = "off")+
    annotate("text",x = 1,y = -0.5,label = "2 weeks",size = 10,fontface = "plain")+
    annotate("text",x = 1.7,y = -0.5,label = "4 weeks",size = 10,fontface = "plain")+
    annotate("text",x = 3,y = -0.5,label = "8 weeks",size = 10,fontface = "plain")+
    annotate("text",x = 2,y = 9.5,label = type,size = 10,fontface = "plain")

  if (y_tick) {
    p <- p+
      annotate("text",x = 0.5,y = seq(0,10,2),label = seq(0,10,2),hjust = 1,size = 10)+
      geom_segment(aes(y = -0.5, yend = 10.5, x = 0.6, xend = 0.6),color = "black",linewidth = 0.5) +
      geom_segment(data = data.frame(x = 0.6,xend = 0.55,y = seq(0, 10, 2),yend = seq(0, 10, 2)),
        aes(x = x, xend = xend, y = y, yend = yend),color = "black",linewidth = 0.5,inherit.aes = FALSE)+
      scale_color_manual( values = c("SheeZan" = "#F4B43F","Usual" = "#8FA0B3"))
  }else {
    p <- p+scale_color_manual(values = c("SheeZan" = "#D55E00","Usual" = "#253858"))
  }

  return(p)
}

p_an_all <- plot_p(an_all, "Overall", "Reduction in GAD-7")
p_an_pos <- plot_p(an_pos, "Screening  positive", " ", y_tick = FALSE, cenline=TRUE)
p_de_all <- plot_p(de_all, "Overall", "Reduction in PHQ-9")
p_de_pos <- plot_p(de_pos, "Screening  positive", " ", y_tick = FALSE, cenline=TRUE)



legend_df1 <- data.frame(label = c("SheeZan","Usual"),col = c("#F4B43F","#8FA0B3"),x = c(0.6, 0.6),y = c(1.6, 1.2))
legend_df2 <- data.frame(label = c("SheeZan positive","Usual positive"),col = c("#D55E00","#253858"),x = c(0.6, 0.6),y = c(1.6, 1.2))

p_legend <- function(legend_df) {
  p <- ggplot(legend_df) +
    geom_segment(aes(x = x,xend = x + 0.15,y = y,yend = y,color = label),linewidth = 1.2) +
    geom_point(aes(x = x + 0.075,y = y,color = label),size = 3.8) +
    geom_text(aes(x = x + 0.25,y = y,label = label),hjust = 0,size = 7) +
    scale_color_manual(values = setNames(legend_df$col,legend_df$label)) +
    theme_void() +
    coord_cartesian(xlim = c(0.5, 3),ylim = c(0.4, 2.1),clip = "off") +
    theme(legend.position = "none",plot.margin = margin(5,5,5,5))
  return(p)
}
legend1 <- p_legend(legend_df1)
legend2 <- p_legend(legend_df2)

dashed_line <-ggplot() +
    geom_segment(aes(x = 0, xend = 0.7, y = 0, yend = 0),linetype = "dashed",linewidth = 1,color = "grey") +theme_void()
