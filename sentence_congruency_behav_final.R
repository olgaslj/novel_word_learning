# Analysis pipeline for behavioral data in Sentence Congruency Task in Novel Word Learning study
# includes 1. data preparation; 2. descriptive stats
# Olga Solaja
# 28-6-2022
# SISSA - International school for Advanced studies, Trieste

#### 1-data preparation ####

# clean environment
rm(list = ls())

# import libraries
library(ggplot2) # plots
library(data.table) # read in data
library(tidyverse) # data wrangling
library(lme4) # (g)lmer
library(lmerTest)
# library(effects) # get model estimates
# library(MASS) # boxcox ## MASS package clases with "select()" function in dplyr/tidyverse; SOLUTION: specify MASS:: where needed
library(wesanderson) # color palette for plots

# disable scientific notation
options(scipen = 999)

# setwd
setwd("C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\\Olga_experiment\\Analyses_main\\sentence_congruency\\behavioral\\cleaned")


#import data
files <- list.files(pattern = ".csv")
temp <- lapply(files, fread, sep=",",encoding='UTF-8')
sct_data <- rbindlist(temp)
rm(temp,files)



# load mif dataset
setwd("..")
mif_data <- fread("mif_11-10-2023.csv", header=T, sep = ",", stringsAsFactors = FALSE)


# merge datasets
results <- merge(mif_data, sct_data, by = "sbj_id")

# exclude participant 1
results <- results %>% filter(!sbj_id %in% c(1))

# create accuracy column
results<-mutate(results, acc=ifelse(congruency =="yes" & answ=="l" | congruency =="no" & answ=="s", 1, 0))

# create complexity LT column (that shows the actual complexity of the items to which they were exposed in training)
results <- results %>%
  mutate(complexity_LT=case_when(
    rot_LT == 1 ~ complexity_LT_rot_1,
    rot_LT == 2 ~ complexity_LT_rot_2,
    rot_LT == 3 ~ complexity_LT_rot_3,
    ))


# relevel complexity variable
results$complexity_LT = factor(results$complexity_LT, levels = c("sf", "hf", "lf"))

# rename column
results <- results %>% rename("mif" = "final_MIE")

### exclude participants with low d-prime
results <- results %>% filter(!sbj_id %in% c(15, 25, 33, 35, 37, 39, 62, 64, 71))


#### 2-descriptive stats ####

#overall mean
round(mean(results$acc), digits = 2)

descriptives <- aggregate(acc ~ complexity_LT, FUN=mean, results)
descriptives$sd <- aggregate(acc ~ complexity_LT, FUN=sd, results)

### 3-plots ####

# plot accuracy data per participant with chance level and threshold for learning success
acc_data <- results %>% 
  group_by(sbj_id) %>% 
  summarise(mean_accuracy = mean(acc), sd_acc = sd(acc))

nullDistribution <- rbinom(n=1000, size=18, prob=.50) # chance level is 0.50
actualDistribution <- rbinom(n=75, size=18, prob=.64) # real accuracy is 0.64 # 75 ppts after exclusion


ggplot() +
  geom_col(data=acc_data,aes(x=factor(sbj_id), y=mean_accuracy),  fill="#003f5c") +
  geom_hline(yintercept = 0.50, size=1)+
  geom_hline(yintercept=quantile(nullDistribution, probs=0.95)/18, size=1, linetype="dashed") +
  theme_light() +
  theme(legend.position = "none",  legend.text = element_text(size=24),legend.title = element_text(size=24), axis.text=element_text(size=20), axis.title=element_text(size=24),
        plot.title=element_text(size=24,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
  scale_fill_manual(values = wes_palette("FantasticFox1", n = 1)) +
  labs(x= "Participant number", y="Mean accuracy") +
  scale_x_discrete(limits = as.character(2:84), breaks = seq(2, 84, 5)) +
  ylim(0,1)

# ggsave("etsct_behavioral_presentation.png",  width = 250, height = 200, units = "mm")


# plot accuracy as violin plot for presentation

ggplot(acc_data, aes(x = "", y = mean_accuracy)) +
  geom_violin(fill = "#003f5c", color = "#003f5c", alpha = 0.3, size = 1.5, trim = T) +
  # geom_violin(aes(fill = factor(complexity_LT)), alpha = 0.3, size = 1.5, trim = T) +
  geom_boxplot(alpha = 0.3, width=0.1, size = 0.8, color="black", outlier.shape = NA) +
  geom_hline(yintercept = 0.5, linetype = "dashed", size = 1) +
  # geom_quasirandom(aes(color=complexity_LT), shape = 20, size=3, dodge.width = 1, alpha = 0.3, show.legend = F, width = 0.4) +
  theme_classic() +
  theme(legend.position = "none", 
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
  # scale_color_manual(values = c("#bc5090", "#003f5c","#fec107")) +
  # scale_fill_manual(values = c("#bc5090", "#003f5c","#fec107")) +
  labs(y="Mean accuracy", x="") +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, 0.2)) +
  scale_x_discrete(label = "Overall performance", position = "bottom")


# ggsave("etsct_behavioral_violinplot_presentation.png",  width = 130, height = 130, units = "mm")

# plot behavioral data across complexity for the paper
acc_data_complexity <- results %>% 
  group_by(sbj_id, complexity_LT) %>% 
  summarise(mean_accuracy = mean(acc), sd_acc = sd(acc))

ggplot(acc_data_complexity, aes(x = factor(complexity_LT), y = mean_accuracy, color = factor(complexity_LT))) +
  geom_violin(aes(fill = factor(complexity_LT)), alpha = 0.3, size = 1.5, trim = T) +
  geom_boxplot(alpha = 0.3, width=0.1, size = 0.8, color="black", outlier.shape = NA) +
  geom_hline(yintercept = 0.5, linetype = "dashed", size = 1) +
  theme_classic() +
  theme(legend.position = "none", 
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
  scale_color_manual(values = c("#bc5090", "#003f5c","#fec107")) +
  scale_fill_manual(values = c("#bc5090", "#003f5c","#fec107")) +
  labs(y="Mean accuracy", x="") +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, 0.2)) + 
  scale_x_discrete(labels = c("Suffixed\n", "High frequency\nendings", "Low frequency\nendings"), position = "bottom")

# ggsave("etsct_behavioral_complexity_violinplot_paper.png",  width = 200, height = 130, units = "mm")


  
# plot difference across congruency conditions (grouped by sbj and complexity)
group_congruency <- results %>% group_by(sbj_id,congruency) %>%
  summarise(n = n(), mean_acc = mean(na.omit(acc)), sd_acc = sd(na.omit(acc)),
            ci_upper = qt(0.975, df = n - 1) * sd_acc / sqrt(n), ci_lower = qt(0.025, df = n - 1) * sd_acc / sqrt(n))

ggplot(group_congruency, aes(x = congruency, y = mean_acc, color = factor(congruency))) +
  geom_violin(aes(fill = factor(congruency),  alpha = 0.5), trim=T, size = 1) +
  geom_boxplot(alpha = 0.5, width=0.1, color="black", outlier.shape = NA) +
  geom_jitter(height = c(0,1), width = 0.4, color = "black") +
  theme_light() +
  theme_light() + theme(legend.position = "none", axis.text=element_text(size=20), axis.title=element_text(size=24), axis.title.x = element_blank(), axis.text.x = element_text(colour = "black",face="bold"),
                        plot.title=element_text(size=20,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
  scale_x_discrete(labels = c("Incongruent", "Congruent")) +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, 0.1)) +
  scale_color_manual(values = wes_palette("FantasticFox1", n = 3 )) +
  scale_fill_manual(values = wes_palette("FantasticFox1", n =3)) +
  labs(y="Mean accuracy")

# save the plot in the current directory
# ggsave("congruency_behavioral.png",  width = 250, height = 200, units = "mm")


# Modeling ----------------------------------------------------------------


# relevel complexity variable
results$complexity_LT = factor(results$complexity_LT, levels = c("lf", "hf", "sf"))

m_acc <- glmer(acc ~ complexity_LT * congruency + (1|sbj_id) + (1|sent), family = "binomial", results)
summary(m_acc)

# conf intervals
round(confint.merMod(m_acc, method="Wald"), digits = 2)

# plot across complexity as a model
# get model means
df_effects_acc<-as.data.frame(effect("complexity_LT", mod=m_acc))

df_effects_acc$complexity_LT = factor(df_effects_acc$complexity_LT, levels = c("sf", "hf", "lf"))

p_model <- ggplot(data = df_effects_acc, aes(x = factor(complexity_LT), y = fit, color = factor(complexity_LT))) +
  geom_point(size = 4, position = position_dodge(0.3)) +
  # geom_line(aes(group = 1), position = position_dodge(0.3)) + # Add this line for connecting points
  geom_errorbar(aes(ymin=lower, ymax=upper, alpha = 0.3, color = factor(complexity_LT)), width = 0.1, size = 1.2, position = position_dodge(0.3)) +
  theme_light() +
  theme(legend.position = "none",  legend.text = element_text(size=12),legend.title = element_text(size=12), axis.text=element_text(size=14), axis.title=element_text(size=14),
        plot.title=element_text(size=20,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
  scale_color_manual(values = wes_palette("FantasticFox1", n =3), guide = "none", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  scale_fill_manual(values = wes_palette("FantasticFox1", n =3), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  guides(alpha = "none") + 
  # scale_color_manual(values = c("#bc5090", "#003f5c","#fec107"), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  # scale_fill_manual(values = c("#bc5090", "#003f5c","#fec107"), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  # scale_color_manual(values = wes_palette("FantasticFox1", n =3), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  # scale_fill_manual(values = wes_palette("FantasticFox1", n =3), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  labs(y = "Mean accuracy", x= "", title = "Sentence congruency - behavioural") +
  scale_y_continuous(limits = c(0.5, 1), breaks = seq(0.5, 1, 0.1)) +
  scale_x_discrete(labels = c("Suffixed\n", "High frequency\nendings", "Low frequency\nendings"), position = "bottom")

p_model 

# ggsave(filename = "sct_model_estimate_behavioral_complexity_paper2ssssssss.png", width = 150, height = 100, units = "mm", limitsize = FALSE)


# Exploratory analysis ----------------------------------------------------

exp_m_acc <- glmer(acc ~ complexity_LT * congruency * mif + (1|sbj_id) + (1|sent), family = "binomial", results)
summ(exp_m_acc)

# conf intervals
round(confint.merMod(exp_m_acc, method="Wald"), digits = 2)



predictors <- expand.grid(complexity = c("level1", "level2"),
                              congruency = c("levelA", "levelB"))


effect_plot <- allEffects(exp_m_acc, predictors = predictors)
plot(effect_plot)

