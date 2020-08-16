#only run if CountyHospitalCombined.csv is not yet made, script will take a while to gather geolocation data because of API restrictions.
#Jacob Zahn
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append('..')
import lib


Hospitals = lib.loadHospitals()
USCountyCovidData = lib.loadUSCountiesCov()
USCountyPopData = lib.loadCountyPopEst()

#the most important information in Hospitals is COUNTY and BEDS
# this can be used to create a dataset of total hospital beds per county
#  other interesting columns is TRAUMA and HELIPAD

hospitalCounties = Hospitals['COUNTY']#Only 1604 counties present
hospitalStates = Hospitals['STATE']#we also need states to specify county
hospitalBeds = Hospitals['BEDS']#NAN are stored as -999 this needs changed. 662 nans
hospitalTrauma = Hospitals['TRAUMA']#many changes need to be made before data is usable
#^actually seems like most entries are not there so this may be useless information
hospitalHelipad = Hospitals['HELIPAD']#ready off the bat
hospitalOwner = Hospitals['OWNER']#GOVERNMENT, NON-PROFIT, PROPRIETARY

#print(hospitalBeds.value_counts())
#plt.hist(HospitalCounties)
#plt.hist(HospitalBeds)
#plt.hist(HospitalTrauma)
#plt.hist(HospitalHelipad)

#create a list of all counties

#start with USCountyPopData[CTYNAME] but filter out the numbers for the states
countyMask = (USCountyPopData['SUMLEV']==50).to_numpy()#this code filters by counties/like
countiesNames = USCountyPopData['CTYNAME'].iloc[countyMask]#one issue here is that some states have counties with the same names
statesNames = USCountyPopData['STNAME'].iloc[countyMask]#so lets store state names also
countiesPops = USCountyPopData['POPESTIMATE2019'].iloc[countyMask]




hospitalStatesExp = []

for stateCode in hospitalStates:
    hospitalStatesExp.append(lib.stateDict[stateCode])

hospitalStatesExp = pd.Series(hospitalStatesExp) 
#have to remove Palau, American Samoa, Northern Mariana Islands, US Virgin Islands, Guam, and Puerto Rico
hospitalStatesExpMask = (~hospitalStatesExp.isin(['Palau', 'American Samoa', 'Northern Mariana Islands', 'U.S. Virgin Islands', 'Guam', 'Puerto Rico'])).to_numpy()


hospitalStatesExp = hospitalStatesExp.iloc[hospitalStatesExpMask]
hospitalCounties = hospitalCounties.iloc[hospitalStatesExpMask]
hospitalBeds = pd.Series(hospitalBeds.iloc[hospitalStatesExpMask],dtype=np.float)
#hospitalTrauma = hospitalTrauma.iloc[hospitalStatesExpMask]
hospitalHelipad = hospitalHelipad.iloc[hospitalStatesExpMask]
hospitalOwner = hospitalOwner.iloc[hospitalStatesExpMask]


#create hospitalOwnerInts to NON-PROFIT, PROPRIETARY, and GOVERNMENT per county
nonProfHOint = np.zeros(hospitalOwner.shape, dtype=np.intc)
privateHOint = np.zeros(hospitalOwner.shape, dtype=np.intc)
governmHOint = np.zeros(hospitalOwner.shape, dtype=np.intc)



for n, owner in enumerate(hospitalOwner):
    if('NON-PROFIT' in owner):
        nonProfHOint[n] += 1
    elif('PROPRIETARY' in owner):
        privateHOint[n] += 1
    elif('GOVERNMENT' in owner):
        governmHOint[n] += 1

nonProfHOint = pd.Series(nonProfHOint)
privateHOint = pd.Series(privateHOint)
governmHOint = pd.Series(governmHOint)

#turn -999 to NaNs in HospitalBeds
hospitalBeds = hospitalBeds.where(hospitalBeds >= 0)

#turn Ys to 1 and Ns to 0
hospitalHelipadInt = np.zeros(hospitalHelipad.shape, dtype=np.intc)

for (n, hosHeli) in enumerate(hospitalHelipad):
    if (hosHeli=='Y'):
        hospitalHelipadInt[n] += 1 
    
hospitalHelipadInt = pd.Series(hospitalHelipadInt)

people = np.sum(countiesPops.to_numpy())
beds = np.nansum(hospitalBeds.to_numpy())
helipads = np.sum(hospitalHelipadInt.to_numpy())
#interesting totals

#remove county/bourough/parish/Census Area from countiesNames and capitalize\

countiesHolder=np.array(countiesNames, dtype=str)

for n, county in enumerate(countiesNames):
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
    countiesHolder[n] = county.upper()


county=countiesHolder[204]
state=statesNames[204]
#^LA for testing


#Abstract hospitalOwner to NON-PROFIT, PROPRIETARY, and GOVERNMENT per county
nonProfHperCounty = np.zeros(countiesNames.shape, dtype=np.intc)
privateHperCounty = np.zeros(countiesNames.shape, dtype=np.intc)
governmHperCounty = np.zeros(countiesNames.shape, dtype=np.intc)

#empty lists to be filled
bedsPerCounty = np.zeros(countiesNames.shape, dtype=np.double)
helipadsPerCounty = np.zeros(countiesNames.shape, dtype=np.intc)

#Loop for fetching county wise data from Hospitals
#O(n^2)


for n, (county, state)  in enumerate(zip(countiesHolder, statesNames.to_numpy())):
    countiesMask=(hospitalCounties==county).to_numpy()
    statesMask=(hospitalStatesExp==state).to_numpy()
    stateAndCountyMask = countiesMask&statesMask
    bedsPerCounty[n] += np.nansum(hospitalBeds.iloc[stateAndCountyMask].to_numpy())
    helipadsPerCounty[n] += np.nansum(hospitalHelipadInt.iloc[stateAndCountyMask].to_numpy())
    nonProfHperCounty[n] += np.sum(nonProfHOint.iloc[stateAndCountyMask].to_numpy())
    privateHperCounty[n] += np.sum(privateHOint.iloc[stateAndCountyMask].to_numpy())
    governmHperCounty[n] += np.sum(governmHOint.iloc[stateAndCountyMask].to_numpy())


#bedsPerCounty       = pd.Series(bedsPerCounty)
#helipadsPerCounty   = pd.Series(helipadsPerCounty)
#nonProfHperCounty   = pd.Series(nonProfHperCounty)
#privateHperCounty   = pd.Series(privateHperCounty)
#governmHperCounty   = pd.Series(governmHperCounty)

#countiesNames_partial = countiesNames.iloc[:1]
#statesNames_partial = statesNames.iloc[:1]

#this takes more than an hour because of api limits
countiesLocs = lib.countyState_to_LatLong(countiesNames, statesNames)

countiesLat = np.zeros(countiesNames.shape, dtype=float)
countiesLon = np.zeros(countiesNames.shape, dtype=float)

for n, county in enumerate(countiesLocs):
    countiesLat[n] = county.lat
    countiesLon[n] = county.lon

dataDict = {
    'COUNTY'      : countiesNames.to_numpy(),
    'STATE'       : statesNames.to_numpy(),
    'POPEST2019'  : countiesPops.to_numpy(),
    'BEDS'        : bedsPerCounty,
    'HELIPADS'    : helipadsPerCounty,
    'NONPROF'     : nonProfHperCounty,
    'PRIVATE'     : privateHperCounty,
    'GOVERNM'     : governmHperCounty,
    'LAT'         : countiesLat,
    'LON'         : countiesLon
}

dataName = '../data/Interim_data_views/CountyHospitalCombined.csv'

lib.saveDictAsCSV(dataDict,dataName)
