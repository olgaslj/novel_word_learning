# Analysis pipeline for Morpheme Interference Task in Novel Word Learning study
# includes 1. data preparation; 2. outlier cleaning; 3. calculation of Morpheme Interference Index; 4. modeling of RT and accuracy data
# 5-3-2021
# Olga Solaja and Davide Crepaldi
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
library(effects) # get model estimates
library(MASS) # boxcox

# disable scientific notation
options(scipen = 999)

setwd("C:\\Users\\olgas\\OneDrive - SISSA\\SISSA\\Projects\\Novel_Word_Learning\\Olga_experiment\\Analyses_main\\morpheme_interference")

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
# 
# temp <- lapply(files, fread, sep=",")
# all_data <- rbindlist(temp, fill = F)
# rm(files,temp)

# look for extreme outliers
hist(all_data$rt)

# delete extreme outliers
all_data <- all_data %>% filter(rt<10)

# rename column
names(all_data)[names(all_data) == "V1"] <- "trial_id"

# create accuracy column
all_data<-mutate(all_data, acc=ifelse(lexicality==1 & ans=="l"|lexicality==0 & ans=="s",1,0))

# select only nonwords for accuracy analysis (morpheme interference effect is calculated based on analyses of nonwords)
nonwords <- all_data %>% filter(lexicality==0)

# select only nonwords with correct answers for reaction time analysis
nonwordsRT <- nonwords %>% filter(acc==1)

#### 2-outliers in the filler items ####
# import code that gives graphic representation of performance separately for subjects and for items
source('diagnostics_mi.R')
attach(all_data)
diagnostics.f(rt, acc, sbj_id, target, lexicality, 'diagnostics_mi')
detach(all_data)

# ADDED should exclude urtevole definitely and flauteria because I made a mistake

all_data <- all_data %>% filter(target != c("urtevole", "flauteria"))


#### 3-calculation of the morpheme interference effect index ####

# based on ACCURACY data
# find mean accuracy for complex items
tempCplxAcc <- aggregate(acc ~ sbj_id, FUN=mean, data=subset(nonwords, complexity==1))

# now look only at simple items
# find mean accuracy for noncomplex items
tempSimpAcc <- aggregate(acc ~ sbj_id, FUN=mean, data=subset(nonwords, complexity==0))

# find difference between complex and simple items - that is Morpheme Interference Effect Index
names(tempSimpAcc)[2]  <- "accSimple"
names(tempCplxAcc)[2] <- "accComplex"
mifDfAcc <- merge(tempCplxAcc, tempSimpAcc)

mifDfAcc$mifAcc<-mifDfAcc$accComplex - mifDfAcc$accSimple
mifDfAcc$mifScaledAcc<-scale(mifDfAcc$accComplex - mifDfAcc$accSimple)
summary(mifDfAcc)

# histogram of distribution of MIE based on accuracy
ggplot(data=mifDfAcc, aes(x=mifAcc)) +
  geom_histogram(binwidth=0.1) +
  theme(legend.position = "none")


# based on REACTION TIMES

# find mean RTs for complex items
tempCplxRt <- aggregate(rt ~ sbj_id, FUN=mean, data=subset(nonwordsRT, complexity==1))

# find mean RTs for noncomplex items
tempSimpRt <- aggregate(rt ~ sbj_id, FUN=mean, data=subset(nonwordsRT, complexity==0))

# find difference between complex and simple items - that is Morpheme Interference Effect Index
names(tempSimpRt)[2]  <- "rtSimple"
names(tempCplxRt)[2] <- "rtComplex"
mifDfRt <- merge(tempCplxRt, tempSimpRt)

mifDfRt$mifRt<-mifDfRt$rtComplex - mifDfRt$rtSimple
mifDfRt$mifScaledRt<-scale(mifDfRt$rtComplex - mifDfRt$rtSimple)
summary(mifDfRt)

# histogram of distribution of MIE based on RTs
ggplot(data=mifDfRt, aes(x=mifRt)) +
  geom_histogram(binwidth=0.1) +
  theme(legend.position = "none")

# check correlation of the MIE indices based on RTs and on accuracy
cor(mifDfAcc$mifAcc,mifDfRt$mifRt)


# FINAL INDEX: zscore accuracy + zscore reading times

# add up standardized MIE scores from accuracy and RTs
final_index <- mifDfAcc$mifScaledAcc + mifDfRt$mifScaledRt

# merge accuracy and RTs data frames and add final_index column
final_df <- cbind(mifDfAcc,mifDfRt)
final_df$final_MIE <- final_index

summary(final_df)

# write out the df with sbj_id and mif
# write.csv((final_df %>% dplyr::select(c("sbj_id", "final_MIE"))), "mif_11-10-2023.csv", row.names = T)


# histogram of the final index distribution
plot_data <- data.frame(cbind(final_df$sbj_id,final_df$final_MIE))

ggplot(plot_data,aes(x=X2)) +
  geom_histogram(binwidth = 0.5) +
  # scale_x_discrete(limits=c(-3,-2,-1,0,1,2)) +
  labs(x="\nIndex of Morpheme Interference", y="count\n", title = "Morpheme Interference Effect index distribution\n")

#### 4-modelling ####

# set treatment contrasts
all_data$complexity <-as.factor(all_data$complexity)
contrasts(all_data$complexity) <- contr.treatment(2)

all_data$lexicality <-as.factor(all_data$lexicality)
contrasts(all_data$lexicality) <- contr.treatment(2)

# RTS

# decide on transformation
boxcox((all_data%>%filter(acc==1))$rt ~ 1)

par(mfrow=c(1,4))
hist((all_data%>%filter(acc==1))$rt, 20)
hist((all_data%>%filter(acc==1))$rt[(all_data%>%filter(acc==1))$rt])
hist(log((all_data%>%filter(acc==1))$rt))
hist(1/(all_data%>%filter(acc==1))$rt)
par(mfrow=c(1,1))

mod_rt2 <- lmerTest::lmer(-1000/rt ~ complexity + (1|sbj_id) + (1|trial_id), data=subset(all_data,lexicality==0 & acc==1))
summary(mod_rt2)

# confidence intervals
round(confint.merMod(mod_rt2, method="Wald"), digits=2)

# ACCURACY

mAcc <- glmer(acc ~ complexity + (1|sbj_id) + (1|target) + (0+complexity|sbj_id), family="binomial", data=nonwords)
summary(mAcc)
# simplify until the model converges
mAcc2 <- glmer(acc ~ complexity + (1|sbj_id) + (1|target), family="binomial", data=nonwords)
summary(mAcc2)

# confidence intervals
round(confint.merMod(mAcc2, method="Wald"), digits=2)

