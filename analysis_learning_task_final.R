# Analysis pipeline for Learning Task in Novel Word Learning study
# includes 1. data preparation; 2. modeling of eye-tracking measures; 3. plotting
# Olga Solaja
# 28-6-2022
# SISSA - International school for Advanced studies, Trieste


# fixations shorter than 80ms are discarded in the file used here (output_lt.csv)

#### 1-data preparation ####
#clean environment
rm(list = ls())

#import libraries
library(ggplot2) # plots
library(data.table) # fread in input
library(tidyverse) # data wrangling
library(lmerTest) # (g)lmer
library(emmeans) # post hoc pairwise comparisons
# library(MASS) # boxcox ## MASS package clases with "select()" function in dplyr/tidyverse; SOLUTION: specify MASS:: where needed
library(cowplot) # create and organize a multiple panel plot
library(wesanderson) # color palette for plots
library(ggbeeswarm) # add nicely shaped scatter to violin plot
library(ggsignif) # add significance brackets to violin plot
library(interactions) # plot interactions
library(jtools) # clean model summaries
library(effects) # interpret models
library(car) # Anova
library(cowplot) # combined plot

# disable scientific notation
options(scipen = 999)

# set wd
setwd("C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\\Olga_experiment\\Analyses_main\\learning_task")


# Prepare data ------------------------------------------------------------

# import data and keep only the necessary columns
eye_tracking_data <- fread("output_LT_main_final_9-10-2023.csv", header=T, sep = ",", stringsAsFactors = FALSE)

# rename column
eye_tracking_data <-rename(eye_tracking_data, order_out = V1)


# load mif dataset
mif_data <- fread("mif_11-10-2023.csv", header=T, sep = ",", stringsAsFactors = FALSE)

# merge datasets
mydata <- merge(mif_data, eye_tracking_data, by = "sbj_id")

# delete participants 1 and 86
mydata <- mydata %>% filter(!sbj_id %in% c(1, 86))

# relevel "complexity" variable
mydata$complexity = factor(mydata$complexity, levels = c("lf", "hf", "sf"))

# substitute 0 with NA
mydata <- mydata %>%  mutate_at(c("tot_dur_target","gaze_dur_target"), ~na_if(., 0))

# fix punctuation in "cribotista"
mydata$target<-gsub('[[:punct:] ]+',' ', mydata$target)

# delete unnecessary column
mydata <- mydata %>% dplyr::select(-V1)

# rename column
mydata <- mydata %>% rename("mif" = "final_MIE")

# set MIF as factor
mydata <- mydata %>% mutate(as.factor(mif))

# remove dfs I don't need
rm(eye_tracking_data, mif_data)

#### 2-descriptive stats ####

# mean number of fixations overall
round(mean(mydata$n_of_fix, na.rm=T),digits=2)

# proportion of single fixations
round(sum(!is.na(mydata$single_fix)) / length(mydata$single_fix),digits=2)

# mean overall gaze duration
round(mean(mydata$gaze_dur_target, na.rm=T),digits=2)


#### 3-modelling ####

# set treatment contrasts
mydata$complexity <- as.factor(mydata$complexity)
contrasts(mydata$complexity) <- contr.treatment(levels(mydata$complexity))

# GAZE DURATIONS

# decide on transformation
dev.off()
MASS::boxcox(mydata$gaze_dur_target ~ 1)

par(mfrow=c(1,4))
hist(mydata$gaze_dur_target, 20)
hist(mydata$gaze_dur_target[all_data$gaze_dur_target])
hist(log(mydata$gaze_dur_target))
hist(1/mydata$gaze_dur_target)
par(mfrow=c(1,1))

# relevel "complexity" variable
mydata$complexity = factor(mydata$complexity, levels = c("lf", "hf", "sf"))

# model gaze duration
m_gaze_target <- lmer(log(gaze_dur_target) ~ complexity*target_order + (1|sbj_id) + (1|target), data = mydata)
summary(m_gaze_target)

predictors_gaze <- expand.grid(complexity = c("level1", "level2"),
                          target_order = c("levelA", "levelB"))


effect_plot_gaze <- allEffects(m_gaze_target, predictors = predictors_gaze)
plot(effect_plot_gaze)


# confidence intervals
round(confint.merMod(m_gaze_target, method="Wald", level = 0.95),digits=2)

# TOTAL DURATIONS

# decide on transformation
dev.off()
MASS::boxcox(mydata$tot_dur_target ~ 1)

par(mfrow=c(1,4))
hist(mydata$tot_dur_target, 20)
hist(mydata$tot_dur_target[mydata$tot_dur_target])
hist(log(mydata$tot_dur_target))
hist(1/mydata$tot_dur_target)

# model total durations
m_tot_target <- lmer(log(tot_dur_target) ~ complexity*target_order + (1|sbj_id) + (1|target), data = mydata )
summary(m_tot_target)

predictors_tot <- expand.grid(complexity = c("level1", "level2"),
                               target_order = c("levelA", "levelB"))


effect_plot_tot <- allEffects(m_tot_target, predictors = predictors_tot)
plot(effect_plot_tot)


# confidence intervals
round(confint.merMod(m_tot_target, method="Wald",level = 0.95), digits=2)

# post hoc pairwise comparisons
# emmeans(m_tot_target, pairwise ~ factor(target_order) * complexity)

# to see where the interaction sf*target order comes from --> it;s significant from the beginning but more pronounced at the end
m_tot_target_m_means = emmeans(m_tot_target, pairwise ~ complexity|target_order, type="tot_dur_target", cov.reduce = range)
summary(m_tot_target_m_means)



# Exploratory analyses ----------------------------------------------------

# model gaze duration
# reorder complexity variable
mydata$complexity = factor(mydata$complexity, levels = c("lf", "hf", "sf"))

exp_m_gaze_target <- lmerTest::lmer(log(gaze_dur_target) ~ complexity*target_order*mif + (1|sbj_id) + (1|target), data = mydata)
summary(exp_m_gaze_target)


# exp_m_gaze_target2 <- lmerTest::lmer(log(gaze_dur_target) ~ complexity + target_order + mif + (1|sbj_id) + (1|target), data = mydata)
# summary(exp_m_gaze_target2)

# anova(exp_m_gaze_target, exp_m_gaze_target2)


# confidence intervals
round(confint.merMod(exp_m_gaze_target, method="Wald", level = 0.95),digits=2)

# post hoc pairwise comparisons
# emm_options(pbkrtest.limit = 15026)  # Set the limit

# emmeans(exp_m_gaze_target, pairwise ~ scale(mif) | complexity)
# 
# emmeans(exp_m_gaze_target, pairwise ~ mif | target_order)
# 
# emmeans(exp_m_gaze_target, pairwise ~ complexity | mif | target_order)

# model total durations
exp_m_tot_target <- lmer(log(tot_dur_target) ~ complexity*target_order*mif + (1|sbj_id) + (1|target), data = mydata )
summary(exp_m_tot_target)

# confidence intervals
round(confint.merMod(exp_m_tot_target, method="Wald",level = 0.95), digits=2)

# post hoc pairwise comparisons
# emm_options(pbkrtest.limit = 15026)  # Set the limit

emmeans(exp_m_tot_target, pairwise ~ mif | target_order)




#### 4-plots ####

# take away the NA and relevel complexity
mydata <- mydata[!is.na(mydata$complexity),];
mydata$complexity = factor(mydata$complexity, levels = c("sf", "hf", "lf"))

gaze_data <- mydata %>% group_by(target_order,complexity) %>%
  summarise(n = n(), mean_rt = mean(na.omit(gaze_dur_target)), sd_rt = sd(na.omit(gaze_dur_target)),
            ci_upper = qt(0.975, df = n - 1) * sd_rt / sqrt(n), ci_lower = qt(0.025, df = n - 1) * sd_rt / sqrt(n),
            sem = sd_rt/sqrt(n-1))

gaze_data_x_sbj <- mydata %>% group_by(target_order,complexity,sbj_id) %>%
  summarise(n = n(), mean_rt = mean(na.omit(gaze_dur_target)), sd_rt = sd(na.omit(gaze_dur_target)),
            ci_upper = qt(0.975, df = n - 1) * sd_rt / sqrt(n), ci_lower = qt(0.025, df = n - 1) * sd_rt / sqrt(n),
            sem = sd_rt/sqrt(n-1))


p_gaze <- ggplot(gaze_data) +
  geom_point(aes(x = target_order, y = mean_rt, color = factor(complexity)),size = 4, alpha = 0.4) +
  geom_line(aes(x = target_order, y = mean_rt, group = complexity, color = complexity), size = 1) +
  geom_ribbon(aes(x=target_order,ymin = mean_rt - sem, ymax = mean_rt + sem, fill = factor(complexity)), alpha = 0.2) +
  theme_classic() +
  theme(legend.position = "right", 
        legend.text = element_text(size = 15), 
        legend.title = element_text(size = 15), 
        strip.text.x = element_text(size = 18, color = "black"), 
        strip.background = element_rect("white"), 
        axis.text = element_text(size = 18, color = "black"),  # Increased axis text size
        axis.title = element_text(size = 22),  # Increased axis title size
        axis.title.x = element_blank(), 
        plot.title = element_text(size = 24, face = "bold"), 
        panel.grid.major.x = element_blank(), 
        panel.grid.minor.x = element_blank(),
        panel.border = element_rect(color = "black", fill = NA, size = 1),  # Added panel border
        plot.margin = margin(1, 1, 1, 1, "cm")) +  # Adjusted plot margins
  guides(alpha = "none") + 
  # scale_color_manual(values = c("#bc5090","#003f5c","#fec107"), guide = "none", labels = c("Suffix", "High frequency ending", "Low frequency ending")) +
  # scale_fill_manual(values = c("#bc5090", "#003f5c","#fec107"), "Type of ending", labels = c("Suffix", "High frequency ending", "Low frequency ending")) +
  labs(y="Gaze durations (in ms)", x="Trial number") +
  # scale_y_continuous(limits = c(400,1200), breaks = seq(400,1200,200)) +
  scale_x_continuous(limits = c(1,10), breaks = seq(1,10,1))

p_gaze
# save the plot to the current directory
# ggsave(filename = "gaze_dur_final.png", width = 250, height = 100, units = "mm")

# EXPLORATORY ANALYSIS plots

# GAZE DATA

summ(exp_m_gaze_target)

# target_order:mif 
interact_plot(exp_m_gaze_target, pred = target_order, modx = mif,
              plot.points = F, # overlay data
                            # different shape for differennt levels of the moderator
              point.shape = T, 
              jitter = 0.1, 
              x.label = "Trial order", 
              y.label = "log(gaze durations)",
              main.title = "Gaze durations as a function of MIF and target order interaction",
              legend.main = "Morpheme interference index",
              colors = "blue",
              # include confidence band
              interval = TRUE, 
              int.width = 0.9, 
              robust = T) +
  theme_light() +
  theme(legend.position = "right",  legend.text = element_text(size=12),legend.title = element_text(size=12), axis.text=element_text(size=14), axis.title=element_text(size=14),
        plot.title=element_text(size=24,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
  scale_x_continuous(limits = c(1,10), breaks = seq(1,10,1))

# ggsave(filename = "gaze_mif_t_order.png", width = 250, height = 100, units = "mm")


# complexitysf:mif
interact_plot(exp_m_gaze_target, pred = mif, modx = complexity,
              plot.points = F, # overlay data
              # different shape for differennt levels of the moderator
              point.shape = T, 
              jitter = 0.1, 
              x.label = "Morpheme interference index", 
              y.label = "log(gaze durations)",
              main.title = "Gaze durations as a function of MIF and complexity interaction",
              legend.main = "Complexity",
              colors = wes_palette("FantasticFox1", n =3),
              # include confidence band
              interval = TRUE, 
              int.width = 0.9, 
              robust = T) +
  theme_light() +
  theme(legend.position = "right",  legend.text = element_text(size=12),legend.title = element_text(size=12), axis.text=element_text(size=14), axis.title=element_text(size=14),
        plot.title=element_text(size=24,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank())

# ggsave(filename = "gaze_mif_complexity.png", width = 250, height = 100, units = "mm")


# complexity:target_order:mif 
# reorder complexity variable
mydata$complexity = factor(mydata$complexity, levels = c("sf", "hf", "lf"))

interact_plot(exp_m_gaze_target, pred = target_order, modx = mif, mod2 = complexity,
              plot.points = F, # overlay data
              # different shape for differennt levels of the moderator
              point.shape = T, 
              jitter = 0.1, 
              x.label = "Trial order", 
              y.label = "log(gaze durations)",
              # main.title = "Gaze durations as a function of MIF x target order x complexity interaction",
              legend.main = "Morpheme interference index",
              # colors = c("#bc5090","#003f5c","#fec107"),
              colors = wes_palette(n = 3, name = "FantasticFox1"),
              # include confidence band
              interval = TRUE, 
              int.width = 0.95, 
              robust = T,
              # modx.values = c(mean(mydata$mif), mean(mydata$mif) + sd(mydata$mif)*2, mean(mydata$mif) - sd(mydata$mif)*2),
              modx.values = c("-2 SD" = mean(mydata$mif) - sd(mydata$mif)*2, 
                              "Mean" = mean(mydata$mif), 
                              "2 SD" = mean(mydata$mif) + sd(mydata$mif)*2),
              mod2.labels = c("Suffixed", "High frequency", "Low frequency")) +
  theme_light() +
  theme(legend.position = "right",  legend.text = element_text(size=12),legend.title = element_text(size=12), axis.text=element_text(size=14), axis.title=element_text(size=14),
        plot.title=element_text(size=24,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank(), strip.text = element_text(size = 16, color = "black"),
        strip.background = element_rect(fill = "white") +
  scale_x_continuous(limits = c(1,10), breaks = seq(1,10,1)))

# ggsave(filename = "gaze_mif_t_order_complexity_stage_2.png", width = 250, height = 100, units = "mm")


# TOTAL DURATIONS

summ(exp_m_tot_target)

# target_order:mif 
interact_plot(exp_m_tot_target, pred = target_order, modx = mif,
              plot.points = F, # overlay data
              # different shape for differennt levels of the moderator
              point.shape = T, 
              jitter = 0.1, 
              x.label = "Trial order", 
              y.label = "log(total durations)",
              main.title = "Total durations as a function of MIF and target order interaction",
              legend.main = "Morpheme interference index",
              colors = "blue",
              # include confidence band
              interval = TRUE, 
              int.width = 0.9, 
              robust = T) +
  theme_light() +
  theme(legend.position = "right",  legend.text = element_text(size=12),legend.title = element_text(size=12), axis.text=element_text(size=14), axis.title=element_text(size=14),
        plot.title=element_text(size=24,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
  scale_x_continuous(limits = c(1,10), breaks = seq(1,10,1))

# ggsave(filename = "tot_dur_mif_t_order.png", width = 250, height = 100, units = "mm")


# complexitysf:mif
interact_plot(exp_m_tot_target, pred = mif, modx = complexity,
              plot.points = F, # overlay data
              # different shape for differennt levels of the moderator
              point.shape = T, 
              jitter = 0.1, 
              x.label = "Morpheme interference index", 
              y.label = "log(total durations)",
              main.title = "Total durations as a function of MIF and complexity interaction",
              legend.main = "Complexity",
              colors = wes_palette("FantasticFox1", n =3),
              # include confidence band
              interval = TRUE, 
              int.width = 0.9, 
              robust = T) +
  theme_light() +
  theme(legend.position = "right",  legend.text = element_text(size=12),legend.title = element_text(size=12), axis.text=element_text(size=14), axis.title=element_text(size=14),
        plot.title=element_text(size=24,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank())

# ggsave(filename = "tot_dur_mif_complexity.png", width = 250, height = 100, units = "mm")




# # ADDED PLOT COMPLEXITY
# 
# gaze_data_x_sbj$complexity = factor(gaze_data_x_sbj$complexity, levels = c("sf", "hf", "lf"))
# 
# 
# ggplot(gaze_data_x_sbj, aes(x = factor(complexity), y = mean_rt, color = factor(complexity))) +
#   geom_violin(size = 1.5, trim = T) +
#   geom_boxplot(alpha = 0.3, width=0.1, size = 0.8, color="black", outlier.shape = NA) +
#   geom_quasirandom(aes(fill = factor(sbj_id)), shape = 20, size=3, dodge.width = 0.5, alpha = 0.2, show.legend = F, width = 0.4) +
#   # geom_boxplot(aes(color = factor(complexity)), outlier.shape = NA) +
#   theme_classic()+
#   theme(legend.position = "none", axis.text=element_text(size=25, color = "black"), axis.text.x=element_text(size = 25), axis.title=element_text(size=25), axis.title.x = element_blank(),
#         plot.title=element_text(size=20,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
#   scale_color_manual(values = wes_palette("FantasticFox1", n =3)) +
#   # scale_fill_manual(values = c("#bc5090", "#003f5c","#fec107")) +
#   labs(y = "Mean gaze duration") +
#   scale_x_discrete(labels = c("Suffixed\n", "High frequency\nendings", "Low frequency\nendings"), position = "bottom") +
#   scale_y_continuous(limits = c(200, 2000), breaks = seq(200,2000,500))


tot_data <- mydata %>% group_by(target_order,complexity) %>%
  summarise(n = n(), mean_rt = mean(na.omit(tot_dur_target)), sd_rt = sd(na.omit(tot_dur_target)),
            ci_upper = qt(0.975, df = n - 1) * sd_rt / sqrt(n), ci_lower = qt(0.025, df = n - 1) * sd_rt / sqrt(n),
            sem = sd_rt/sqrt(n-1))

tot_data_x_sbj <- mydata %>% group_by(target_order,complexity,sbj_id) %>%
  summarise(n = n(), mean_rt = mean(na.omit(tot_dur_target)), sd_rt = sd(na.omit(tot_dur_target)),
            ci_upper = qt(0.975, df = n - 1) * sd_rt / sqrt(n), ci_lower = qt(0.025, df = n - 1) * sd_rt / sqrt(n),
            sem = sd_rt/sqrt(n-1))

p_tot <- ggplot(tot_data) +
  geom_point(aes(x = target_order, y = mean_rt, color = factor(complexity)),size = 4, alpha = 0.4) +
  geom_line(aes(x = target_order, y = mean_rt, group = complexity, color = complexity), size = 1) +
  geom_ribbon(aes(x=target_order,ymin = mean_rt - sem, ymax = mean_rt + sem, fill = factor(complexity)), alpha = 0.2) +
  theme_classic() +
  theme(legend.position = "right", 
        legend.text = element_text(size = 15), 
        legend.title = element_text(size = 15), 
        strip.text.x = element_text(size = 18, color = "black"), 
        strip.background = element_rect("white"), 
        axis.text = element_text(size = 18, color = "black"),  # Increased axis text size
        axis.title = element_text(size = 22),  # Increased axis title size
        axis.title.x = element_blank(), 
        plot.title = element_text(size = 24, face = "bold"), 
        panel.grid.major.x = element_blank(), 
        panel.grid.minor.x = element_blank(),
        panel.border = element_rect(color = "black", fill = NA, size = 1),  # Added panel border
        plot.margin = margin(1, 1, 1, 1, "cm")) +  # Adjusted plot margins
  guides(alpha = "none") + 
  scale_color_manual(values = c("#bc5090","#003f5c","#fec107"), guide = "none", labels = c("Suffix", "High frequency ending", "Low frequency ending")) +
  scale_fill_manual(values = c("#bc5090", "#003f5c","#fec107"), "Type of ending", labels = c("Suffix", "High frequency ending", "Low frequency ending")) +
  labs(y="Total durations (in ms)", x="Trial number") +
  # scale_y_continuous(limits = c(600,2000), breaks = seq(600,2000,200)) +
  scale_x_continuous(limits = c(1,10), breaks = seq(1,10,1))

p_tot
# save the plot to the current directory
# ggsave(filename = "tot_dur_final.png", width = 250, height = 100, units = "mm")

# # ADDED PLOT TOTAL DURATIONS
# 
# tot_data_x_sbj$complexity <- factor(tot_data$complexity, levels = c("sf", "hf", "lf"))
# 
# ggplot(tot_data_x_sbj, aes(x = factor(complexity), y = mean_rt, color = factor(complexity))) +
#   geom_violin(size = 1.5, trim = T) +
#   geom_boxplot(alpha = 0.3, width=0.1, size = 0.8, color="black", outlier.shape = NA) +
#   geom_quasirandom(aes(fill = factor(sbj_id)), shape = 20, size=3, dodge.width = 0.5, alpha = 0.2, show.legend = F, width = 0.4) +
#   # geom_boxplot(aes(color = factor(complexity)), outlier.shape = NA) +
#   theme_classic()+
#   theme(legend.position = "none", axis.text=element_text(size=25, color = "black"), axis.text.x=element_text(size = 25), axis.title=element_text(size=25), axis.title.x = element_blank(),
#         plot.title=element_text(size=20,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
#   scale_color_manual(values = c("#bc5090","#003f5c","#fec107")) +
#   # scale_fill_manual(values = c("#bc5090", "#003f5c","#fec107")) +
#   labs(y = "Mean total duration") +
#   scale_x_discrete(labels = c("Suffixed\n", "High frequency\nendings", "Low frequency\nendings"), position = "bottom") +
#   scale_y_continuous(limits = c(200, 4000), breaks = seq(200, 4000, 500))


# Your existing code for p_gaze and p_tot

# Create a shared legend for p_gaze and p_tot
legend <- get_legend(p_gaze + theme(legend.position="right"))

# Arrange the plots and the legend into a single plot
combined_plot <- plot_grid(p_gaze + theme(legend.position="none"), p_tot + theme(legend.position="none"), legend, ncol = 3, align = 'h')


# Add a unique x-axis name
combined_plot_with_label <- ggdraw() +
  draw_plot(combined_plot) +
  draw_label("Trial number", x = 0.3, y = 0.01, 
size = 22, 
hjust = 0, vjust = 0)

# Show the plot
combined_plot_with_label

# save the plot to the current directory
# ggsave(filename = "gaze_total_learning_presentation.png", width = 350, height = 100, units = "mm")

# plot model estimates
# gaze
# model gaze duration
m_gaze_target <- lmer(log(gaze_dur_target) ~ complexity * target_order + (1|sbj_id) + (1|target), data = mydata)
summary(m_gaze_target)

# get model means
df_effects_m_gaze<-as.data.frame(effect("complexity:target_order", mod=m_gaze_target))

# relevel complexity variable
df_effects_m_gaze$complexity = factor(df_effects_m_gaze$complexity, levels = c("sf", "hf", "lf"))


p_model_gaze <- ggplot(data = df_effects_m_gaze, aes(x = factor(complexity), y = exp(fit), color = factor(complexity))) +
  # geom_point(aes(x = target_order, y = exp(fit), color = factor(complexity)), size = 4, alpha = 0.4) +
  geom_line(aes(x = target_order, y = exp(fit), color = complexity), size = 1.2) +
  geom_ribbon(aes(x=target_order, ymin = exp(lower), ymax = exp(upper), fill = factor(complexity)), alpha = 0.1, color = NA) +
  theme_classic() +
  theme(legend.position = "right", 
        legend.text = element_text(size = 15), 
        legend.title = element_text(size = 15), 
        strip.text.x = element_text(size = 18, color = "black"), 
        strip.background = element_rect("white"), 
        axis.text = element_text(size = 18, color = "black"),  # Increased axis text size
        axis.title = element_text(size = 22),  # Increased axis title size
        axis.title.x = element_blank(), 
        plot.title = element_text(size = 24, face = "bold"), 
        panel.grid.major.x = element_blank(), 
        panel.grid.minor.x = element_blank(),
        panel.border = element_rect(color = "black", fill = NA, size = 1),  # Added panel border
        plot.margin = margin(1, 1, 1, 1, "cm")) +  # Adjusted plot margins
  guides(alpha = "none") + 
  scale_color_manual(values = c("#bc5090","#003f5c","#fec107"), guide = "none", labels = c("Suffix", "High frequency ending", "Low frequency ending")) +
  scale_fill_manual(values = c("#bc5090", "#003f5c","#fec107"), "Type of ending", labels = c("Suffix", "High frequency ending", "Low frequency ending")) +
  labs(y = "Gaze durations (in ms)") +
  scale_y_continuous(limits = c(300, 900), breaks = seq(300, 900, 100)) +
  scale_x_continuous(limits = c(1,10), breaks = seq(1,10,1))

p_model_gaze 
  
# total durations
# model total durations
m_tot_target <- lmer(log(tot_dur_target) ~ complexity*target_order + (1|sbj_id) + (1|target), data = mydata )
summary(m_tot_target)


# get model means
df_effects_m_tot_dur<-as.data.frame(effect("complexity:target_order", mod=m_tot_target))

# relevel complexity variable
df_effects_m_tot_dur$complexity = factor(df_effects_m_tot_dur$complexity, levels = c("sf", "hf", "lf"))


p_model_tot <- ggplot(data = df_effects_m_tot_dur, aes(x = factor(complexity), y = exp(fit), color = factor(complexity))) +
  # geom_point(aes(x = target_order, y = exp(fit), color = factor(complexity)), size = 4, alpha = 0.4) +
  geom_line(aes(x = target_order, y = exp(fit), color = complexity), size = 1.2) +
  geom_ribbon(aes(x=target_order, ymin = exp(lower), ymax = exp(upper), fill = factor(complexity)), alpha = 0.1, color = NA) +
  theme_classic() +
  theme(legend.position = "right", 
        legend.text = element_text(size = 15), 
        legend.title = element_text(size = 15), 
        strip.text.x = element_text(size = 18, color = "black"), 
        strip.background = element_rect("white"), 
        axis.text = element_text(size = 18, color = "black"),  # Increased axis text size
        axis.title = element_text(size = 22),  # Increased axis title size
        axis.title.x = element_blank(), 
        plot.title = element_text(size = 24, face = "bold"), 
        panel.grid.major.x = element_blank(), 
        panel.grid.minor.x = element_blank(),
        panel.border = element_rect(color = "black", fill = NA, size = 1),  # Added panel border
        plot.margin = margin(1, 1, 1, 1, "cm")) +  # Adjusted plot margins
  guides(alpha = "none") + 
  scale_color_manual(values = c("#bc5090","#003f5c","#fec107"), guide = "none", labels = c("Suffix", "High frequency ending", "Low frequency ending")) +
  scale_fill_manual(values = c("#bc5090", "#003f5c","#fec107"), "Type of ending", labels = c("Suffix", "High frequency ending", "Low frequency ending")) +
  labs(y = "Total durations (in ms)") +
  scale_y_continuous(limits = c(500, 2300), breaks = seq(500, 2300, 200)) +
  scale_x_continuous(limits = c(1,10), breaks = seq(1,10,1))

p_model_tot
# Create a shared legend for p_gaze and p_tot
legend_model <- get_legend(p_model_tot + theme(legend.position="right"))

# Arrange the plots and the legend into a single plot
combined_plot_model <- plot_grid(p_model_gaze + theme(legend.position="none"), p_model_tot + theme(legend.position="none"), legend_model, ncol = 3, align = 'h')


# Add a unique x-axis name
combined_plot_with_label_model <- ggdraw() +
  draw_plot(combined_plot_model) +
  draw_label("Trial number", x = 0.3, y = 0.01, 
             size = 22, 
             hjust = 0, vjust = 0)

# Show the plot
combined_plot_with_label_model

# save the plot to the current directory
# ggsave(filename = "gaze_total_learning_model_presentation.png", width = 350, height = 100, units = "mm")






