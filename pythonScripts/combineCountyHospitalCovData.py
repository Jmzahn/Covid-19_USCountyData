#Jacob Zahn

import sys
import time

import numpy as np
import pandas as pd
import datetime

sys.path.append('..')
import lib

#load new dataset 
CountyHospital = lib.loadCHCombined()
#load NYTimes data
CountyCovData = lib.loadUSCountiesCov()

#grab dates and turn them into numpy variable
DAYBEFORE = '2020-01-20'
DAYBEFORE = np.datetime64(DAYBEFORE)
dates = CountyCovData['date']
dates = np.array(dates, dtype=np.datetime64)

#make a range of dates so we know current dataset length in days
dateRange = np.arange(DAYBEFORE, dates[-1]+np.timedelta64(1,'D'), dtype=np.datetime64)

#make ndarrays that are shape (county, days since day zero), and contain zeros
cCountyDay = np.zeros((len(CountyHospital),len(dateRange)),dtype=np.intc)
dCountyDay = np.zeros((len(CountyHospital),len(dateRange)),dtype=np.intc)
#zeros allow us to choose that if we dont have info about a county yet, we assume they have zero cases

#POPEST2019,BEDS,HELIPADS,NONPROF,PRIVATE,GOVERNM,LAT,LON
#grab county state from hospital and cov data
counties = CountyHospital['COUNTY'].to_numpy()
states = CountyHospital['STATE'].to_numpy()
populations = CountyHospital['POPEST2019'].to_numpy()
beds = CountyHospital['BEDS'].to_numpy()
helipads = CountyHospital['HELIPADS'].to_numpy()
nonProf = CountyHospital['NONPROF'].to_numpy()
private = CountyHospital['PRIVATE'].to_numpy()
governm = CountyHospital['GOVERNM'].to_numpy()
lat = CountyHospital['LAT'].to_numpy()
lon = CountyHospital['LON'].to_numpy()

countiesHolder=np.array(counties, dtype=str)

for n, county in enumerate(counties):
    if(county.endswith(' County')):
        county = county[:-7]
    if(county.endswith(' Borough')):
        county = county[:-8]
    if(county.endswith(' Municipality')):
        county = county[:-13]
    if(county.endswith(' Census Area')):
        county = county[:-12]
    if(county.endswith(' Parish')):
        county = county[:-7]
    if(county.endswith(' and')):
        county = county[:-4]
    countiesHolder[n] = county

covCounties = CountyCovData['county'].to_numpy()
covStates = CountyCovData['state'].to_numpy()
covCases = CountyCovData['cases'].to_numpy()
covDeaths = CountyCovData['deaths'].to_numpy()

countyIndex = np.arange(len(countiesHolder), dtype=np.intc)
datesIndex = np.arange(len(dateRange), dtype=np.intc)


county=countiesHolder[204]
state=states[204]
#^LA for testing

start = time.time()
for (c, county, state) in zip(countyIndex, countiesHolder, states):
    stateAndCountyMap = (covCounties==county)&(covStates==state)
    Ccases = covCases[stateAndCountyMap]
    Cdeaths = covDeaths[stateAndCountyMap]
    Cdates = dates[stateAndCountyMap]
    for (d, date) in zip(datesIndex, dateRange):
        datesMap = Cdates==date
        CcasesTemp = Ccases[datesMap]
        CdeathsTemp = Cdeaths[datesMap]
        numCases = np.sum(CcasesTemp) if CcasesTemp.size != 0 else np.intc(0)
        previousC = cCountyDay[c,d-np.intc(1)] if d != 0 else np.intc(0)
        numDeaths = np.sum(CdeathsTemp) if CdeathsTemp.size != 0 else np.intc(0)
        previousD = dCountyDay[c,d-np.intc(1)] if d != 0 else np.intc(0)
        cCountyDay[c,d] = numCases if numCases >= previousC else previousC
        dCountyDay[c,d] = numDeaths if numDeaths >= previousD else previousD
end = time.time()
ellapsed = end-start
print('big loop took : ',ellapsed,' seconds')


#create DataFrame from python dict containing our county and hospital information
dataDict = {
        'county'        : counties    ,
        'state'         : states      ,
        'population'    : populations ,
        'beds'          : beds        ,
        'helipads'      : helipads    ,
        'nonProf'       : nonProf     ,
        'private'       : private     ,
        'governm'       : governm     ,
        'lat'           : lat         ,
        'lon'           : lon         
}
CH = pd.DataFrame(dataDict, index = countyIndex)

#create and populate column names from dates
cDateRange = np.empty(dateRange.shape,dtype='<U11')
dDateRange = np.empty(dateRange.shape,dtype='<U11')
dateRangeDT = np.array([date.astype(datetime.datetime) for date in dateRange])
dateRangeStr = np.array([date.strftime('%Y-%m-%d') for date in dateRangeDT])


for (d, date) in zip(datesIndex, dateRangeStr):
    cdate = np.unicode_('c')+date
    ddate = np.unicode_('d')+date
    cDateRange[d] = cdate
    dDateRange[d] = ddate

#create DataFrames from cases and deaths
Cs = pd.DataFrame(cCountyDay, index = countyIndex, columns = cDateRange)
Ds = pd.DataFrame(dCountyDay, index = countyIndex, columns = dDateRange)

df = pd.concat([CH, Cs, Ds], axis=1)
df.to_csv('../data/Interim_data_views/CovCountyHospitalTimeSeries.csv',index=False)