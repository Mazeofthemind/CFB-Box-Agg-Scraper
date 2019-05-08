# CFB-Box-Agg-Scraper

## Introduction

Python3 scraper that:

- Takes input parameters for the years and conferences/teams of interest
- Enumerates the CFB games specified by those parameters
- Extracts the offensive box scores for those enumerated games
- Aggregates them into basic annual player statistics

This scraper can be expanded upon in the future to expand the box score data harvested (ex. defensive statistics) or produce alternative aggregates on demand (ex. )

## Blocking Notes

Many stat websites have protections in place to prevent excessive scraping based on patterns and rates of access from individual IPs. As such, it is recommended to use conservative timing settings (sleep time between access operations) and non-personal IPs (ex. Amazon AWS Public IPs).

pip3 install -r requirements.txt 
