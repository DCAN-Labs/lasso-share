#!/usr/bin/env Rscript
args = commandArgs(trailingOnly=TRUE)
# if (!require(rprime)) install.packages('rprime',lib='~/R')
# if (!require(dplyr)) install.packages('dplyr',lib='~/R')
# if (!require(tidyr)) install.packages('tidyr',lib='~/R')

library(rprime,lib.loc="/home/naxos2-raid14/donovan/R/x86_64-redhat-linux-gnu-library/3.6")
library(dplyr,lib.loc="/home/naxos2-raid14/donovan/R/x86_64-redhat-linux-gnu-library/3.6")
library(tidyr,lib.loc="/home/naxos2-raid14/donovan/R/x86_64-redhat-linux-gnu-library/3.6")

#library(rprime,lib.loc="/home/range2-raid1/zeynepb/R/x86_64-redhat-linux-gnu-library/3.6")
#library(dplyr,lib.loc="/home/range2-raid1/zeynepb/R/x86_64-redhat-linux-gnu-library/3.6")
#library(tidyr,lib.loc="/home/range2-raid1/zeynepb/R/x86_64-redhat-linux-gnu-library/3.6")

# FIND EPRIME FILES

files <- list.files(path=getwd(), pattern="*.txt", full.names=TRUE, recursive=FALSE)

# READ QA TABLES

qa.tp1 <- subset(read.csv('275_BRIDGES_RUN_QA_2059.csv'),select=c('grid','scan_id','scan_type'))
qa.tp2 <- subset(read.csv('275_BRIDGES_RUN_QA_2065.csv'),select=c('grid','scan_id','scan_type'))
qa.tp3 <- subset(read.csv('275_BRIDGES_RUN_QA_2071.csv'),select=c('grid','scan_id','scan_type'))

home <- getwd()

# BEGIN LOOP THROUGH EPRIME FILES

lapply(files, function(file) {
tryCatch({
out <- tools::file_path_sans_ext(file)
splitname <- strsplit(basename(out),"-")[[1]]
sub <- nth(splitname,-2L)
run <- nth(splitname,-1L)

# GET EVENT ID FROM QA TABLE

if(run=="1"){ses.df<-subset(qa.tp1, grid == sub, select=c(scan_id))}
else if(run=="2"){ses.df<-subset(qa.tp2, grid == sub, select=c(scan_id))}
else if(run=="3"){ses.df<-subset(qa.tp3, grid == sub, select=c(scan_id))}
ses <- ses.df$scan_id[1]
print(paste(sub,ses,sep="-"))

# READ EPRIME FILE

edatfile <- read_eprime(file)
edatframes <- FrameList(edatfile)
frames <- keep_levels(edatframes,c(2,3,4))
df <- to_data_frame(frames)
pruned<-subset(df,select=c("Eprime.LevelName",
                             "Eprime.FrameNumber",
                             "Procedure",
                             "Running",
                             "BlockType",
                             "RunTitle",
                             "PrepStim.OnsetDelay",
                             "PrepStim.OnsetTime",
                             "PrepIAPS.DurationError",
                             "PrepIAPS.OnsetTime",
                             "Stimulus.DurationError", 
                             "Stimulus.OnsetTime",
                             "RestStim.OnsetTime"))

pruned %>% fill(BlockType,.direction = "up") -> pruned
pruned %>% fill(RunTitle,.direction = "up") -> pruned
pruned$onset.all <- coalesce(pruned$PrepStim.OnsetTime,
                             pruned$PrepIAPS.OnsetTime,
                             pruned$RestStim.OnsetTime)
pruned$onset.final <- ifelse(!is.na(pruned$PrepStim.OnsetDelay),
                             as.numeric(pruned$onset.all) - as.numeric(pruned$PrepStim.OnsetDelay),
                             as.numeric(pruned$onset.all))
pruned$order <- ifelse(pruned$Procedure=="TrialProc",
                       ifelse(pruned$Running=="BlockList",
                              pruned$BlockType,
                              pruned$Running),
                       pruned$Running)

isrun1 <- na.omit(subset(pruned,RunTitle=="Run1",select=c("order","onset.final")))
isrun2 <- na.omit(subset(pruned,RunTitle=="Run2",select=c("order","onset.final")))

## RUN 1 FUNCITON

dorun1 <- function() {

run1 <- na.omit(subset(pruned,RunTitle=="Run1",select=c("order","onset.final")))
run1$onset.zero.sec <- (run1$onset.final - run1$onset.final[1]) / 1000
run1$duration.sec <- append(diff(run1$onset.final)/1000,NA)

# omg i can't believe i'm gonna do it this way...

## RUN 1 TEMPLATE
template.run1 <- data.frame(matrix(0, ncol = 3, nrow = 14))
#Get Block Names
template.run1[1,1] <- run1$order[1]
template.run1[2,1] <- run1$order[2]
template.run1[3,1] <- run1$order[17]
template.run1[4,1] <- run1$order[32]
template.run1[5,1] <- run1$order[47]
template.run1[6,1] <- run1$order[62]
template.run1[7,1] <- run1$order[77]
template.run1[8,1] <- run1$order[92]
template.run1[9,1] <- run1$order[107]
template.run1[10,1] <- run1$order[122]
template.run1[11,1] <- run1$order[137]
template.run1[12,1] <- run1$order[152]
template.run1[13,1] <- run1$order[167]
template.run1[14,1] <- run1$order[182]
#Get Onset Times
template.run1[1,2] <- run1$onset.zero.sec[1]
template.run1[2,2] <- run1$onset.zero.sec[2]
template.run1[3,2] <- run1$onset.zero.sec[17]
template.run1[4,2] <- run1$onset.zero.sec[32]
template.run1[5,2] <- run1$onset.zero.sec[47]
template.run1[6,2] <- run1$onset.zero.sec[62]
template.run1[7,2] <- run1$onset.zero.sec[77]
template.run1[8,2] <- run1$onset.zero.sec[92]
template.run1[9,2] <- run1$onset.zero.sec[107]
template.run1[10,2] <- run1$onset.zero.sec[122]
template.run1[11,2] <- run1$onset.zero.sec[137]
template.run1[12,2] <- run1$onset.zero.sec[152]
template.run1[13,2] <- run1$onset.zero.sec[167]
template.run1[14,2] <- run1$onset.zero.sec[182]
#Get Durations
template.run1[1,3] <- sum(run1$duration.sec[1])
template.run1[2,3] <- sum(run1$duration.sec[2:16])
template.run1[3,3] <- sum(run1$duration.sec[17:31])
template.run1[4,3] <- sum(run1$duration.sec[32:46])
template.run1[5,3] <- sum(run1$duration.sec[47:61])
template.run1[6,3] <- sum(run1$duration.sec[62:76])
template.run1[7,3] <- sum(run1$duration.sec[77:91])
template.run1[8,3] <- sum(run1$duration.sec[92:106])
template.run1[9,3] <- sum(run1$duration.sec[107:121])
template.run1[10,3] <- sum(run1$duration.sec[122:136])
template.run1[11,3] <- sum(run1$duration.sec[137:151])
template.run1[12,3] <- sum(run1$duration.sec[152:166])
template.run1[13,3] <- sum(run1$duration.sec[167:181])
template.run1[14,3] <- round(285 - run1$onset.zero.sec[182], digits=3)


# FSL TABLES RUN1

Prep_1 <- subset(template.run1,select=c("X2","X3"))
Prep_1$X4 <- ifelse(template.run1$X1=="RunList",1,0)

AllGo_1 <- subset(template.run1,select=c("X2","X3"))
AllGo_1$X4 <- ifelse(template.run1$X1=="AllGoBlockList",1,0)

Neutral_1 <- subset(template.run1,select=c("X2","X3"))
Neutral_1$X4 <- ifelse(template.run1$X1=="Neutral",1,0)

Positive_1 <- subset(template.run1,select=c("X2","X3"))
Positive_1$X4 <- ifelse(template.run1$X1=="Positive",1,0)

Negative_1 <- subset(template.run1,select=c("X2","X3"))
Negative_1$X4 <- ifelse(template.run1$X1=="Negative",1,0)

Scrambled_1 <- subset(template.run1,select=c("X2","X3"))
Scrambled_1$X4 <- ifelse(template.run1$X1=="Scrambled",1,0)

# CREATE TIMING_FILES DIR AND SUBDIRECTORIES

setwd(home)
dir.create("timing_files",showWarnings=FALSE)
setwd("timing_files")
dir.create("task-GNG1_run-02_bold",showWarnings=FALSE)
subname<-paste("sub",sub,sep="-")
sesname<-paste("ses",ses,sep="-")

# WRITE GNG1 TABLES

setwd("task-GNG1_run-02_bold")
dirname<-paste(subname,sesname,sep="_")
dir.create(dirname)
setwd(dirname)

write.table(Prep_1, "Prep_1", append = FALSE, sep = "\t", dec = ".",
            row.names = FALSE, col.names = FALSE)

write.table(AllGo_1, "AllGo_1", append = FALSE, sep = "\t", dec = ".",
            row.names = FALSE, col.names = FALSE)

write.table(Neutral_1, "Neutral_1", append = FALSE, sep = "\t", dec = ".",
            row.names = FALSE, col.names = FALSE)

write.table(Positive_1, "Positive_1", append = FALSE, sep = "\t", dec = ".",
            row.names = FALSE, col.names = FALSE)

write.table(Negative_1, "Negative_1", append = FALSE, sep = "\t", dec = ".",
            row.names = FALSE, col.names = FALSE)

write.table(Scrambled_1, "Scrambled_1", append = FALSE, sep = "\t", dec = ".",
            row.names = FALSE, col.names = FALSE)

setwd(home) 
print("Done")

}


## START RUN2

dorun2 <- function() {

run2 <- na.omit(subset(pruned,RunTitle=="Run2",select=c("order","onset.final")))
run2$onset.zero.sec <- (run2$onset.final - run2$onset.final[1]) / 1000
run2$duration.sec <- append(diff(run2$onset.final)/1000,NA)

## RUN 2 TEMPLATE
template.run2 <- data.frame(matrix(0, ncol = 3, nrow = 14))

#Get Block Names
template.run2[1,1] <- run2$order[1]
template.run2[2,1] <- run2$order[2]
template.run2[3,1] <- run2$order[17]
template.run2[4,1] <- run2$order[32]
template.run2[5,1] <- run2$order[47]
template.run2[6,1] <- run2$order[62]
template.run2[7,1] <- run2$order[77]
template.run2[8,1] <- run2$order[92]
template.run2[9,1] <- run2$order[107]
template.run2[10,1] <- run2$order[122]
template.run2[11,1] <- run2$order[137]
template.run2[12,1] <- run2$order[152]
template.run2[13,1] <- run2$order[167]
template.run2[14,1] <- run2$order[182]
#Get Onset Times
template.run2[1,2] <- run2$onset.zero.sec[1]
template.run2[2,2] <- run2$onset.zero.sec[2]
template.run2[3,2] <- run2$onset.zero.sec[17]
template.run2[4,2] <- run2$onset.zero.sec[32]
template.run2[5,2] <- run2$onset.zero.sec[47]
template.run2[6,2] <- run2$onset.zero.sec[62]
template.run2[7,2] <- run2$onset.zero.sec[77]
template.run2[8,2] <- run2$onset.zero.sec[92]
template.run2[9,2] <- run2$onset.zero.sec[107]
template.run2[10,2] <- run2$onset.zero.sec[122]
template.run2[11,2] <- run2$onset.zero.sec[137]
template.run2[12,2] <- run2$onset.zero.sec[152]
template.run2[13,2] <- run2$onset.zero.sec[167]
template.run2[14,2] <- run2$onset.zero.sec[182]
#Get Durations
template.run2[1,3] <- sum(run2$duration.sec[1])
template.run2[2,3] <- sum(run2$duration.sec[2:16])
template.run2[3,3] <- sum(run2$duration.sec[17:31])
template.run2[4,3] <- sum(run2$duration.sec[32:46])
template.run2[5,3] <- sum(run2$duration.sec[47:61])
template.run2[6,3] <- sum(run2$duration.sec[62:76])
template.run2[7,3] <- sum(run2$duration.sec[77:91])
template.run2[8,3] <- sum(run2$duration.sec[92:106])
template.run2[9,3] <- sum(run2$duration.sec[107:121])
template.run2[10,3] <- sum(run2$duration.sec[122:136])
template.run2[11,3] <- sum(run2$duration.sec[137:151])
template.run2[12,3] <- sum(run2$duration.sec[152:166])
template.run2[13,3] <- sum(run2$duration.sec[167:181])
template.run2[14,3] <- round(285 - run2$onset.zero.sec[182], digits=3)


# FSL TABLES RUN2

Prep_2 <- subset(template.run2,select=c("X2","X3"))
Prep_2$X4 <- ifelse(template.run2$X1=="RunList",1,0)

AllGo_2 <- subset(template.run2,select=c("X2","X3"))
AllGo_2$X4 <- ifelse(template.run2$X1=="AllGoBlockList",1,0)

Neutral_2 <- subset(template.run2,select=c("X2","X3"))
Neutral_2$X4 <- ifelse(template.run2$X1=="Neutral",1,0)

Positive_2 <- subset(template.run2,select=c("X2","X3"))
Positive_2$X4 <- ifelse(template.run2$X1=="Positive",1,0)

Negative_2 <- subset(template.run2,select=c("X2","X3"))
Negative_2$X4 <- ifelse(template.run2$X1=="Negative",1,0)

Scrambled_2 <- subset(template.run2,select=c("X2","X3"))
Scrambled_2$X4 <- ifelse(template.run2$X1=="Scrambled",1,0)


# CREATE TIMING_FILES DIR AND SUBDIRECTORIES

dir.create("timing_files",showWarnings=FALSE)
setwd("timing_files")
dir.create("task-GNG2_run-03_bold",showWarnings=FALSE)
subname<-paste("sub",sub,sep="-")
sesname<-paste("ses",ses,sep="-")


# WRITE GNG2 TABLES

setwd(home)
setwd('timing_files')
setwd("task-GNG2_run-03_bold")
dirname<-paste(subname,sesname,sep="_")
dir.create(dirname)
setwd(dirname)

write.table(Prep_2, "Prep_2", append = FALSE, sep = "\t", dec = ".",
            row.names = FALSE, col.names = FALSE)

write.table(AllGo_2, "AllGo_2", append = FALSE, sep = "\t", dec = ".",
            row.names = FALSE, col.names = FALSE)

write.table(Neutral_2, "Neutral_2", append = FALSE, sep = "\t", dec = ".",
            row.names = FALSE, col.names = FALSE)

write.table(Positive_2, "Positive_2", append = FALSE, sep = "\t", dec = ".",
            row.names = FALSE, col.names = FALSE)

write.table(Negative_2, "Negative_2", append = FALSE, sep = "\t", dec = ".",
            row.names = FALSE, col.names = FALSE)

write.table(Scrambled_2, "Scrambled_2", append = FALSE, sep = "\t", dec = ".",
            row.names = FALSE, col.names = FALSE)

setwd(home)

print("Done")

}


if(nrow(isrun1) == 0){
    print("RUN1 DATA MISSING... skipping")}else{
        print("RUN1 DATA FOUND... attempting conversion")
        dorun1()
        }

if(nrow(isrun2) == 0){
    print("RUN2 DATA MISSING...skipping")}else{
        print("RUN2 DATA FOUND....attempting conversion")
        dorun2()
        }

}, error=function(e){cat("ERROR :",conditionMessage(e), "\n");setwd(home)})
})

