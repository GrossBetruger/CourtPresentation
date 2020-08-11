
library(gdata)
library(Rmisc)

data = read.csv("user_means_lan_100.csv")

CI(as.numeric(unlist(data["user_mean"])), 0.999)
