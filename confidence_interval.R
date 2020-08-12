library(gdata)
library(Rmisc)

#options(warn=-1)

user_means <- read.csv("user_means_lan_100.csv")

print("User Means Confidence Interval (99%):")
print(CI(as.numeric(unlist(user_means["user_mean"])), 0.99))


tryCatch({
test_ground_truth_results <- read.csv("ground_truth_rate_double_lan_100_raw.csv")
test_ground_truth_results_israel <- read.csv("ground_truth_rate_100_lan_israel_cache.csv")
print("Ground Truth Tests Confidence Interval (95%):")
print(CI(as.numeric(unlist(test_ground_truth_results["ground_truth_rate"])), 0.95))
print("Ground Truth Tests Confidence Interval - Israeli Cache (95%):")
print(CI(as.numeric(unlist(test_ground_truth_results_israel["ground_truth_rate"])), 0.95))
})

