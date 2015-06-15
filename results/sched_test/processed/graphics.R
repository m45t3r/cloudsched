#!/usr/bin/R -f

library(ggplot2)

dirpath <- "."
setwd(paste(dirpath, sep=""))

google <- read.table(paste("./googlece_n32_temp.csv",sep=""),sep = ",",header = TRUE)
azure <- read.table(paste("./azure_n32_temp.csv",sep=""),sep = ",",header = TRUE)

ggplot(google, aes(x=Algorithms,y=Time, fill = Operation)) + 
    geom_bar(stat="identity", position = "dodge",data = google) + 
    scale_fill_brewer(palette = "Set1")

ggplot(azure, aes(x=Algorithms,y=Time, fill = Operation)) + 
    geom_bar(stat="identity", position = "dodge",data = azure) + 
    scale_fill_brewer(palette = "Set1")
