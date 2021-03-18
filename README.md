# Covid-19 vaccine coverage reporting with PRIMIS specification

This repo contains:

* code to generate reports on covid-19 vaccine coverage using variables defined in the
  _SARS-CoV2 (COVID-19) Vaccine Uptake Reporting Specification Collection 2020/2021_
  document from PRIMIS
* aggregated data showing cumulative coverage, broken down by demographic and clinical
  groups, from TPP and EMIS, covering 95% of the population of England

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

Data covers 2020-12-08 to 2021-03-07.

# About the OpenSAFELY framework

The OpenSAFELY framework is a secure analytics platform for electronic health records
research in the NHS.

Instead of requesting access for slices of patient data and transporting them elsewhere
for analysis, the framework supports developing analytics against dummy data, and then
running against the real data *within the same infrastructure that the data is stored*.
Read more at [OpenSAFELY.org](https://opensafely.org).
