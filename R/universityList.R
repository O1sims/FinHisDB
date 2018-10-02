library(jsonlite)
library(magrittr)


countryCodes <- c("FR", "IT", "ES", "BE", "DE", "GB")
countryNames <- c("France", "Italy", "Spain", "Belgium", "Germany", "United Kingdom")

university.names <- getwd() %>%
  paste0("/data/universities.json") %>%
  jsonlite::fromJSON() %>%
  subset(alpha_two_code %in% countryCodes)


timesHigherRank <- "https://www.timeshighereducation.com/sites/default/files/the_data_rankings/world_university_rankings_2019_limit0_7216a250f6ae72c71cd09563798a9f18.json"

full.universities.rank <- timesHigherRank %>% 
  jsonlite::fromJSON()

universities.rank <- full.universities.rank$data %>%
  subset(location %in% countryNames)

a <- subset(universities.rank$name, )



gdpProjection <- c()
for (i in 1:26) {
  gdpProjection %<>% 
    append(41.6 * (1 + 0.03)^i)
}

calculateLostGDP <- function(finalRate, years) {
  lostGDP <- c()
  sacrificeRatio <- finalRate/years
  for (i in 1:years) {
    delta <- (sacrificeRatio * i)/100
    actualGDP <- gdpProjection[i+1] * (1 + delta)
    lostGDP %<>% 
      append(gdpProjection[i+1] - actualGDP)
  }
  return(lostGDP)
}

for (i in c(-5.33, -9.1)) {
  calculateLostGDP(
    finalRate = i, 
    years = 25)
}

# Calculate the number of jobs that have been removed
# This will include the number of migrants that are currently employed and a proportion of the number that could have 
# otherwise come in to work
# 
# There were initially 79,000 workers with approximately 60,000 employed
# In the Principal projection there is a net migration of 800
# In Scenario 1 there is a net migration of approximately -1800
# In Scenario 2 there is a net migration of approximately -3800

jobsLost1 <- list(
  max = 60000 + (25 * 1800 * 0.5),
  min = 60000 + (25 * 800 * 0.5))
jobsLost2 <- list(
  max = 60000 + (25 * 3800 * 0.5),
  min = 60000 + (25 * 2800 * 0.5))





