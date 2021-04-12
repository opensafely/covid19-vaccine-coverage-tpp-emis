# OpenSAFELY Covid-19 Vaccine Coverage Report of 57.9million people

This repo contains the code and configuration of our pre-print paper [_Trends and clinical characteristics of COVID-19 vaccine recipients: a federated analysis of 57.9 million patients’ primary care records in situ using OpenSAFELY_](https://doi.org/10.1101/2021.01.25.21250356).

You can sign up for the [OpenSAFELY email newsletter here](https://opensafely.org/contact/) for updates about the COVID-19 vaccine reports and other OpenSAFELY projects.

This repo contains:

* If you are interested in how we defined our variables, take a look at the [study definition](https://github.com/opensafely/covid19-vaccine-coverage-tpp-emis/blob/master/analysis/study_definition.py); this is written in python, but non-programmers should be able to understand what is going on there
* All codelists used in defining varibables are available on [OpenCodelists](https://codelists.opensafely.org/). For this we used the national [COVID-19 Vaccination Uptake Reporting Specification developed by PRIMIS.](https://www.nottingham.ac.uk/primis/covid-19/covid-19.aspx)
* We are updating this repo routinely as more data becomes available. The charts and tables that are in our preprint paper are [available here](https://github.com/opensafely/covid19-vaccine-coverage-tpp-emis/tree/2021-03-17/released_outputs/). We have made .csv files available, with the data behind the tables and charts for inspection, further analysis and re-use by anyone as long as OpenSAFELY.org is credited and/or linked to.


## Data

In `released_outputs/combined/`, you'll find:

* `cumulative_coverage/all/[key]/all_[key]_by_wave.csv`: cumulative coverage for whole
  population, stratified by priority group
* `cumulative_coverage/wave_[n]/[key]/wave_[n]_[key]_by_[col].csv`: cumulative coverage
  for one priority group, stratified by demographic or clinical group
* `tables/all_[key].csv`: coverage for whole population at latest date, stratified by
  priority group
* `tables/wave_[n]_[key].csv`: coverage for one priority group at latest date,
  stratified by demographic or clinical group
* `charts/all_[key].png`: chart of cumulative coverage for whole population, stratified
  by priority group
* `charts/wave_[n]_[key].csv`: chart of cumulative coverage for one priority group,
  stratified by demographic or clinical group
* `reports/all_[key].html`: report containing charts and table for whole population
* `reports/wave_[n]_[key].html`: report containing charts and table for one priority
  group

# About the OpenSAFELY framework

The OpenSAFELY framework is a secure analytics platform for electronic health records
research in the NHS.

Instead of requesting access for slices of patient data and transporting them elsewhere
for analysis, the framework supports developing analytics against dummy data, and then
running against the real data *within the same infrastructure that the data is stored*.
Read more at [OpenSAFELY.org](https://opensafely.org).
