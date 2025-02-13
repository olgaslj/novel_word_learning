# Analysis pipeline for Definition Selection Task in Novel Word Learning study
# includes 1. data preparation; 2.analysis
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
library(car) # Anova
# library(MASS) # boxcox ## MASS package clases with "select()" function in dplyr/tidyverse; SOLUTION: specify MASS:: where needed

# disable scientific notation
options(scipen = 999)

# setwd
setwd("C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\\Olga_experiment\\Analyses_main\\definition_selection\\outputs")

# import data
files <- list.files(pattern = ".csv") #note that R should have set your working directory automatically to the location of the present script. If not, you'll have to set the working directory yourself.

# when I run the code under it says that the number of columns is different in some files, so check what are those files
# Loop through each CSV file and print the number of columns
# for (file in files) {
#   # Read the CSV file to get the number of columns
#   data <- read.csv(file, header = TRUE)
# 
#   # Get the number of columns in the current CSV file
#   num_columns <- ncol(data)
# 
#   # Print the file name and number of columns
#   cat("File:", file, "Number of Columns:", num_columns, "\n")
# }

temp <- lapply(files, fread, sep=",")
results <- rbindlist(temp, fill = F)
rm(files,temp)

# exclude ppt 3 due to an error in the experimental script
# results <- results %>% filter(sbj_id!=3)

# ADDED
# create complexity LT column (that shows the actual compelxity of the items to which they were exposed in training)
results <- results %>%
  mutate(complexity_LT=case_when(
    rot_LT == 1 ~ complexity_LT_rot_1,
    rot_LT == 2 ~ complexity_LT_rot_2,
    rot_LT == 3 ~ complexity_LT_rot_3,
  ))


# relevel complexity variable
results$complexity_LT = factor(results$complexity_LT, levels = c("sf", "hf", "lf"))

#rename columns
results = results %>% rename (trial_id = V1,acc=accuracy)

# transform accuracy column into 1,0
results_all = mutate(results, acc=ifelse(acc=="yes",1,0))

# keep only columns we need
results <- results_all %>% dplyr::select(c("sbj_id", "rot_LT", "id", "test_novel_word", "RT", "acc", "complexity_LT"))

### exclude participants with low d-prime
results <- results %>% filter(!sbj_id %in% c(15, 25, 33, 35, 37, 39, 62, 64, 71))

# three participants were assigned correct rotations but was noted wrong
results[sbj_id == 35, rot_LT := 2] # this person is already excluded
results[sbj_id == 36, rot_LT := 3]
results[sbj_id == 46, rot_LT := 1]


#### 2-descriptive stats ####

round(mean(results$acc), digits = 2)

descriptives <- aggregate(acc ~ complexity_LT, FUN=mean, results)
descriptives$sd <- aggregate(acc ~ complexity_LT, FUN=sd, results)

#### 3-modelling ####

# modeling accuracy

# relevel complexity variable
results$complexity_LT = factor(results$complexity_LT, levels = c("lf", "hf", "sf"))

# set treatment contrasts
results$complexity_LT <-as.factor(results$complexity_LT)
contrasts(results$complexity_LT) <- contr.treatment(levels(results$complexity_LT))

m_acc <- glmer(acc ~ complexity_LT + (1|sbj_id), family="binomial", data = results)
summary(m_acc)

# confidence intervals
round(confint.merMod(m_acc, method="Wald", level = 0.95),digits=2)


# plot for presentation

plot_data <- results %>% group_by(complexity_LT, sbj_id) %>%
  summarise(n = n(), mean_rt = mean(RT), mean_acc = mean(acc), sd_rt = sd(RT), sd_acc = sd(acc), ci_upper_acc = qt(0.975, df = n - 1) * sd_acc / sqrt(n), ci_lower_acc = qt(0.025, df = n - 1) * sd_acc / sqrt(n),
            sem_acc = sd_acc/sqrt(n-1))


ggplot(plot_data, aes(x = factor(complexity_LT), y = mean_acc, color = factor(complexity_LT))) +
  geom_violin(aes(fill = factor(complexity_LT)), alpha = 0.3, size = 1.5, trim = T) +
  geom_boxplot(alpha = 0.3, width=0.1, size = 0.8, color="black", outlier.shape = NA) +
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
  scale_color_manual(values = c("#003f5c","#bc5090","#fec107"), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  scale_fill_manual(values = c("#003f5c","#bc5090","#fec107"), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  labs(y="Mean accuracy", x="") +
  scale_x_discrete(labels = c("Suffixed\n", "High frequency\nendings", "Low frequency\nendings"), position = "bottom") +
  ylim(0, 1)


# ggsave("dst_accuracy_presentation.png", width = 180, height = 130, units = "mm", limitsize = FALSE)
# 
# plot model
m_acc <- glmer(acc ~ complexity_LT + (1|sbj_id), family="binomial", data = results)
summary(m_acc)

library(effects)
library(wesanderson)
df_effects_m_acc<-as.data.frame(effect("complexity_LT", mod=m_acc))

# relevel complexity variable
df_effects_m_acc$complexity_LT = factor(df_effects_m_acc$complexity_LT, levels = c("sf", "hf", "lf"))

ggplot(data = df_effects_m_acc, aes(x = factor(complexity_LT), y = fit, color = factor(complexity_LT))) +
  geom_point(size = 4, position = position_dodge(0.3)) +
  # geom_line(aes(group = 1), position = position_dodge(0.3)) + # Add this line for connecting points
  geom_errorbar(aes(ymin=lower, ymax=upper, alpha = 0.3, color = factor(complexity_LT)), width = 0.1, size = 1.2, position = position_dodge(0.3)) +
  theme_light() +
  theme(legend.position = "none",  legend.text = element_text(size=12),legend.title = element_text(size=12), axis.text=element_text(size=14), axis.title=element_text(size=14),
        plot.title=element_text(size=24,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
  scale_color_manual(values = wes_palette("FantasticFox1", n =3), guide = "none", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  scale_fill_manual(values = wes_palette("FantasticFox1", n =3), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  guides(alpha = "none") + 
  # scale_color_manual(values = c("#bc5090", "#003f5c","#fec107"), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  # scale_fill_manual(values = c("#bc5090", "#003f5c","#fec107"), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  # scale_color_manual(values = wes_palette("FantasticFox1", n =3), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  # scale_fill_manual(values = wes_palette("FantasticFox1", n =3), "Complexity", labels = c("Suffixed", "High frequency ending", "Low frequency ending")) +
  labs(y = "Mean accuracy", x = "") +
  scale_y_continuous(limits = c(0.5, 1), breaks = seq(0.5, 1, 0.1)) +
  scale_x_discrete(labels = c("Suffixed\n", "High frequency\nendings", "Low frequency\nendings"), position = "bottom")

ggsave(filename = "dst_model_estimate_paper25.png", width = 150, height = 100, units = "mm", limitsize = FALSE)

# plot responses




button_counts <- results_all %>% filter(acc == 0) %>% group_by(complexity_LT) %>%
  summarise(
    buttonIncom = sum(buttonIncom == "x"),
    buttonOverCat = sum(buttonOverCat == "x"),
    buttonMeanInc = sum(buttonMeanInc == "x")
  )

# Reshape the data frame for plotting
button_counts <- button_counts %>%
  pivot_longer(cols = starts_with("button"),
               names_to = "button_type",
               values_to = "count")

# Plotting
ggplot(button_counts, aes(x = button_type, y = count, fill = factor(button_type))) +
  geom_bar(stat = "identity") +
  labs(x = "Button Type", y = "Count", title = "Button Selection Counts") +
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
  scale_color_manual(values = c("#003f5c","#bc5090","#fec107")) +
  scale_fill_manual(values = c("#003f5c","#bc5090","#fec107")) +
  # labs(y="Mean accuracy", x="") +
  scale_x_discrete(labels = c("Incompatible\nmeaning", "Switched\nmeaning", "Overarching\ncategory"), position = "bottom") +
  # ylim(0, 1) +
  labs(x="Distractor condition", title = "Mistakes across distractors")


# ggsave("dst_distractors_presentation_incorrect_responses.png", width = 180, height = 130, units = "mm", limitsize = FALSE)



