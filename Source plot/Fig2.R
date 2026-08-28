library(tibble)
library(dplyr)
library(ggplot2)
library(cowplot)
library(grid)

load("fig2.RData")

## a panel
plot_pa <- function(df, y_label=FALSE, legend=FALSE, y_tick=TRUE) {
  x_pos = 1.35
  y_pos = 65
  p <- ggplot(df, aes(x = time, y = p, group = group))+
    geom_col(aes(fill = group, color = group),width = 0.55,position = position_dodge(width = 0.65),linewidth = 1.8)+
    labs(x = "", y = if (y_label) "Proportion (%)" else "") +
    scale_y_continuous(breaks = seq(0, 100, 20)) +
    scale_color_manual(values = c("SheeZan" = "#D88900","Usual" = "#3E4A5C"),
                       labels = c("SheeZan        ", "Usual")) +
    scale_fill_manual(values = c("SheeZan" = "#f6b23a","Usual"= "#bfc4cc"),
                      labels = c("SheeZan        ", "Usual")) +
    geom_segment(aes(y = -3, yend = -3, x = 1-0.45/2-0.05, xend = x_pos-0.075), color = "black",linewidth=0.5)+
    theme_minimal(base_size = 11) +
    theme(
      legend.title = element_blank(),
      legend.position = if (legend) "top" else "none",
      legend.text = element_text(size = 22),
      legend.key.width  = unit(1.0, "cm"),
      legend.key.height = unit(0.8, "cm"),
      panel.grid = element_blank(),
      axis.text.y = element_blank(),
      axis.ticks.y = element_blank(),
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      axis.title.x = element_blank(),
      axis.title.y = element_text(size = 30, color = "black", margin = margin(r = 25)),
      plot.margin = if (y_label) margin(t = 10, r = 160, b = 10, l = 5) else margin(t = 10, r = 175, b = 10, l = 5),
      text = element_text(face = "plain"),
      panel.background = element_rect(fill = "transparent", colour = NA),
      plot.background = element_rect(fill = "transparent", colour = NA),
    ) +
    annotate("text",x = 1,y = 80,label = df$time[1],size = 10,fontface = "plain")+
    coord_cartesian(ylim = c(0, 100),clip = "off")

  if (y_tick) {
    p <- p +
      geom_segment(aes(y = 0, yend = 100, x = 0.6, xend = 0.6),color = "black",linewidth = 0.5) +
      geom_segment(data = data.frame(x = 0.6,xend = 0.55,y = seq(0, 100, 20),yend = seq(0, 100, 20)),
                   aes(x = x, xend = xend, y = y, yend = yend),color = "black",linewidth = 0.5,inherit.aes = FALSE)+
      annotate("text",x = 0.5,y = seq(0,100,20),label = seq(0,100,20),hjust = 1,size = 10)
  }


  if(legend){
    p <- p+
      geom_errorbar(aes(ymin = lower, ymax = upper),color = "black",width = 0.05,linewidth = 1.5,
                    position = position_dodge(width = 0.65))
    legend_all <- get_plot_component(p, "guide-box", return_all = TRUE)
    p <- ggdraw(legend_all[[4]])
  } else {
    p <- p+
      geom_errorbar(aes(ymin = lower, ymax = upper, color=group),width = 0.05,linewidth = 1.5,
                    position = position_dodge(width = 0.65))
  }

  return(p)
}

p_a4 <- plot_pa(dfa4, y_label=TRUE)
p_a8 <- plot_pa(dfa8, y_label=F, y_tick=F)
p_legenda <- plot_pa(dfa4, legend=TRUE)



## b panel
aRR$type <- factor(aRR$type,levels = c("Help-seeking", "Advice adherence"))
aRR$time <- factor(aRR$time,levels = c("8 weeks", "4 weeks"))
BP$type <- factor(BP$type,levels = c("Help-seeking", "Advice adherence"))
BP$time <- factor(BP$time,levels = c("8 weeks", "4 weeks"))
p_aRR <- ggplot(aRR, aes(x = time, y = aRR, color = type)) +
  geom_point(position = position_dodge(width = 0.6), size = 10) +
  geom_errorbar(aes(ymin = CI_low, ymax = CI_high),position = position_dodge(width = 0.6),width = 0.2,linewidth = 0.8) +
  geom_hline(yintercept = 1, linetype = "dashed", color = "black") +
  coord_flip() +
  scale_color_manual(values = c("Help-seeking" = "#D55E00","Advice adherence" = "#0072B2"),
                     labels = c("Help-seeking        ", "Advice adherence")) +
  scale_y_continuous(
    limits = c(0.5, 2.5),
    breaks = seq(0.5, 2.5, 0.5)
  ) +
  theme_classic(base_size = 13) +
  theme(
    legend.position = c(0.75, 1.35),
    legend.direction = "vertical",
    legend.key.height = unit(1.5, "cm"),
    legend.title = element_blank(),
    legend.margin = margin(b = 20),
    legend.key.width = unit(1.5, "cm"),
    legend.text = element_text(size = 22),
    axis.title.y = element_blank(),
    axis.title.x = element_text(size = 30, margin = margin(t = 15)),
    axis.text.x = element_text(size = 30, margin = margin(t = 15)),
    axis.text.y = element_blank(),
    axis.ticks.length.y = unit(0, "cm"),
    axis.ticks.length.x = unit(0.3, "cm"),
    panel.border = element_rect(color = "black", fill = NA),
    plot.margin = margin(t = 80, r = 0, b = 5, l = 5),
    text = element_text(face = "plain"),
    panel.background = element_rect(fill = "transparent", colour = NA),
    plot.background = element_rect(fill = "transparent", colour = NA),
  ) +
  labs(y = "Adjusted rative ratio",title = "")+
  annotate("text",x = 2,y = 0.815,label = "4 weeks",hjust = 1,size = 10)+
  annotate("text",x = 0.95,y = 0.815,label = "8 weeks",hjust = 1,size = 10)+
  guides(color = guide_legend(override.aes = list(size = 5)))

p_BP <- ggplot(BP, aes(x = time, y = BP, color = type)) +
  geom_point(position = position_dodge(width = 0.6), size = 10) +
  geom_errorbar(aes(ymin = CI_low, ymax = CI_high),position = position_dodge(width = 0.6),width = 0.2,linewidth = 0.8) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "black") +
  coord_flip() +
  scale_color_manual(values = c("Help-seeking" = "#D55E00","Advice adherence" = "#0072B2")) +
  scale_y_continuous(limits = c(-10, 40),breaks = seq(-10, 40, 10)) +
  theme_classic(base_size = 13) +
  theme(
    legend.position = "none",
    legend.text = element_text(size = 25),
    axis.title.y = element_blank(),
    axis.title.x = element_text(size = 30, margin = margin(t = 15)),
    axis.text.x = element_text(size = 30, margin = margin(t = 15)),
    axis.text.y = element_blank(),
    axis.ticks.length.y = unit(0, "cm"),
    axis.ticks.length.x = unit(0.3, "cm"),
    panel.border = element_rect(color = "black", fill = NA),
    plot.margin = margin(t = 80, r = 0, b = 5, l = 5),
    text = element_text(face = "plain"),
    panel.background = element_rect(fill = "transparent", colour = NA),
    plot.background = element_rect(fill = "transparent", colour = NA),
  ) +
  labs(y = "Between-group difference",title = "")+
  annotate("text",x = 2,y = -2,label = "4 weeks",hjust = 1,size = 10)+
  annotate("text",x = 0.95,y = -2,label = "8 weeks",hjust = 1,size = 10)



## c panel
p_intention <- ggplot(df_intention, aes(x_pos, prop, group = group)) +
  geom_col(aes(color = group),fill = df_intention$fill_color,width = 0.67,
           position = position_dodge(width = 0.71),linewidth = 1.8) +
  geom_errorbar(aes(ymin = lower, ymax = upper, color = group), width = 0.05,linewidth = 1, 
                position = position_dodge(width = 0.71)) +
  scale_x_continuous(breaks = c(1, 2, 2.8, 3.8, 4.6),) +
  scale_y_continuous(breaks = seq(0, 100, 20)) +
  coord_cartesian(ylim = c(0, 100),clip = "off")+
  scale_color_manual(values = c("SheeZan" = "#D88900", "Usual"   = "#3E4A5C")) +
  geom_segment(aes(y = 0, yend = 100, x = 0.42, xend = 0.42), color = "black", linewidth=0.5) +
  geom_segment(x = 2.0, xend = 3.8, y = -4, yend = -4, color = "black", linewidth = 0.5) +
  geom_segment(x = 4.3, xend = 6.1, y = -4, yend = -4, color = "black", linewidth = 0.5) +
  geom_segment(data = data.frame(y = seq(0, 100, 20)),aes(x = 0.42, xend = 0.28, y = y, yend = y),
               inherit.aes = FALSE,color = "black",linewidth = 0.5) +
  labs(x = "",y = "Proportion (%)",title = "") +
  theme_minimal() +
  theme(
    legend.title = element_blank(),
    legend.position = "none",
    panel.grid = element_blank(),
    axis.text.x = element_blank(),
    axis.text.y = element_blank(),
    axis.title.y = element_text(size = 36, color = "black", margin = margin(r = 25)),
    axis.title.x = element_blank(),
    plot.title = element_blank(),
    plot.margin = margin(t = 5, r = 5, b = 45, l = 5),
    panel.background = element_rect(fill = "transparent", colour = NA),
    plot.background = element_rect(fill = "transparent", colour = NA)
  ) +
  annotate("text",x = 0.15,y = seq(0,100,20),label = seq(0,100,20),hjust = 1,size = 11)+
  annotate("text",x = 2.9,y = 82,label = "4 weeks",size = 11,fontface = "plain")+
  annotate("text",x = 5.2,y = 82,label = "8 weeks",size = 11,fontface = "plain")


legend_legendc1 <- ggdraw() +
  draw_grob(gridtext::richtext_grob("<span style='color:#D88900;'>SheeZan</span>versus<span style='color:#3E4A5C;'>usual</span>",
                                    x = 0.4, y = 0.5,hjust = 0, vjust = 0,gp = gpar(fontsize = 25)))
legend_itemsc <- tribble(
  ~label,                  ~fill,       ~color,
  "Intention to act",      "#FFFFFF",   "#3E4A5C",
  "Action among intended", "#E8EAED",   "#3E4A5C",
  "Action among unintended","#D1D5DB",  "#3E4A5C"
)

legend_itemsc <- legend_itemsc %>%
  mutate(x_tile = 1,y_tile = c(1.6, 1.3, 1))

p_legendc2 <- ggplot(legend_itemsc, aes(x = x_tile, y = y_tile)) +
  geom_tile(aes(width = 0.15,height = 0.15,fill = fill,color = color),linewidth = 0.8) +
  geom_text(aes(x = x_tile + 0.13,y = y_tile,label = label),hjust = 0,vjust = 0.5,size = 8) +
  scale_fill_identity() +
  scale_color_identity() +
  theme_void() +
  xlim(0.5, 3) +
  ylim(0.5, 3.5)



## d panel
plot_bar_count_d <- function(df, x_lab, x_text = FALSE, legend = FALSE) {
  df$level <- factor(df$level,levels = rev(unique(df$level)))
  p <- ggplot(df, aes(x = level, y = prop, fill = group)) +
    geom_col(position = position_dodge(width = 0.8), width = 0.8) +
    scale_y_continuous(breaks = seq(0, 60, 20)) +
    coord_cartesian(ylim = c(0, 60),clip = "off")+
    scale_fill_manual(values = c("SheeZan" = "#e4db3c","Usual"   = "#c9d1ea")) +
    scale_x_discrete() +
    labs(x = "", y = "", fill = NULL) +
    geom_segment(aes(x =1, xend = 5, y = -3, yend = -3), color = "black",linewidth=0.5) +
    geom_segment(aes(x =1, xend = 1, y = -3, yend = -5), color = "black",linewidth=0.5) +
    geom_segment(aes(x =2, xend = 2, y = -3, yend = -5), color = "black",linewidth=0.5) +
    geom_segment(aes(x =3, xend = 3, y = -3, yend = -5), color = "black",linewidth=0.5) +
    geom_segment(aes(x =4, xend = 4, y = -3, yend = -5), color = "black",linewidth=0.5) +
    geom_segment(aes(x =5, xend = 5, y = -3, yend = -5), color = "black",linewidth=0.5) +
    geom_segment(aes(y = 0, yend = 60, x = 0.4, xend = 0.4), color = "black",linewidth=0.5)+
    geom_segment(data = data.frame(x = 0.4, xend = 0.3,y = seq(0, 60, 20),yend = seq(0, 60, 20)),
                 aes(x = x, xend = xend, y = y, yend = yend),color = "black", linewidth = 0.5, inherit.aes = FALSE)+
    theme_minimal() +
    theme(
      axis.text.x = if (x_text) element_text(size = 24, color = "black", vjust = -2) else element_blank(),
      axis.text.y = element_blank(),
      axis.title.x = element_text(size = 32, color = "black", margin = margin(t = 10)),
      axis.ticks = element_blank(),
      axis.line = element_blank(),
      legend.position = "none",
      panel.grid = element_blank(),
      plot.margin = if (x_text) margin(r = 80, t=90, l = 80, b = 90) else margin(r = 80, t=90, l = 80, b = 120),
      panel.background = element_rect(fill = "transparent", colour = NA),
      plot.background = element_rect(fill = "transparent", colour = NA)
    )+
    annotate("text",x = 0.2,y = seq(0,60,20),label = seq(0,60,20),hjust = 1,size = 10)+
    annotate("text",x = 3.4,y = 40,label = x_lab,hjust = 1,size = 10)

  if (legend) {
    p <- p +
      geom_segment(aes(y = 60, yend = 60, x = 1, xend = 5), color = "grey",linewidth=0.5)+
      geom_segment(aes(y = 63, yend = 60, x = 4.8, xend = 5), color = "grey",linewidth=0.5)+
      geom_segment(aes(y = 57, yend = 60, x = 4.8, xend = 5), color = "grey",linewidth=0.5)+
      annotate("text",x = 2.5,y = 67,label = "High social-evaluative threat",hjust = 0.35,size = 9)
  }

  return(p)
}

legend_itemsd <- tribble(
  ~label,                  ~fill,       ~color,
  "SheeZan",      "#f4b43f",   "#f4b43f",
  "Usual", "#8fa0b3",   "#8fa0b3"
)

legend_itemsd$x_tile <- c(1, 1.8)
legend_itemsd$y_tile <- 1

p_legendd <- ggplot(legend_itemsd, aes(x = x_tile, y = y_tile)) +
  geom_tile(aes(width = 0.1,height = 0.1,fill = fill,color = color),linewidth = 0.8) +
  geom_text(aes(x = x_tile + 0.13, y = y_tile,label = label),hjust = 0,vjust = 0.5,size = 8) +
  scale_fill_identity() +
  scale_color_identity() +
  theme_void() +
  xlim(0.5, 3.5) +
  ylim(0.5, 1.5)

p_d4 <- plot_bar_count_d(dfd4, "4 weeks", legend=TRUE)
p_d8 <- plot_bar_count_d(dfd8, "8 weeks", x_text=TRUE)
dy_lab <- ggdraw() + draw_label("Relative\nproportion (%)", y = 0.50,x=0.2, angle = 90, size = 32)
