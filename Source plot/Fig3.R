library(cowplot)
library(Cairo)
library(grid)
library(ggplot2)
library(dplyr)

load("fig3.RData")

## a panel
plot_bar_count_a <- function(df, x_lab) {
  df$level <- gsub("\\\\n", "\n", df$level)
  df$level <- factor(df$level,levels = unique(df$level))
  p <- ggplot(df, aes(x = level, y = n, fill = group)) +
    geom_col(position = position_dodge(width = 0.9), width = 0.9) +
    scale_y_continuous(breaks = seq(0, 150, 50)) +
    coord_cartesian(ylim = c(0, 150),clip = "off")+
    scale_fill_manual(values = c("SheeZan" = "#f6b23a","Usual"   = "#bfc4cc")) +
    scale_x_discrete() +
    labs(x = "", y = "Number of\nparticipants", fill = NULL) +
    geom_segment(aes(x =1, xend = 5, y = -3, yend = -3), color = "black",linewidth=0.5) +
    geom_segment(aes(x =1, xend = 1, y = -3, yend = -10), color = "black",linewidth=0.5) +
    geom_segment(aes(x =2, xend = 2, y = -3, yend = -10), color = "black",linewidth=0.5) +
    geom_segment(aes(x =3, xend = 3, y = -3, yend = -10), color = "black",linewidth=0.5) +
    geom_segment(aes(x =4, xend = 4, y = -3, yend = -10), color = "black",linewidth=0.5) +
    geom_segment(aes(x =5, xend = 5, y = -3, yend = -10), color = "black",linewidth=0.5) +
    geom_segment(aes(y = 0, yend = 150, x = 0.4, xend = 0.4), color = "black",linewidth=0.5)+
    geom_segment(data = data.frame(x = 0.4, xend = 0.3,y = seq(0, 150, 50),yend = seq(0, 150, 50)),
                 aes(x = x, xend = xend, y = y, yend = yend),color = "black", linewidth = 0.5, inherit.aes = FALSE)+
    theme_minimal() +
    theme(
      axis.text.x = element_text(size = 22, color = "black", vjust = 0.5),
      axis.text.y = element_blank(),
      axis.title.x = element_blank(),
      axis.title.y = element_text(size = 29, color = "black", margin = margin(r = 60)),
      axis.ticks = element_blank(),
      axis.line = element_blank(),
      legend.position = "none",
      panel.grid = element_blank(),
      plot.margin = margin(r = -15, t=130, l = 0, b = 150),
      panel.background = element_rect(fill = "transparent", colour = NA),
      plot.background = element_rect(fill = "transparent", colour = NA)
    )+
    annotate("text",x = 0.2,y = seq(0,150,50),label = seq(0,150,50),hjust = 1,size = 10)+
    annotate("text",x = 0.5,y = 135,label = x_lab,size = 9.5,hjust=0, fontface = "plain")

  return(p)
}

legend_labela <- ggdraw() +
  draw_grob(
    gridtext::richtext_grob(
      "<span style='color:#f4b43f;'>SheeZan</span>versus<span style='color:#8fa0b3;'>usual</span>",
      x = 0.4, y = 0.5,hjust = 0, vjust = 0,gp = gpar(fontsize = 22)))

p_at <- plot_bar_count_a(at, "Stigma attitudes")
p_sa <- plot_bar_count_a(sa, "Satisifaction")
p_ac <- plot_bar_count_a(ac, "Acceptance")
p_hp <- plot_bar_count_a(hp, "Awareness of Helpful behavior")



## b panel
dfb$Dimension <- factor(
  dfb$Dimension,
  levels = rev(c(
    "Speaking safely without fear of judgement",
    "Clear and concrete analysis of their situation",
    "Feeling understood",
    "A consistently available patient companion",
    "Collaboratively inding a direction without direct answers",
    "Deep conversation clarifying vague thoughts and feelings"
  )))

bp <- ggplot(dfb, aes(x = Dimension, y = Proportion)) +
  geom_col(width = 0.7, fill = "#ddead5") +
  scale_y_continuous(breaks = seq(0, 60, 10),labels = function(x) paste0(x, "")) +
  coord_flip(ylim = c(0, 60),clip = "off")+
  labs(x = NULL,y = "Proportion (%)") +
  geom_segment(y = 0, yend = 60, x = 0.3, xend = 0.3, color = "black",linewidth=0.3)+
  geom_segment(data = data.frame(x = 0.3, xend = 0.2,y = seq(0, 60, 10),yend = seq(0, 60, 10)),
               aes(x = x, xend = xend, y = y, yend = yend),color = "black", linewidth = 0.5, inherit.aes = FALSE)+
  geom_segment(x = 0.5, xend = 6.5, y = -3, yend = -3, color = "black", linewidth = 0.3) +
  geom_segment(x = 0.5, xend = 0.5, y = -3, yend = -1.5, color = "black", linewidth = 0.3) +
  geom_segment(x = 6.5, xend = 6.5, y = -3, yend = -1.5, color = "black", linewidth = 0.3) +
  theme_minimal() +
  theme(
    axis.text.x = element_text(size = 20, color = "black", margin = margin(t = 15),),
    axis.text.y = element_blank(),
    legend.position = "none",
    panel.grid = element_blank(),
    axis.ticks.y = element_blank(),
    axis.title.y = element_blank(),
    axis.title.x = element_text(size = 21, color = "black",margin = margin(t=20)),
    axis.ticks.x = element_blank(),
    plot.margin = margin(r = 5, t=35, l = 5, b = 5),
    panel.background = element_rect(fill = "transparent", colour = NA),
    plot.background = element_rect(fill = "transparent", colour = NA)
  )+
  geom_text(aes(x = Dimension,y = 2,label = Dimension),hjust = 0,size = 6.25)



## c panel
draw_coping_skill_radar <- function(plot_data) {
  axis_data <- unique(plot_data[c("skill_type", "criterion", "axis_label")])
  n_axes <- nrow(axis_data)
  group_levels <- unique(plot_data$group)
  plot_data <- plot_data %>%
    arrange(factor(group, levels = group_levels),skill_type,criterion)
  score_matrix <- matrix(plot_data$mean,nrow = length(group_levels),ncol = n_axes,byrow = TRUE)
  sd_matrix <- matrix(plot_data$sd,nrow = length(group_levels),ncol = n_axes,byrow = TRUE)
  rownames(score_matrix) <- group_levels
  rownames(sd_matrix) <- group_levels
  angles <- seq(pi / 2,pi / 2 - 2 * pi,length.out = n_axes + 1)[-(n_axes + 1)]
  scale_max <- 5
  radar_radius <- 1.15
  angle_dodge_deg <- 2.5
  angle_dodge <- angle_dodge_deg * pi / 180
  group_angle_offset <- c("SheeZan" = -angle_dodge,"Usual"   =  angle_dodge)
  tick_values <- 1:5
  grid_radius <- tick_values / scale_max * radar_radius
  group_colors <- c("SheeZan" = "#D98532","Usual" = "#5B94AD")
  skill_colors <- c("Episodic future thinking" = "#3594CC","Cognitive reconstructing" = "#EA801C")
  skill_fill_colors <- c(
    "Episodic future thinking" = adjustcolor("#3594CC", alpha.f = 0.08),
    "Cognitive reconstructing" = adjustcolor("#EA801C", alpha.f = 0.08)
  )
  skill_fill_colors_legend <- c(
    "Episodic future thinking" = adjustcolor("#3594CC", alpha.f = 0.38),
    "Cognitive reconstructing" = adjustcolor("#EA801C", alpha.f = 0.38)
  )
  par(mar = c(1.2, 1.2, 1.2, 1.2),xpd = NA,font = 1,font.axis = 1,font.lab = 1,font.main = 1)
  plot(0, 0,type = "n",asp = 1,axes = FALSE,xlab = "",ylab = "",xlim = c(-1.78, 1.78),ylim = c(-1.68, 1.62))

  episodic_start <- -pi / 3
  episodic_end   <-  2 * pi / 3
  episodic_arc <- seq(episodic_start, episodic_end, length.out = 500)
  polygon(x = c(0, radar_radius * cos(episodic_arc), 0),y = c(0, radar_radius * sin(episodic_arc), 0),
          col = unname(skill_fill_colors["Episodic future thinking"]),border = NA)
  cognitive_start <- 2 * pi / 3
  cognitive_end   <- 5 * pi / 3
  cognitive_arc <- seq(cognitive_start, cognitive_end, length.out = 500)
  polygon(x = c(0, radar_radius * cos(cognitive_arc), 0),y = c(0, radar_radius * sin(cognitive_arc), 0),
          col = unname(skill_fill_colors["Cognitive reconstructing"]),border = NA)

  theta <- seq(0, 2 * pi, length.out = 360)
  for (r in grid_radius) {
    lines(r * cos(theta),r * sin(theta),col = "#D7D7D7",lwd = 1.2)
  }
  lines(radar_radius * cos(theta),radar_radius * sin(theta),col = "#555555",lwd = 1.6)
  for (i in seq_len(n_axes)) {
    lines(c(0, radar_radius * cos(angles[i])),c(0, radar_radius * sin(angles[i])),col = "#C7C7C7",lwd = 1)
  }

  tick_angle <- angles[1] - pi / 13
  for (i in seq_along(tick_values)) {
    r <- grid_radius[i]
    text(r * cos(tick_angle),r * sin(tick_angle),labels = tick_values[i],cex = 1.68,col = "#222222",font = 1)
  }

  criterion_r <- radar_radius * 1.09
  criterion_labels <- c(
    "Reasonableness",
    "Specificity",
    "Helpfulness",
    "Reasonableness",
    "Specificity",
    "Helpfulness"
  )
  criterion_srt <- c(0, -60, 60, 0, -60, 60)
  for (i in seq_len(n_axes)) {
    text(criterion_r * cos(angles[i]), criterion_r * sin(angles[i]),labels = criterion_labels[i],
         cex = 1.68, font = 1,srt = criterion_srt[i])
  }

  for (group in group_levels) {
    j <- match(group, group_levels)
    radii <- score_matrix[j, ] / scale_max * radar_radius
    group_angles <- angles + unname(group_angle_offset[group])
    x <- radii * cos(group_angles)
    y <- radii * sin(group_angles)
    lines(c(x, x[1]),c(y, y[1]),col = group_colors[group],lwd = 4)

    for (i in seq_len(n_axes)) {
      low <- max(0, score_matrix[j, i] - sd_matrix[j, i]) /
        scale_max * radar_radius
      high <- min(scale_max, score_matrix[j, i] + sd_matrix[j, i]) /
        scale_max * radar_radius
      ux <- cos(group_angles[i])
      uy <- sin(group_angles[i])
      lines(c(low * ux, high * ux),c(low * uy, high * uy),col = group_colors[group],lwd = 3)
    }

    points(x,y,pch = 21,bg = "white",col = group_colors[group], cex = 2.2)
  }

  legend_x <- 1.5
  legend_y <- 1.25
  for (i in seq_along(group_levels)) {
    group <- group_levels[i]
    y0 <- legend_y - (i - 1) * 0.15
    segments(legend_x,y0,legend_x + 0.13,y0,col = group_colors[group],lwd = 3)
    points(legend_x + 0.065,y0,pch = 21,bg = "white",col = group_colors[group],cex = 1.35)
    text(legend_x + 0.17,y0,labels = group,adj = 0,cex = 1.4,font = 1)
  }
}

CairoPDF("fig3c_radar.pdf", width = 10,height = 9,family ="Aptos",bg = "transparent")
draw_coping_skill_radar(radar_data)
dev.off()

p_forest <- ggplot(df_forest, aes(y = Intervention, x = Mean, color = Intervention)) +
  geom_errorbar(aes(xmin = lower,xmax = upper),width = 0.15,linewidth = 1.5) +
  geom_point(size = 8,aes(color = Intervention)) +
  geom_vline(xintercept = 0,linetype = "dashed",color = "black") +
  scale_color_manual(
    values = c(
      "Episodic future\nthinking" = "#aed4eb",
      "Cognitive\nrestructuring" = "#f7cca4"
    )) +
  scale_x_continuous(limits = c(-8, 6),breaks = seq(-8, 6, 2)) +
  labs(x = "Pre-to-post training distress change",y = "") +
  theme_classic(base_size = 14) +
  theme(
    legend.position = "none",
    axis.text.x = element_text(size = 26, margin = margin(t = 10)),
    axis.text.y = element_blank(),
    axis.title.x = element_text(size = 26, margin = margin(t = 25)),
    axis.ticks.length.x = unit(0.3, "cm"),
    axis.ticks.length.y = unit(0, "cm"),
    panel.border = element_rect(color = "black",fill = NA,linewidth = 1),
    panel.background = element_rect(fill = "transparent", colour = NA),
    plot.background = element_rect(fill = "transparent", colour = NA),
    plot.margin = margin(r = 80, t=160, l = 160, b = 100)
  )


legend_itemsc <- tribble(
  ~label,                  ~fill,       ~color,
  "Episodic future thinking",      "#c2dff0",   "#c2dff0",
  "Cognitive restructuring", "#f9d9bb",   "#f9d9bb"
)

legend_itemsc$x_tile <- c(1, 1)
legend_itemsc$y_tile <- c(1.2, 1.0)

p_legendc <- ggplot(legend_itemsc, aes(x = x_tile, y = y_tile)) +
  geom_tile(aes(width = 0.1,height = 0.1,fill = fill,color = color),linewidth = 0.8) +
  geom_text(aes(x = x_tile + 0.13,y = y_tile,label = label),hjust = 0,vjust = 0.5,size = 8.5) +
  scale_fill_identity() +
  scale_color_identity() +
  theme_void() +
  xlim(0.5, 3.5) +
  ylim(0.5, 1.5)

