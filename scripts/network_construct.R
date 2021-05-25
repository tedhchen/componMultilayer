# Load required library
library(network)

# Function to build multilayer network
create_network <- function(years, threshold, directed = T, path = '../data/'){
  cat('Reading in Twitter data... ')
  # tweets and affiliation
  rts <- readRDS(paste(path, 'climate_filtered_retweets_2013_2020.rds', sep = ''))
  rts <- rts[which(rts$year %in% years), c(2, 3, 5, 6)]

  # affiliation
  affel <- unique(rbind(as.matrix(rts[,c(1,2)]), as.matrix(rts[,c(3,4)])))

  # organizational survey
  cat('Reading in survey data... ')
  l1el <- read.csv(paste(path, 'collaboration_2014.txt', sep = ''), as.is = T, sep = ';')
  l1el <- l1el[,c(1,3)]

  # List of actors (FI and FA handcoded for now)
  vs <- c(paste('FI', sprintf("%03d", seq(1, 96)), sep = ''), paste('FA', sprintf("%03d", seq(1, 66)), sep = ''), paste('T', sort(unique(unlist(rts[,c(1,3)]))), sep = ''))

  # constructing Matrix
  cat('Constructing network... ')
  mat <- matrix(0, nrow = length(vs), ncol = length(vs), dimnames = list(vs, vs))

  # Filling in Twitter ties
  for(i in 1:nrow(rts)){
    mat[paste('T', rts[i, 3], sep = ''), paste('T', rts[i, 1], sep = '')] <- mat[paste('T', rts[i, 3], sep = ''), paste('T', rts[i, 1], sep = '')] + 1
  }

  # Threshold
  mat[mat < threshold] <- 0; mat[mat > 0] <- 1

  # Filling in Affiliation ties
  for(i in 1:nrow(affel)){
    mat[affel[i,2], paste('T', affel[i, 1], sep = '')] <- 1
  }

  # Filling in survey ties
  for(i in 1:nrow(l1el)){
    mat[l1el[i,1], l1el[i,2]] <- 1
  }

  nw <- network(mat, directed = directed)
  nw%v%'layer.mem' <- c(rep(1, 162), rep(2, (nrow(mat) - 162)))
  cat('DONE')
  nw
}

simple_plot <- function(nw, l1v.cex = 0.5, l2v.cex = 0.3, l1v.col = 'red', l2v.col = 'gray', isolates = F, arrows = F, labels = F){
  plot(nw,
       vertex.cex = c(rep(l1v.cex, 162), rep(l2v.cex, (network.size(nw) - 162))),
       vertex.col = c(rep(l1v.col, 162), rep(l2v.col, (network.size(nw) - 162))),
       displayisolates = isolates, usearrows = arrows, displaylabels = labels)
}
