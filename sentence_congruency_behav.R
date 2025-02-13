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
results <- rbindlist(temp)
rm(temp,files)

# exclude participant 3 because of error in the experimental code
# results = results %>% filter(sbj_id!=3)

# rename column
# results = results %>% rename(trial_id = V1)

# create accuracy column
results<-mutate(results, acc=ifelse(congruency =="yes" & answ=="l" | congruency =="no" & answ=="s", 1, 0))

# create complexity LT column (that shows the actual compelxity of the items to which they were exposed in training)
results <- results %>%
  mutate(complexity_LT=case_when(
    rot_LT == 1 ~ complexity_LT_rot_1,
    rot_LT == 2 ~ complexity_LT_rot_2,
    rot_LT == 3 ~ complexity_LT_rot_3,
    ))


# relevel complexity variable
results$complexity_LT = factor(results$complexity_LT, levels = c("sf", "hf", "lf"))


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
actualDistribution <- rbinom(n=13, size=18, prob=.57) # real accuracy is 0.57 


ggplot() +
  geom_col(data=acc_data,aes(x=factor(sbj_id), y=mean_accuracy,  fill="red")) +
  geom_hline(yintercept = 0.50, size=1)+
  geom_hline(yintercept=quantile(nullDistribution, probs=0.95)/18, size=1, linetype="dashed") +
  theme_light() +
  theme(legend.position = "none",  legend.text = element_text(size=24),legend.title = element_text(size=24), axis.text=element_text(size=20), axis.title=element_text(size=24),
        plot.title=element_text(size=24,face="bold"), panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank()) +
  scale_fill_manual(values = wes_palette("FantasticFox1", n = 1)) +
  labs(x= "Participant number", y="Mean accuracy") +
  ylim(0,1)

# ggsave("etsct_behavioral.png",  width = 250, height = 200, units = "mm")

# plot difference across congruency conditions (grouped by sbj and complexity)
group_congruency <- results %>% group_by(sbj_id,congruency) %>%
  summarise(n = 13, mean_acc = mean(na.omit(acc)), sd_acc = sd(na.omit(acc)),
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

#### 4-power analysis ####
source("power_functions/simData_sentence_congruency_bhv.R");
source("power_functions/computePower_sentence_congruency_bhv.R");
source("power_functions/powerCurve_sentence_congruency_bhv.R");

#computer the model to estimate an effect size
m_acc <- glmer(acc ~ congruency*complexity_LT + (1|sbj_id) + (1|sent), family="binomial", data=results)
#and cut them down to 2/3, as per the rest of the analysis (the small sample of the pilot might have surely mischaracterised the effect size)
fixef(m_acc)*2/3

#try out the function with only 10 replicates
computePower(n_repl=10, beta_0=-0.04442360, beta_cong=0.45419664, beta_hf=0.15906673, beta_sf=-0.06653686, beta_hfC=-0.08138836, beta_SfC=0.07546428);

# #now let's run the power curve. Contrary to the previous tasks (learning and recognition memory), here will fix the effect size within the simulations, and check which sample size would allow us to reach that effect size
# png("p_sct_bhv.png")
# powerCurve(n_repl=1000, steps=seq(0.05,0.5,0.05), whichTest='F', threshold=.02) 
# dev.off()



# EXPLORATIONS

# relevel complexity variable
results$complexity_LT = factor(results$complexity_LT, levels = c("lf", "hf", "sf"))

m_acc <- glmer(acc ~ complexity_LT + (1|sbj_id) + (1|sent), family = "binomial", results)
summary(m_acc)







