library(ggplot2)

load("extended data fig1.RData")

plot_sub <- function(df, level_panle, y_title=FALSE){
  r_white <- 106
  if (y_title){r_white <- 60}
  p_aRR <- ggplot(df, aes(x = label, y = aRR, color = type)) +
    geom_point(position = position_dodge(width = 0.3), size = 8) +
    geom_errorbar(aes(ymin = CI_low, ymax = CI_high),position = position_dodge(width = 0.3),
                  width = 0.1,linewidth = 1.0) +
    geom_hline(yintercept = 1, linetype = "dashed", color = "black") +
    scale_color_manual(values = c("Help-seeking" = "#D55E00","Advice adherence" = "#0072B2"),
                       labels = c("Help-seeking        ", "Advice adherence")) +
    scale_y_continuous(limits = c(0, 5),breaks = seq(0, 5, 1)) +
    scale_x_discrete(expand = expansion(add = 0.3))+
    theme_classic(base_size = 13) +
    theme(
      legend.position = "none",
      axis.title.y = if (y_title) element_text(size = 38, margin = margin(r = 20)) else element_blank(),
      axis.title.x = element_blank(),
      axis.text.x = element_text(size = 35, margin = margin(t = 15)),
      axis.text.y = element_text(size = 35, margin = margin(r = 15)),
      axis.ticks.length.y = unit(0.3, "cm"),
      axis.ticks.length.x = unit(0.3, "cm"),
      panel.border = element_rect(color = "black", fill = NA),
      plot.margin = margin(t = 0, r = r_white, b = 5, l = 5),
      plot.title = element_text(size = 30, hjust = 0.5, face = "plain", margin = margin(b = 15)),
      text = element_text(face = "plain"),
      panel.background = element_rect(fill = "transparent", colour = NA),
      plot.background = element_rect(fill = "transparent", colour = NA),
    ) +
    labs(y = "Adjusted relative ratio",title = NULL)+
    annotate("text",x = 1.5,y = 5,label = unique(df$Title),size = 13,fontface = "plain")
}

p_an <- plot_sub(an, y_title=TRUE)
p_de <- plot_sub(de)
p_age <- plot_sub(age)
p_sex <- plot_sub(sex)
p_setting <- plot_sub(setting)
p_liv <- plot_sub(liv)
p_pho <- plot_sub(pho)
p_soc <- plot_sub(soc)
p_edu <- plot_sub(edu, y_title=TRUE)
print(p_edu)

legend_df <- data.frame(label = c("Help-seeking", "Advice adherence"),col = c("#D55E00","#0072B2"),x = c(0.6, 1.8),y = c(1.2, 1.2))
p_legend  <- ggplot(legend_df) +
  geom_segment(aes(x = x,xend = x + 0.15,y = y,yend = y,color = label),linewidth = 1.2) +
  geom_point(aes(x = x + 0.075,y = y,color = label),size = 4) +
  geom_text(aes(x = x + 0.25,y = y,label = label),hjust = 0,size = 9) +
  scale_color_manual(values = setNames(legend_df$col,legend_df$label)) +
  theme_void() +
  coord_cartesian(xlim = c(0.5, 3),ylim = c(0.4, 2.1),clip = "off") +
  theme(legend.position = "none",plot.margin = margin(5,5,5,5))

