library(ggplot2)

load("fig1c.RData")

## kappa panel
plot_kappa <- ggplot(df_kappa, aes(x = Dimension, y = kappa, group = type)) +
  geom_line(aes(color = type),linetype = "dashed",linewidth = 1.2) +
  geom_point(aes(shape = type, color = type),size = 11) +
  scale_shape_manual(values = c(15, 15),labels = c("SheeZan       ", "Instrument")) +
  scale_color_manual(values = c("#F8D28A", "#89c1e5"),labels = c("SheeZan       ", "Instrument")) +
  guides(color = guide_legend(override.aes = list(linetype = "dashed",shape = c(15, 15),size = 3))) +
  scale_y_continuous(breaks = seq(0.2, 1.0, 0.2))+
  coord_cartesian(ylim = c(0.2, 1.0),clip = "off") +
  labs(x = NULL,y = "Weighted kappa",color = "Kappa type",shape = "Kappa type")+
  annotate("segment", x = 0.7, xend = 0.7, y = 0.20, yend = 1.0, color = "black", linewidth = 0.6) +
  annotate("segment", x = 1, xend = 2, y = 0.20, yend = 0.20, color = "black", linewidth = 0.6) +
  geom_segment(data = data.frame(x = 0.7, xend = 0.65,y = seq(0.2, 1.0, 0.2),yend = seq(0.2, 1.0, 0.2)),
               aes(x = x, xend = xend, y = y, yend = yend),color = "black", linewidth = 0.7, inherit.aes = FALSE)+
  geom_segment(data = data.frame(y = 0.20, yend = 0.18,x = seq(1, 2, 1),xend = seq(1, 2, 1)),
               aes(x = x, xend = xend, y = y, yend = yend),color = "black", linewidth = 0.7, inherit.aes = FALSE)+
  annotate("text",x = 0.6,y = seq(0.2, 1.0, 0.2),label = sprintf("%.1f", seq(0.2, 1.0, 0.2)),hjust = 1,size = 10)+
  guides(color = guide_legend(override.aes = list(size = 6,linewidth = 0)))+
  theme_minimal()+
  theme(
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    panel.border = element_blank(),
    axis.ticks.x = element_blank(),
    axis.ticks.y = element_blank(),
    axis.line = element_blank(),
    axis.text.y = element_blank(),
    axis.text.x = element_text(size = 30, color = "black", margin = margin(t=0)),
    legend.position = "top",
    legend.title = element_blank(),
    legend.text = element_text(size = 26),
    legend.key.width  = unit(0, "cm"),
    axis.title.y = element_text(size = 30, color = "black",margin = margin(r=15)),
    legend.margin = margin(t = 0, b = 20, r = 20),
    panel.background = element_rect(fill = "transparent", colour = NA),
    plot.background = element_rect(fill = "transparent", colour = NA),
    plot.margin = margin(t = 230, r = 200, b = 75, l = 100)
  )

## reason panel
df_reason$Reason <- factor(
  df_reason$Reason,
  levels = rev(c(
    "dynamic affective state",
    "trust and safety to open up",
    "detailed personal experience",
    "comprehensive symptom expression",
    "cultural framing of health state"
  ))
)
plot_reason <- ggplot(df_reason, aes(x = Reason, y = Proportion)) +
  geom_col(width = 0.82, fill = "#f7f4d9") +
  scale_y_continuous(breaks = seq(0, 100, 25),labels = function(x) paste0(x, "")) +
  coord_flip(ylim = c(0, 100),clip = "off")+
  labs(x = NULL,y = NULL)  +
  geom_segment(y = 0, yend = 100, x = 5.7, xend = 5.7, color = "black",linewidth=0.3)+
  geom_segment(data = data.frame(x = 5.7, xend = 5.85,y = seq(0, 100, 20),yend = seq(0, 100, 20)),
               aes(x = x, xend = xend, y = y, yend = yend),color = "black", linewidth = 0.5, inherit.aes = FALSE)+
  geom_segment(x = 0.5, xend = 5.5, y = -3, yend = -3, color = "black", linewidth = 0.3) +
  geom_segment(x = 0.5, xend = 0.5, y = -3, yend = -1.5, color = "black", linewidth = 0.3) +
  geom_segment(x = 5.5, xend = 5.5, y = -3, yend = -1.5, color = "black", linewidth = 0.3) +
  theme_minimal() +
  theme(
    axis.text.x = element_blank(),
    axis.text.y = element_blank(),
    legend.position = "none",
    panel.grid = element_blank(),
    axis.ticks.y = element_blank(),
    axis.title.y = element_blank(),
    axis.title.x = element_blank(),
    axis.ticks.x = element_blank(),
    plot.margin = margin(r = 50, t=80, l = 80, b = 80),
    panel.background = element_rect(fill = "transparent", colour = NA),
    plot.background = element_rect(fill = "transparent", colour = NA),
  )+
  geom_text(aes(x = Reason,y = 2,label = Reason),hjust = 0,size = 10)+
  annotate("text",x = 6.2,y = seq(0,100,20),label = seq(0,100,20),size = 10)+
  annotate("text",x = 6.9,y = 50,label = "Proportion (%)",size = 11)
