#This script combines and transposes CovCountyHospitalTimeSeries.csv, and StateTestingTimeSeries.csv
# into MasterTimeSeries.csv a days X 3142(num of us counties+dc) long time series with variables stored as a proportion of population


#Jacob Zahn

import sys
import time

import numpy as np
import pandas as pd
import datetime

sys.path.append('..')
import lib

#load data
CCHTS = lib.loadCCHTimeSeries()
STTS = lib.loadSTTS()


#get date data
CCHTS_startDate = np.datetime64(((CCHTS.columns).to_numpy()[10])[-10:])
CCHTS_endDate = np.datetime64(((CCHTS.columns).to_numpy()[-1])[-10:])
#create range from start and end date
dateRange = np.arange(CCHTS_startDate, CCHTS_endDate+np.timedelta64(1,'D'), dtype='datetime64[D]')
numDays = len(dateRange)


#get county level data
counties    = CCHTS['county'].to_numpy()
county_states      = CCHTS['state'].to_numpy()
county_populations = CCHTS['population'].to_numpy()
beds        = CCHTS['beds'].to_numpy()
helipads    = CCHTS['helipads'].to_numpy()
nonProf     = CCHTS['nonProf'].to_numpy()
private     = CCHTS['private'].to_numpy()
governm     = CCHTS['governm'].to_numpy()
lat         = CCHTS['lat'].to_numpy()
lon         = CCHTS['lon'].to_numpy()

#grab cases/deaths as a matrix of shape (counties+dc, days in dataset)
casesMatrix = CCHTS.iloc[:,10:10+numDays].to_numpy()
deathsMatrix = CCHTS.iloc[:,10+numDays:10+numDays+numDays].to_numpy()

#calulate variables as a proportion of population
bedsPerPop          = beds/county_populations
helipadsPerPop      = helipads/county_populations
nonProfPerPop       = nonProf/county_populations
privatePerPop       = private/county_populations
governmPerPop       = governm/county_populations
casesPerPopMatrix   = np.zeros(casesMatrix.shape,dtype=np.float64)
deathsPerPopMatrix  = np.zeros(deathsMatrix.shape,dtype=np.float64)
np.divide(casesMatrix, county_populations.reshape((len(county_populations),1)), out=casesPerPopMatrix)
np.divide(deathsMatrix, county_populations.reshape((len(county_populations),1)), out=deathsPerPopMatrix)


#get state level data
states = STTS['state'].to_numpy()
state_pop = STTS['population'].to_numpy()

#grab cases/deaths as a matrix of shape (states+dc, days in dataset)
testMatrix = STTS.iloc[:,2:2+numDays].to_numpy()
tPosMatrix = STTS.iloc[:,2+numDays:2+numDays+numDays].to_numpy()
tNegMatrix = STTS.iloc[:,2+numDays+numDays:2+numDays+numDays+numDays].to_numpy()

#calulate variables as a proportion of population
testPerPopMatrix = np.zeros(testMatrix.shape,dtype=np.float64)
tPosPerPopMatrix = np.zeros(tPosMatrix.shape,dtype=np.float64)
tNegPerPopMatrix = np.zeros(tNegMatrix.shape,dtype=np.float64)
np.divide(testMatrix, state_pop.reshape((len(state_pop), 1)), out=testPerPopMatrix)
np.divide(tPosMatrix, state_pop.reshape((len(state_pop), 1)), out=tPosPerPopMatrix)
np.divide(tNegMatrix, state_pop.reshape((len(state_pop), 1)), out=tNegPerPopMatrix)


#get testing variables as shape(counties+dc, days in dataset)
cTestPerPop = np.zeros(casesMatrix.shape, dtype=np.float64)
cTPosPerPop = np.zeros(casesMatrix.shape, dtype=np.float64)
cTNegPerPop = np.zeros(casesMatrix.shape, dtype=np.float64)

countyIndex = np.arange(len(counties), dtype=np.intc)
statesIndex = np.arange(len(states), dtype=np.intc)

start = np.intc(0)
for (s, state, test, pos, neg) in zip(statesIndex, states, testPerPopMatrix, tPosPerPopMatrix, tNegPerPopMatrix):
    stateMask = county_states==state
    numC = cTestPerPop[stateMask].shape[0]
    for c in np.arange(start, start+numC):
        cTestPerPop[c] = test
        cTPosPerPop[c] = pos
        cTNegPerPop[c] = neg
    start+=numC


#now that we have shapes (county+dc, days), we need to transpose and expand to (days*(counties+dc), num variables)
datesCol = np.empty((numDays,len(counties)), dtype='<U10')
dateRangeDT = np.array([date.astype(datetime.datetime) for date in dateRange])
dateRangeStr = np.array([date.strftime('%Y-%m-%d') for date in dateRangeDT])
datesIndex = np.arange(len(dateRange), dtype=np.intc)

for (d, date) in zip(datesIndex, dateRangeStr):
    datesCol[d] = np.repeat(date, len(counties))

#flatten our multivariate time series data
datesColPerDay = datesCol.flatten()
cTestPerPopPerDay = cTestPerPop.T.flatten()
cTPosPerPopPerDay = cTPosPerPop.T.flatten()
cTNegPerPopPerDay = cTNegPerPop.T.flatten()
casesPerPopPerDay = casesPerPopMatrix.T.flatten()
deathsPerPopPerDay = deathsPerPopMatrix.T.flatten()
#repeat our constants
countiesPerDay = np.tile(counties, numDays)
statesPerDay = np.tile(county_states, numDays)
bedsPerPopPerDay = np.tile(bedsPerPop, numDays)
helipadsPerPopPerDay = np.tile(helipadsPerPop, numDays)
nonProfPerPopPerDay = np.tile(nonProfPerPop, numDays)
privatePerPopPerDay = np.tile(privatePerPop, numDays)
governmPerPopPerDay = np.tile(governmPerPop, numDays)

#save file
dataDict = {
    'date' : datesColPerDay,
    'county' : countiesPerDay,
    'state' : statesPerDay,
    'beds' : bedsPerPopPerDay,
    'helipads' : helipadsPerPopPerDay,
    'nonProf' : nonProfPerPopPerDay,
    'private' : privatePerPopPerDay,
    'governm' : governmPerPopPerDay,
    'tests' : cTestPerPopPerDay,
    'positive' : cTPosPerPopPerDay,
    'negative' : cTNegPerPopPerDay,
    'cases' : casesPerPopPerDay,
    'deaths' : deathsPerPopPerDay,
}
df = pd.DataFrame(dataDict)
df.to_csv('../data/Final_data_view/MasterTimeSeries.csv', index = False)#you can remove .gz to get an uncrompress csv