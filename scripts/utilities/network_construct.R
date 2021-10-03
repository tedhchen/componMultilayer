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
  nsize <- length(vs)

  # constructing Matrix
  cat('Constructing network... ')
  mat <- matrix(0, nrow = nsize, ncol = nsize, dimnames = list(vs, vs))

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
  nw%v%'layer.mem' <- c(rep(1, 162), rep(2, (nsize - 162)))
  nw%v%'org.aff' <- c(1:162, colSums(as.matrix(nw)[1:162, 163:nsize] * matrix(rep(1:162, (nsize - 162)), nrow = 162, byrow = F)))
  cat('DONE\n')
  nw
}

make_constraints <- function(nw){
  # Getting base network info as edgelist container
  base_attrs <- attributes(as.edgelist(nw))
  nsize <- network.size(nw)

  # All combinations of ties within layers
  el <- rbind(t(combn(1:162, 2)), t(combn(163:nsize, 2)))
  el <- rbind(el, el[,c(2,1)])

  # Give the free edgelist the proper attributes
  base_attrs$dim[1] <- nrow(el)
  attributes(el) <- base_attrs
  el
}

simple_plot <- function(nw, l1v.cex = 0.5, l2v.cex = 0.3, l1v.col = 'red', l2v.col = 'gray', e.col = 'lightgray', isolates = F, arrows = F, labels = F){
  plot(nw,
       vertex.cex = c(rep(l1v.cex, 162), rep(l2v.cex, (network.size(nw) - 162))),
       vertex.col = c(rep(l1v.col, 162), rep(l2v.col, (network.size(nw) - 162))),
       vertex.border = c(rep('black', 162), rep('darkgray', (network.size(nw) - 162))),
       displayisolates = isolates, usearrows = arrows, displaylabels = labels,
       edge.col = e.col)
}
