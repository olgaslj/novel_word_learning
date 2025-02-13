############################
# Code by Davide Crepaldi  #
# February 2012            #
# davide.crepaldi@sissa.it #
############################

# adapted for MIT_all data set
# Olga
# 27-12-20

diagnostics.f <- function (rt, acc, sbj.id, target, lexicality, filename)

{
aggregate(rt[acc==1 & lexicality==1], list(sbj.id[acc==1 & lexicality==1]),mean) -> temp1;     
names(temp1) <- c("sbj.id", "rt.1");
aggregate(rt[acc==1 & lexicality==0], list(sbj.id[acc==1 & lexicality==0]), mean) -> temp2;     
names(temp2) <- c("sbj.id", "rt.0");
aggregate(acc[lexicality==1], list(sbj.id[lexicality==1]), mean) -> temp3;      
names(temp3) <- c("sbj.id", "acc.1");
aggregate(acc[lexicality==0], list(sbj.id[lexicality==0]), mean) -> temp4;
names(temp4) <- c("sbj.id", "acc.0");
sbj.diagnostics <- merge(temp1,temp2);
sbj.diagnostics <- merge(sbj.diagnostics,temp3);
sbj.diagnostics <- merge(sbj.diagnostics,temp4);
sbj.diagnostics <- sbj.diagnostics;

# to get fillers graph, lexicality == 1, for targets lexicality == 0

aggregate(rt[acc==1 & lexicality==0], list(target[acc==1 & lexicality==0]), mean) -> temp1;
names(temp1) <- c("target","rt");
aggregate(acc[lexicality==0], list(target[lexicality==0]), mean) -> temp2;
names(temp2) <- c("target","acc");
target.diagnostics <- merge(temp1, temp2);

jpeg(paste(as.character(filename),".jpg",sep=""), res=200, height=1654, width=2339);
layout(matrix(c(1,2,3,3), nrow=2, byrow=T), heights=c(2,1));	 

ymin <- min(min(sbj.diagnostics$acc.1),min(sbj.diagnostics$acc.0));
ymax <- max(max(sbj.diagnostics$acc.1),max(sbj.diagnostics$acc.0));
xmin <- min(min(sbj.diagnostics$rt.1),min(sbj.diagnostics$rt.0));
xmax <- max(max(sbj.diagnostics$rt.1),max(sbj.diagnostics$rt.0));

sd1 <- vector(mode="numeric", length=nrow(sbj.diagnostics));
for (i in 1:nrow(sbj.diagnostics)) sd1[i] <- sd(rt[sbj.id==sbj.diagnostics$sbj.id[i] & acc==1 & lexicality==1])/sqrt(length(rt[sbj.id==sbj.diagnostics$sbj.id[i] & acc==1 & lexicality==1]));

sd0 <- vector(mode="numeric", length=nrow(sbj.diagnostics));
for (i in 1:nrow(sbj.diagnostics)) sd0[i] <- sd(rt[sbj.id==sbj.diagnostics$sbj.id[i] & acc==1 & lexicality==0])/sqrt(length(rt[sbj.id==sbj.diagnostics$sbj.id[i] & acc==1 & lexicality==0]));

sbj.diagnostics$sd.1 <- sd1;
sbj.diagnostics$sd.0 <- sd0;

plot(sbj.diagnostics$rt.1, sbj.diagnostics$acc.1, xlab="RT (ms)", ylab="% correct", main="Subjects", type="n", ylim=c(ymin,ymax), xlim=c(xmin,xmax));

symbols(sbj.diagnostics$rt.1, sbj.diagnostics$acc.1, fg="red", add=T, inches=F, circles=sd1);
symbols(sbj.diagnostics$rt.0, sbj.diagnostics$acc.0, fg="blue", add=T, inches=F, circles=sd0);
text(sbj.diagnostics$rt.1, sbj.diagnostics$acc.1, as.character(sbj.diagnostics$sbj.id), col="red");
text(sbj.diagnostics$rt.0, sbj.diagnostics$acc.0, as.character(sbj.diagnostics$sbj.id), col="blue");
for (i in 1:nrow(sbj.diagnostics)) lines(c(sbj.diagnostics$rt.1[i], sbj.diagnostics$rt.0[i]), c(sbj.diagnostics$acc.1[i], sbj.diagnostics$acc.0[i]), col=grey(.70));

abline(v=mean(sbj.diagnostics$rt.1)+(2*sd(sbj.diagnostics$rt.1)), col="red", lty=2, lwd=2);
abline(v=mean(sbj.diagnostics$rt.0)+(2*sd(sbj.diagnostics$rt.0)), col="blue", lty=2, lwd=2);
abline(h=mean(sbj.diagnostics$acc.1)-(2*sd(sbj.diagnostics$acc.1)), col="red", lty=2, lwd=2);
abline(h=mean(sbj.diagnostics$acc.0)-(2*sd(sbj.diagnostics$acc.0)), col="blue", lty=2, lwd=2);

plot(target.diagnostics$rt, target.diagnostics$acc, pch=19, xlab="RT (ms)", ylab="% correct", main="Targets", type="n");
text(target.diagnostics$rt, target.diagnostics$acc, as.character(target.diagnostics$target));

#hist(rt[acc==1 & lexicality=="word"], xlab="RT (ms)", ylab="Density", main="Individual datapoints", breaks=(max(rt[acc==1 & lexicality=="word"])-min(rt[acc==1 & lexicality=="word"]))/50);
hist(rt[acc==1 & lexicality==1], xlab="RT (ms)", ylab="Density", main="Individual datapoints", breaks=50);

dev.off();

par(mfrow=c(1,1));

};
