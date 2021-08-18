# set directory and list files
setwd()
files <- list.files()

# for each file (i.e. organization) count number of rows
nacc <- numeric(length(files))
for(i in 1:length(files)){
  nacc[i] <- tryCatch(nrow(read.csv(files[i], header = F)), error = function(e)return(0))
}

# set everyone above 500 to 500
nacc[nacc>499]<-500

# plot
hist(nacc, main = 'Number of accounts to check per organization', xlab = '(Above 500 set to 500)', breaks = 10)
