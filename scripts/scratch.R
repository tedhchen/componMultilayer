source('network_construct.R')

# Creating network
nw <- create_network(2020, 1)

# Check everything looks right
simple_plot(nw)

library(multilayer.ergm)

nw

m <- ergm(nw
          ~ edges
          + edges
          + edges
          ,
          constraints = ~fixallbut(),
          eval.loglik = F, verbose = F,
          control = control.ergm(seed = 111953,
                                 MCMC.burnin = 5000,
                                 MCMC.samplesize = 1500,
                                 MCMC.interval = 1500,
                                 MCMLE.maxit = 30,
                                 parallel = 0)
          )












