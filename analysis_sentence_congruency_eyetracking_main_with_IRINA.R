# Analysis pipeline for Sentence Congruency Task in Novel Word Learning study
# includes 1. data preparation; 2. modeling of eye-tracking measures; 3. plotting
# Olga Solaja
# 28-6-2022
# SISSA - International school for Advanced studies, Trieste


# Prepare data ------------------------------------------------------------

# fixations shorter than 80ms are discarded in the file used here (output_ETSCT_main_final_10-10-23.csv)

#clean environment
rm(list = ls())

#import libraries
library(ggplot2) # plots
library(data.table) # fread in input
library(tidyverse) # data wrangling
library(lme4) # (g)lmer
library(lmerTest)
# library(effects) # get model estimates
# library(MASS) # boxcox ## MASS package clashes with "select()" function in dplyr/tidyverse; SOLUTION: specify MASS:: where needed
library(wesanderson)

# disable scientific notation
options(scipen = 999)

# import data
eyetracking <- read.csv("output_ETSCT_main_final_10-10-23.csv", header = T, fileEncoding = "UTF-8-BOM")
  
# merging behavioral and eyetracking data so that I can get the complexity info

behavioral <- read.csv("merged_behavioral_final.csv", header = T, fileEncoding = "UTF-8-BOM")
behavioral <- behavioral %>% rename(sent_id = id_sct)

# load mif dataset
setwd("..")
mif_data <- fread("mif_11-10-2023.csv", header=T, sep = ",", stringsAsFactors = FALSE)

# merge datasets
bhv_et_data <- merge(behavioral, eyetracking, by = c("sbj_id", "sent_id", "congruency", "rot"))

# add mif data
all_data <- merge(bhv_et_data, mif_data, by = "sbj_id")


# delete participants 1 and 86
all_data <- all_data %>% filter(!sbj_id %in% c(1, 86))


# ADDED create complexity_LT
all_data <- all_data %>%
  mutate(complexity_LT=case_when(
    rot_LT == 1 ~ complexity_LT_rot_1,
    rot_LT == 2 ~ complexity_LT_rot_2,
    rot_LT == 3 ~ complexity_LT_rot_3,
  ))

#rename columns
all_data<-rename(all_data, order_out = X)
all_data<-rename(all_data, mif = final_MIE)


# relevel complexity variable
all_data$complexity_LT = factor(all_data$complexity_LT, levels = c("sf", "hf", "lf"))

# rename congruency column yes/no
all_data <- all_data %>%
  mutate(congruency=case_when(
    congruency == "yes" ~ "congruent",
    congruency == "no" ~ "incongruent"
  ))

# relevel congruency variable (baseline is "incongruent")
all_data$congruency = factor(all_data$congruency, levels = c("incongruent", "congruent"))

# substitute 0 with NA
mydata <- all_data %>%  mutate_at(c("tot_dur","init_dur","fomf_dur","gaze_dur","ssp_dur"), ~na_if(., 0))


### exclude participants with low d-prime
mydata <- mydata %>% filter(!sbj_id %in% c(15, 25, 33, 35, 37, 39, 62, 64, 71))



#### 2-descriptive stats ####

# mean number of fixations overall
round(mean(mydata$count_fix, na.rm=T),digits=2)

# percentage of refixations
round(mean(is.na(mydata$single_fix)), digits = 2)

#### 3-modelling ####

# set treatment contrasts
mydata$complexity_LT <-as.factor(mydata$complexity_LT)
contrasts(mydata$complexity_LT) <- contr.treatment(levels(mydata$complexity_LT))
mydata$complexity_LT <- relevel(mydata$complexity_LT, 'lf')

mydata$congruency <- as.factor(mydata$congruency)
contrasts(mydata$congruency) <- contr.treatment(levels(mydata$congruency))


# GAZE DURATIONS
dev.off()
MASS::boxcox(mydata$gaze_dur ~ 1)

par(mfrow=c(1,4))
hist(mydata$gaze_dur, 20)
hist(mydata$gaze_dur[mydata$gaze_dur])
hist(log(mydata$gaze_dur)) # this is the best according to boxcox and histogram
hist(1/mydata$gaze_dur)
par(mfrow=c(1,1))

# model gaze durations
mydata$complexity_LT <- relevel(mydata$complexity_LT, 'lf');
m_gaze <- lmer(log(gaze_dur) ~ complexity_LT*congruency + (1|sbj_id) + (1|baseword), data = mydata )
summary(m_gaze)

# confidence intervals
round(confint.merMod(m_gaze, method="Wald"), digits=2)


#  TOTAL DURATIONS
dev.off()
MASS::boxcox(mydata$tot_dur ~ 1)

par(mfrow=c(1,4))
hist(mydata$tot_dur, 20)
hist(mydata$tot_dur[mydata$tot_dur])
hist(log(mydata$tot_dur))
hist(1/mydata$tot_dur)
par(mfrow=c(1,1))

mydata$complexity_LT <- relevel(mydata$complexity_LT, 'lf');
m_tot <- lmer(log(tot_dur) ~ complexity_LT*congruency + (1|sbj_id) + (1|baseword), data = mydata)
summary(m_tot)

m_tot_new <- lmer(log(tot_dur) ~ complexity_LT + congruency + (1|sbj_id) + (1|baseword), data = mydata) # get rid of interaction to see what happens

anova(m_tot_new, m_tot) # compare two models: they seems to be equally valid (p > 0.1)

# the interaction was not statistically significant but it was theoretically important so we check with emmeans it the more complex model
emmeans::emmeans(m_tot, pairwise ~  congruency | complexity_LT) # we see that in lf there's difference between congruent and incongruent and also in high frequency, but not in suffixed, exactly as the graph shows

# confidence intervals
round(confint.merMod(m_tot, method="Wald"), digits=2)

#### 4-plots ####

tot_data <- mydata %>% group_by(congruency , complexity_LT) %>%
  summarise(n = n(), mean_rt = mean(na.omit(tot_dur)), sd_rt = sd(na.omit(tot_dur)),
            ci_upper = qt(0.975, df = n - 1) * sd_rt / sqrt(n), ci_lower = qt(0.025, df = n - 1) * sd_rt / sqrt(n),
            sem = sd_rt/sqrt(n-1))


tot_data$complexity_LT = factor(tot_data$complexity_LT, levels = c("sf", "hf", "lf"))

p_tot <- ggplot(tot_data) +
  geom_point(aes(x = complexity_LT, y = mean_rt, color = congruency), size = 4, alpha = 0.7, position = position_dodge(width = 0.3)) +
  geom_line(aes(x = complexity_LT, y = mean_rt, group = congruency, color = congruency), size = 1, position = position_dodge(width = 0.3)) +
  geom_errorbar(aes(x=complexity_LT,ymin = mean_rt - sem, ymax = mean_rt + sem, color = factor(congruency)), width = 0.3, size = 0.75, alpha = 0.7, position = position_dodge(width = 0.3)) +
  theme_light() +
  theme(legend.position = "right",  legend.text = element_text(size=12),legend.title = element_text(size=12), axis.text=element_text(size=14), axis.title=element_text(size=14),
        plot.title=element_text(size=24,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
  scale_color_manual(values = wes_palette("FantasticFox1", n =3),  "Congruency", labels = c("Incongruent", "Congruent")) +
  scale_fill_manual(values = wes_palette("FantasticFox1", n =3), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  labs(y="Total durations", x="Complexity in the Learning task") +
  scale_x_discrete(labels = c("Suffixed\n", "High frequency\nendings", "Low frequency\nendings"), position = "bottom")


p_tot
# save the plot to the current directory
# ggsave(filename = "tot_dur_final_congXcomplexity.png", width = 250, height = 100, units = "mm")



gaze_data <- mydata %>% group_by(congruency , complexity_LT) %>%
  summarise(n = n(), mean_rt = mean(na.omit(gaze_dur)), sd_rt = sd(na.omit(gaze_dur)),
            ci_upper = qt(0.975, df = n - 1) * sd_rt / sqrt(n), ci_lower = qt(0.025, df = n - 1) * sd_rt / sqrt(n),
            sem = sd_rt/sqrt(n-1))


gaze_data$complexity_LT = factor(gaze_data$complexity_LT, levels = c("sf", "hf", "lf"))

p_gaze <- ggplot(gaze_data) +
  geom_point(aes(x = complexity_LT, y = mean_rt, color = congruency), size = 4, alpha = 0.7, position = position_dodge(width = 0.3)) +
  geom_line(aes(x = complexity_LT, y = mean_rt, group = congruency, color = congruency), size = 1, position = position_dodge(width = 0.3)) +
  geom_errorbar(aes(x=complexity_LT,ymin = mean_rt - sem, ymax = mean_rt + sem, color = factor(congruency)), width = 0.3, size = 0.75, alpha = 0.7, position = position_dodge(width = 0.3)) +
  theme_light() +
  theme(legend.position = "right",  legend.text = element_text(size=12),legend.title = element_text(size=12), axis.text=element_text(size=14), axis.title=element_text(size=14),
        plot.title=element_text(size=24,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
  scale_color_manual(values = wes_palette("FantasticFox1", n =3),  "Congruency", labels = c("Incongruent", "Congruent")) +
  scale_fill_manual(values = wes_palette("FantasticFox1", n =3), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  labs(y="Gaze durations", x="Complexity in the Learning task") +
  scale_x_discrete(labels = c("Suffixed\n", "High frequency\nendings", "Low frequency\nendings"), position = "bottom")


p_gaze



# Exploratory analysis ----------------------------------------------------

# I SHOULD DO THIS BECAUSE THE MODEL WITHOUT MIF SHOWED NO EFFECT OF COMPLEXITY
# gaze durations
mydata$complexity_LT = factor(mydata$complexity_LT, levels = c("lf", "hf", "sf"))

exp_m_gaze <- lmer(log(gaze_dur) ~ complexity_LT*congruency*mif + (1|sbj_id) + (1|baseword), data = mydata )
summary(exp_m_gaze)

# confidence intervals
round(confint.merMod(exp_m_gaze, method="Wald"), digits=2)


predictors <- expand.grid(complexity = c("level1", "level2"),
                          congruency = c("levelA", "levelB"))


effect_plot <- allEffects(exp_m_gaze, predictors = predictors)
plot(effect_plot)



# plot
# complexity:target_order:mif
# have to create a dummy numeric variable for congruency in the model
mydata$congruency_dummy <- as.numeric(factor(mydata$congruency))

# Now, you can use 'congruency_dummy' in your lmer model
dummy_exp_m_gaze <- lmer(log(gaze_dur) ~ complexity_LT * congruency_dummy * mif + (1|sbj_id) + (1|baseword), data = mydata)
summary(dummy_exp_m_gaze)

mydata$complexity_LT = factor(mydata$complexity_LT, levels = c("sf", "hf", "lf"))
x_axis_labs <- c("Incongruent", "Congruent")

interact_plot(dummy_exp_m_gaze, pred = congruency_dummy, modx = mif, mod2 = complexity_LT,
              plot.points = F, # overlay data
              # different shape for differennt levels of the moderator
              point.shape = T, 
              jitter = 0.1, 
              x.label = "Congruency", 
              y.label = "log(gaze durations)",
              # main.title = "SCT - Gaze durations as a function of MIF x congruency x complexity interaction",
              legend.main = "MIF",
              colors = wes_palette("FantasticFox1", n = 3),
              # include confidence band
              interval = TRUE, 
              int.width = 0.9, 
              robust = T,
              modx.values = c("-2 SD" = mean(mydata$mif) - sd(mydata$mif)*2, 
                              "Mean" = mean(mydata$mif), 
                              "2 SD" = mean(mydata$mif) + sd(mydata$mif)*2),
              mod2.labels = c("Suffixed", "High frequency", "Low frequency")) +
  theme_light() +
  theme(legend.position = "right",  legend.text = element_text(size=12),legend.title = element_text(size=12), axis.text=element_text(size=14), axis.text.x=element_text(size=14),axis.title=element_text(size=14),
        plot.title=element_text(size=24,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank(), strip.text = element_text(size = 14)) +
scale_x_continuous(breaks = 1:2, labels = x_axis_labs)



# ggsave(filename = "SCT_gaze_mif_congruency_complexity.png", width = 250, height = 100, units = "mm")




# total durations
exp_m_tot <- lmer(log(tot_dur) ~ complexity_LT*congruency*mif + (1|sbj_id) + (1|baseword), data = mydata)
summary(exp_m_tot)






