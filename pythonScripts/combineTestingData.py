#Jacob Zahn

import sys
import time

import numpy as np
import pandas as pd
import datetime

sys.path.append('..')
import lib

CCHTS = lib.loadCCHTimeSeries()
CC = lib.loadUSCountiesCov()
DST = lib.loadDailyStateTesting()

#get date data

DAYBEFORE = '2020-01-20'
DAYBEFORE = np.datetime64(DAYBEFORE)
CCdates = CC['date']
CCdates = np.array(CCdates, dtype=np.datetime64)
CCdateRange = np.arange(DAYBEFORE, CCdates[-1]+np.timedelta64(1,'D'), dtype='datetime64[D]')

CCHTS_startDate = np.datetime64(((CCHTS.columns).to_numpy()[10])[-10:])
CCHTS_endDate = np.datetime64(((CCHTS.columns).to_numpy()[-1])[-10:])
CCHTSdateRange = np.arange(CCHTS_startDate, CCHTS_endDate+np.timedelta64(1,'D'), dtype='datetime64[D]')

dst_dates = DST['date'].to_numpy()
dst_dates = np.array([ pd.to_datetime(str(date), format='%Y%m%d') for date in dst_dates], dtype='datetime64[D]')
DST_startDate = np.datetime64(dst_dates[-1])
DST_endDate = np.datetime64(dst_dates[0])
DSTdateRange = np.arange(DST_startDate, DST_endDate, dtype='datetime64[D]')

DSTstates = DST['state'].to_numpy()
DSTstatesExp = []
for stateCode in DSTstates:
    DSTstatesExp.append(lib.stateDict[stateCode])
DSTstatesExp = np.array(DSTstatesExp)

#create date range thats the same as our cases/deaths data
tDateRange = np.arange(DAYBEFORE, CCdates[-1]+np.timedelta64(1,'D'), dtype='datetime64[D]')

#check dates totals CC and CCHTS should be == if CCHTS is as up to date as CC
print('CC date range: ',len(CCdateRange),'\tCCHTS date range: ',len(CCHTSdateRange),'\tDST date range: ',len(DSTdateRange))

#retrieve neccessary itterables from DST dst_dates was created above
dst_states = DST['state'].to_numpy()
dst_tests = DST['totalTestResults'].to_numpy()
dst_pos = DST['positive'].to_numpy()
dst_neg = DST['negative'].to_numpy()

#retrieve neccessary itterables from CCHTS
countyPop = CCHTS['population'].to_numpy()
countyState = CCHTS['state']

#create list of 51 states+dc postal codes
states = np.array(list(lib.stateDict.keys()))
removeStatesMask = ~np.isin(states,np.array(['AS','GU','MP','PR','VI','UM','FM','MH','PW','AA','AE','AP','CM','PZ','NB','PH','PC']))
states = states[removeStatesMask]

#get full state names
statesExp = np.array([lib.stateDict[stateCode] for stateCode in states])

#create zero filled holder matrix for daily state testing
tStateDay = np.zeros((len(states), len(tDateRange)), dtype=np.intc)
pStateDay = np.zeros((len(states), len(tDateRange)), dtype=np.intc)
nStateDay = np.zeros((len(states), len(tDateRange)), dtype=np.intc)

#create zero filled holder for cummulative state population
statePop = np.zeros((len(states)), dtype=np.intc)

#create indeces for traversing xStateDays
statesIndex = np.arange(len(states), dtype=np.intc)
datesIndex = np.arange(len(tDateRange), dtype=np.intc)

start = time.time()
for (s, state) in zip(statesIndex, states):
    stateMask = dst_states==state
    state_tests = dst_tests[stateMask]
    state_pos = dst_pos[stateMask]
    state_neg = dst_neg[stateMask]
    state_dates = dst_dates[stateMask]
    stateMask = countyState==statesExp[s]
    statePop[s] += np.sum(countyPop[stateMask])
    for (d, date) in zip(datesIndex, tDateRange):
        dateMap = state_dates==date
        sTestsTemp = state_tests[dateMap]
        sPosTemp = state_pos[dateMap]
        sNegTemp = state_neg[dateMap]
        numT = np.sum(sTestsTemp) if sTestsTemp.size != 0 else np.intc(0)
        numP = np.sum(sPosTemp) if sPosTemp.size != 0 else np.intc(0)
        numN = np.sum(sNegTemp) if sNegTemp.size != 0 else np.intc(0)
        prevT = tStateDay[s, d-np.intc(1)] if d != np.intc(0) else np.intc(0)
        prevP = pStateDay[s, d-np.intc(1)] if d != np.intc(0) else np.intc(0)
        prevN = nStateDay[s, d-np.intc(1)] if d != np.intc(0) else np.intc(0)
        tStateDay[s,d] = numT if numT >= prevT else prevT
        pStateDay[s,d] = numP if numP >= prevP else prevP
        nStateDay[s,d] = numN if numN >= prevN else prevN
end = time.time()
ellapsed = end-start
print('big loop took : ',ellapsed,' seconds')

#create and populate column names from dates
tDateRangeStr = np.empty(tDateRange.shape,dtype='<U11')
pDateRangeStr = np.empty(tDateRange.shape,dtype='<U11')
nDateRangeStr = np.empty(tDateRange.shape,dtype='<U11')
dateRangeDT = np.array([date.astype(datetime.datetime) for date in tDateRange])
dateRangeStr = np.array([date.strftime('%Y-%m-%d') for date in dateRangeDT])

for (d, date) in zip(datesIndex, dateRangeStr):
    tdate = np.unicode_('t')+date
    pdate = np.unicode_('p')+date
    ndate = np.unicode_('n')+date
    tDateRangeStr[d] = tdate
    pDateRangeStr[d] = pdate
    nDateRangeStr[d] = ndate


#create dataframes
dataDict = {
    'state' : statesExp,
    'population' : statePop
}
Ss = pd.DataFrame(dataDict, index = statesIndex)
Ts = pd.DataFrame(tStateDay, index = statesIndex, columns = tDateRangeStr)
Ps = pd.DataFrame(pStateDay, index = statesIndex, columns = pDateRangeStr)
Ns = pd.DataFrame(nStateDay, index = statesIndex, columns = nDateRangeStr)

#save
df = pd.concat([Ss, Ts, Ps, Ns], axis = 1)
df.to_csv('../data/Interim_data_views/StateTestingTimeSeries.csv', index = False)