library(gdata)
library(Rmisc)

#options(warn=-1)

sample <- c(68.61779123977205,
              24.32896911424133,
              76.92231966099243,
              26.29507258584366,
              18.796275829665444,
              38.773925161027975,
              67.44159181726717,
              62.07725767257152,
              14.501151138015311,
              28.858883412489455,
              30.329102577441848,
              19.72540138544492,
              40.64619537747528,
              37.38703159564258,
              10.77011588187048,
              54.870156998236396,
              80.83564628348462,
              77.88440363344672,
              83.4140247331403,
              57.22799821759984)
print("sample CI:")
print(CI(as.numeric(sample), 0.99))

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

