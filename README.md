# Covid-19_USCountyData
Collection of datasets related to Covid-19, and a combined time series dataset created by myself for a data science school project.


## Data

### Hospitals.csv
Available here: https://hifld-geoplatform.opendata.arcgis.com/datasets/hospitals

Information on hospitals in the United States.

### us-counties.csv
Available here: https://github.com/nytimes/covid-19-data

Daily covid cases and death data for us counties.

### co-est2019-alldata.csv
Available here: https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/

Data sheet available here: https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2019/co-est2019-alldata.pdf

2019 county level census estimates.

### daily.csv
Available here: https://covidtracking.com/api/v1/states/daily.csv

Daily state level covid testing data.

### CountyHospitalCombined.csv, CovCountyHospitalTimeSeries.csv, and StateTestingTimeSeries.csv
Intereim data views created by me to hold cleaned data and used to create the final datset.

### MasterTimeSeries.csv
Final combined dataset, a days X 3142(num of us counties+dc) long time series with variables stored as a proportion of population.


## Code
The python scripts have comments to explain which datasets they're responsible for generating.

Feel free to use and edit them to tailor the datasets generated to your liking.

There is also a helper function library in the main directory.

Scripts can be ran by calling >python \<scriptname\>.py in the directory they reside in.
