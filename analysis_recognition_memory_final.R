# Analysis pipeline for Recognition Memory Task in Novel Word Learning study
# includes 1. data preparation; 2. modeling of accuracy results and plot; 3. calculation of d prime
# Olga Solaja
# 28-6-2022
# SISSA - International school for Advanced studies, Trieste


#### 1-data preparation ####

#clean environment
rm(list = ls())

#import libraries
library(ggplot2) # plots
library(data.table) # read in data
library(tidyverse) # data wrangling
library(lme4) # (g)lmer
# library(effects) # get model estimates
# library(MASS) # boxcox ## MASS package clases with "select()" function in dplyr/tidyverse; SOLUTION: specify MASS:: where needed
library(interactions) # plot interactions
library(jtools) # pretty model summaries
library(effects)
# disable scientific notation
options(scipen = 999)

#set working directory
setwd("C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\\Olga_experiment\\Analyses_main\\recognition_memory\\outputs")


#import results
files <- list.files(pattern = ".csv")
temp <- lapply(files, fread, sep=",")
rmt_data <- rbindlist(temp[2:86]) # because we exclude the ppt 1
rm(temp,files)

# column names are shifted, fix this
rmt_data <- rmt_data %>% rename("some_number" = "target_complexity", "target_complexity" = "target", "target" = "simple_id")


# relevel complexity variable
rmt_data$target_complexity = factor(rmt_data$target_complexity, levels = c("lf", "hf", "sf"))

# ADDED
# create accuracy column
rmt_data <- rmt_data %>% mutate(acc = if_else(ans == "l" & distractor_type == "corr" | ans == "s" & distractor_type != "corr", 1,0))

# load mif dataset

# go up one directory
setwd("..")

mif_data <- fread("mif_11-10-2023.csv", header=T, sep = ",", stringsAsFactors = FALSE)

# merge datasets
results <- merge(mif_data, rmt_data, by = "sbj_id")

# delete participants 1 and 86
results <- results %>% filter(!sbj_id %in% c(1))

# rename columns
results <- results %>% rename("mif" = "final_MIE")

# delete columns I don't need
results <- results %>% dplyr::select(c("sbj_id", "mif", "rot", "target_complexity", "target", "distractor_type", "ans", "rt", "acc"))


# D-prime analysis to decide on exclusion ---------------------------------

source('dPrimes.R')

# ADDED
results <- mutate(results, expected_resp=ifelse(distractor_type=="corr","l","s"))

# add a column with a given response
results <- mutate(results, given_resp=ans)

# apply dPrime function from dPrimes.R
sbj_dprime <- dPrime(results$sbj_id, results$expected_resp, results$given_resp); # participants 15 25 33 35 37 39 62 64 71 have d-prime under 1

# mean dprime across subjects
summary(sbj_dprime)

# dPrime across complexity
suff_subset <- results %>% subset(target_complexity=="sf" | is.na(target_complexity))

suff_dprime <- dPrime(suff_subset$sbj_id, suff_subset$expected_resp, suff_subset$given_resp);

hf_subset <- results %>% subset(target_complexity=="hf" | is.na(target_complexity))

hf_dprime <- dPrime(hf_subset$sbj_id, hf_subset$expected_resp, hf_subset$given_resp);

lf_subset <- results %>% subset(target_complexity=="lf" | is.na(target_complexity))

lf_subset$expected_resp <-as.factor(lf_subset$expected_resp)
lf_subset$given_resp <-as.factor(lf_subset$given_resp)

lf_dprime <- dPrime(lf_subset$sbj_id, lf_subset$expected_resp, lf_subset$given_resp);

lf_dprime_rem <- lf_dprime %>% filter(!sbj %in% c(15, 25))

  
round(mean(suff_dprime$dprime), digits=2)
round(mean(hf_dprime$dprime), digits=2)
round(mean(lf_dprime_rem$dprime), digits=2)


### exclude 
results <- results %>% filter(!sbj_id %in% c(15, 25, 33, 35, 37, 39, 62, 64, 71))

#### 2-descriptive stats ####

# DESCRIPTIVE STATS
round(mean(results$acc), digits = 2) # this includes also NO responses

descriptives <- aggregate(acc ~ target_complexity, FUN = mean, results) # target_complexity doesn't exist for distractors, only for the trained data

sd <- aggregate(acc ~ target_complexity, FUN = sd, results)
names(sd)[2] ="sd"


results <- results %>% mutate_at(c("mif", "rt", "acc"), as.integer) %>%
  mutate_at(c("sbj_id", "rot", "target_complexity", "target", "distractor_type", "ans", "expected_resp", "given_resp"), as.factor) 

#### 3-modelling ####

# set treatment contrasts
results$target_complexity <-as.factor(results$target_complexity)
contrasts(results$target_complexity) <- contr.treatment(levels(results$target_complexity))

# ADDED
m_acc <- glmer(acc ~ target_complexity + (1|sbj_id) + (1|target), family = "binomial", data = results %>% filter(distractor_type == "corr"))
summary(m_acc)

car::Anova(m_acc)

# conf intervals
round(confint.merMod(m_acc, method="Wald"), digits = 2)




# Exploratory analysis ----------------------------------------------------
# 
# exp_m_acc <- glmer(acc ~ mif*target_complexity + (1|sbj_id) + (1|target), family = "binomial", data = results %>% filter(distractor_type == "corr"))
# summ(exp_m_acc)




# plot
plot_data <- results %>% filter(distractor_type == "corr")


plot_data <- plot_data %>%
  group_by(target_complexity, sbj_id) %>% 
  summarise(n=n(), mean_acc = mean(acc), sd_acc = sd(acc), ci_upper = qt(0.975, df = n - 1) * sd_acc / sqrt(n), ci_lower = qt(0.025, df = n - 1) * sd_acc / sqrt(n))


library(wesanderson)
plot_data$target_complexity = factor(plot_data$target_complexity, levels = c("sf", "hf", "lf"))


ggplot(plot_data, aes(x = factor(target_complexity), y = mean_acc, color = factor(target_complexity))) +
  geom_violin(aes(fill = factor(target_complexity)), alpha = 0.3, size = 1.5, trim = T) +
  geom_boxplot(alpha = 0.3, width=0.1, size = 0.8, color="black", outlier.shape = NA) +
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
  scale_color_manual(values = c("#bc5090", "#003f5c","#fec107"), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  scale_fill_manual(values = c("#bc5090", "#003f5c","#fec107"), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  labs(y="Mean accuracy", x="") +
  scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, 0.2)) +
  scale_x_discrete(labels = c("Suffixed\n", "High frequency\nendings", "Low frequency\nendings"), position = "bottom")




# save the plot to the current directory
# ggsave(filename = "rmt_violin_presentation.png", width = 180, height = 130, units = "mm", limitsize = FALSE)


# plot model
m_acc <- glmer(acc ~ target_complexity + (1|sbj_id) + (1|target), family = "binomial", data = results %>% filter(distractor_type == "corr"))
summary(m_acc)


df_effects_m_acc<-as.data.frame(effect("target_complexity", mod=m_acc))

# relevel complexity variable
df_effects_m_acc$target_complexity = factor(df_effects_m_acc$target_complexity, levels = c("sf", "hf", "lf"))

ggplot(data = df_effects_m_acc, aes(x = factor(target_complexity), y = fit, color = factor(target_complexity))) +
  geom_point(size = 4, position = position_dodge(0.3)) +
  # geom_line(aes(group = 1), position = position_dodge(0.3)) + # Add this line for connecting points
  geom_errorbar(aes(ymin=lower, ymax=upper, alpha = 0.3, color = factor(target_complexity)), width = 0.1, size = 1.2, position = position_dodge(0.3)) +
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
  labs(y = "Mean accuracy", x = "", title = "Recognition memory") +
  scale_y_continuous(limits = c(0.5, 1), breaks = seq(0.5, 1, 0.1)) +
  scale_x_discrete(labels = c("Suffixed\n", "High frequency\nendings", "Low frequency\nendings"), position = "bottom")

# ggsave(filename = "rmt_model_estimate_paper2sssssss.png", width = 150, height = 100, units = "mm", limitsize = FALSE)

#










# plot for the presentation
# relevel complexity
results$target_complexity = factor(results$target_complexity, levels = c("sf", "hf", "lf","0"))


# fix what is factor etc in the dataframe and get rid of columns I don't need
results_plot <- results %>% filter(distractor_type == "corr")

results_plot <- results_plot %>% select(c(sbj_id, target_complexity, acc)) %>% mutate_at("sbj_id",as.factor)


results_plot <- results_plot %>% group_by(sbj_id,target_complexity) %>%
  summarise(n = n(), mean_acc = mean(acc), sd_acc = sd(acc),
            ci_upper = qt(0.975, df = n - 1) * sd_acc / sqrt(n), ci_lower = qt(0.025, df = n - 1) * sd_acc / sqrt(n))


# melted <- results_plot %>% melt(id.vars="sbj_id")

library(wesanderson)

ggplot(plot_data, aes(x = factor(target_complexity), y = mean_acc, color = factor(target_complexity))) +
  geom_violin(aes(fill = factor(target_complexity),  alpha = 0.5),size = 1) +
  geom_boxplot(alpha = 0.5, width=0.1, color="black", outlier.shape = NA) +
  # geom_quasirandom(aes(color=target_complexity), shape = 20, size=4, dodge.width = 1, alpha = 0.3, show.legend = F, width = 0.4) +
  # geom_jitter(height = c(0,1), width = 0.2, color = "black") +
  theme_light() +
  theme_light() + theme(legend.position = "none", axis.text=element_text(size=20), axis.title=element_text(size=24), axis.title.x = element_blank(),
                        plot.title=element_text(size=20,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
  scale_x_discrete(labels = c("Suffixed", "High frequency\nendings", "Low frequency\nendings")) +
  scale_y_continuous(limits = c(0.3, 1), breaks = seq(0.3, 1, 0.1)) +
  scale_color_manual(values = wes_palette("FantasticFox1", n = 3 )) +
  scale_fill_manual(values = wes_palette("FantasticFox1", n =3)) +
  labs(y="Mean accuracy")


