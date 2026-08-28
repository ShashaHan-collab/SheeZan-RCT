library(ggnewscale)
library(ggplot2)
library(tibble)
library(dplyr)

load("fig5.RData")

## a panel
error_group <- c("Voice + Text" = "#8B6FC0","Text only" = "#4C78A8")
plot_pa <- function(df, y_label=FALSE, legend=FALSE, y_tick=TRUE) {
  df$error_group <- df$group
  df$group <- factor(df$group,levels = c("Voice + Text", "Text only"))
  x_pos = 1.35
  y_pos = 65
  p <- ggplot(df, aes(x = time, y = p, group = group))+
    geom_col(aes(fill = group, color = group),width = 0.55,position = position_dodge(width = 0.65),linewidth = 1.8)+
    labs(x = "", y = if (y_label) "Proportion (%)" else "") +
    scale_y_continuous(breaks = seq(0, 100, 20)) +
    scale_color_manual(values = c("Voice + Text" = "#C7B9E7","Text only" = "#9ABBDD"),
                       labels = c("Voice + Text        ", "Text only")) +
    scale_fill_manual(values = c("Voice + Text" = "#C7B9E7","Text only"= "#9ABBDD"),
                      labels = c("Voice + Text        ", "Text only")) +
    geom_segment(aes(y = -3, yend = -3, x = 1-0.45/2-0.05, xend = x_pos-0.075), color = "black",linewidth=0.5)+
    theme_minimal(base_size = 11) +
    theme(
      legend.position = "none",
      panel.grid = element_blank(),
      axis.text.y = element_blank(),
      axis.ticks.y = element_blank(),
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      axis.title.x = element_blank(),
      axis.title.y = element_text(size = 30, color = "black", margin = margin(r = 50)),
      plot.margin = if (y_label) margin(t = 0, r = 160, b = 10, l = 165) else margin(t = 0, r = 175, b = 10, l = 165),
      text = element_text(face = "plain"),
      panel.background = element_rect(fill = "transparent", colour = NA),
      plot.background = element_rect(fill = "transparent", colour = NA),
    ) +
    annotate("text",x = 1,y = 85,label = df$time[1],size = 10,fontface = "plain")+
    coord_cartesian(ylim = c(0, 100),clip = "off")+
    new_scale_color()+
    geom_errorbar(aes(ymin = lower, ymax = upper, color = error_group),width = 0.05,linewidth = 1.5,
                  position = position_dodge(width = 0.65))+
    scale_color_manual(values = error_group)

  if (y_tick) {
    p <- p +
      geom_segment(aes(y = 0, yend = 100, x = 0.6, xend = 0.6),color = "black",linewidth = 0.5) +
      geom_segment(data = data.frame(x = 0.6,xend = 0.55,y = seq(0, 100, 20),yend = seq(0, 100, 20)),
                   aes(x = x, xend = xend, y = y, yend = yend),color = "black",linewidth = 0.5,inherit.aes = FALSE)+
      annotate("text",x = 0.5,y = seq(0,100,20),label = seq(0,100,20),hjust = 1,size = 10)
  }
  return(p)
}

p_a4 <- plot_pa(df4, y_label=TRUE)
p_a8 <- plot_pa(df8, y_label=F, y_tick=F)

legend_items <- tribble(
  ~label,                  ~fill,       ~color,
  "Voice + Text",      "#C7B9E7",   "#C7B9E7",
  "Text only", "#9ABBDD",   "#9ABBDD"
)

legend_items$x_tile <- c(1, 1)
legend_items$y_tile <- c(1.3, 1.0)

p_legenda <- ggplot(legend_items, aes(x = x_tile, y = y_tile)) +
  geom_tile(aes(width = 0.13,height = 0.13,fill = fill,color = color),linewidth = 0) +
  geom_text(aes(x = x_tile + 0.13,y = y_tile,label = label),hjust = 0,vjust = 0.5,size = 8) +
  scale_fill_identity() +
  scale_color_identity() +
  theme_void() +
  xlim(0.5, 3.5) +
  ylim(0.5, 1.5)



## b panel
plot_pb <- function(df, y_label) {
  df$Time_num <- recode(df$Time,"2 weeks" = 1,"4 weeks" = 1.7,"8 weeks" = 3)
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
      plot.margin = margin(t = 0, r = 35, b = 10, l = 25),
      text = element_text(face = "plain"),
      panel.background = element_rect(fill = "transparent", colour = NA),
      plot.background = element_rect(fill = "transparent", colour = NA),
    ) +
    coord_cartesian(ylim = c(0, 10),clip = "off")+
    annotate("text",x = 1,y = -0.5,label = "2 weeks",size = 10,fontface = "plain")+
    annotate("text",x = 1.7,y = -0.5,label = "4 weeks",size = 10,fontface = "plain")+
    annotate("text",x = 3,y = -0.5,label = "8 weeks",size = 10,fontface = "plain")+
    scale_color_manual(
      values = c("Voice" = "#8B6FC0","Text" = "#4C78A8",
                 "Voice positive" = "#8d198d","Text positive" = "#0000b3"))+
    annotate("text",x = 0.5,y = seq(0,10,2),label = seq(0,10,2),hjust = 1,size = 10)+
    geom_segment(aes(y = -0.5, yend = 10.5, x = 0.6, xend = 0.6),color = "black",linewidth = 0.5) +
    geom_segment(data = data.frame(x = 0.6,xend = 0.55,y = seq(0, 10, 2),yend = seq(0, 10, 2)),
                 aes(x = x, xend = xend, y = y, yend = yend),color = "black",linewidth = 0.5,inherit.aes = FALSE)

  return(p)
}

p_an <- plot_pb(an, "Reduction in GAD-7")
p_de <- plot_pb(de, "Reduction in PHQ-9")

legendb_df1 <- data.frame(label = c("Voice + Text","Text only "),col = c("#8B6FC0","#4C78A8"),x = c(0.6, 0.6),y = c(1.7, 1.2))
legendb_df2 <- data.frame(label = c("Voice + Text  positive","Text only positive"),col = c("#8d198d","#0000b3"),x = c(0.6, 0.6),y = c(1.7, 1.2))

p_legendb <- function(legend_df) {
  p <- ggplot(legend_df) +
    geom_segment(aes(x = x,xend = x + 0.15,y = y,yend = y,color = label),linewidth = 1.2) +
    geom_point(aes(x = x + 0.075,y = y,color = label),size = 3.8) +
    geom_text(aes(x = x + 0.25,y = y,label = label),hjust = 0,size = 8) +
    scale_color_manual(values = setNames(legend_df$col,legend_df$label)) +
    theme_void() +
    coord_cartesian(xlim = c(0.5, 3),ylim = c(0.4, 2.1),clip = "off") +
    theme(legend.position = "none",plot.margin = margin(5,5,5,5))
  return(p)
}
legendb1 <- p_legendb(legendb_df1)
legendb2 <- p_legendb(legendb_df2)

