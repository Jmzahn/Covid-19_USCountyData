#library of helper functions
import os
import time

import numpy as np
import pandas as pd

#a bunch of data loading functions

#data from https://hifld-geoplatform.opendata.arcgis.com/datasets/hospitals
def loadHospitals():
    df = pd.read_csv(os.path.dirname(__file__)+'/data/Hospital_data/Hospitals.csv')
    return df

#data from https://github.com/nytimes/covid-19-data
def loadUSCountiesCov():
    df = pd.read_csv(os.path.dirname(__file__)+'/data/NYT_data/us-counties.csv')
    return df

#data sheet https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2019/co-est2019-alldata.pdf
#data from https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/
def loadCountyPopEst():
    df = pd.read_csv(os.path.dirname(__file__)+'/data/Census_data/co-est2019-alldata.csv', encoding='latin-1')
    return df

def loadCHCombined():
    df = pd.read_csv(os.path.dirname(__file__)+'/data/Interim_data_views/CountyHospitalCombined.csv')
    return df

def loadCCHTimeSeries():
    df = pd.read_csv(os.path.dirname(__file__)+'/data/Interim_data_views/CovCountyHospitalTimeSeries.csv')
    return df

#data from https://covidtracking.com/api/v1/states/daily.csv
def loadDailyStateTesting():
    df = pd.read_csv(os.path.dirname(__file__)+'/data/CovidTrackingProj_data/daily.csv')
    return df

def loadSTTS():
    df = pd.read_csv(os.path.dirname(__file__)+'/data/Interim_data_views/StateTestingTimeSeries.csv')
    return df

def loadMTS():
    df = pd.read_csv(os.path.dirname(__file__)+'/data/Final_data_view/MasterTimeSeries.csv.gz')
    return df

#function for loading MTS and converting to tensors
def loadNNData():
    
    MTS = loadMTS()
    #only grab this many rows : 307916 (counties*7*14)
    MTS = MTS.head(307916)
    Weeks=14
    Jump = 6
    TRAIN_weeks = 12-Jump
    VAL_weeks = Weeks-TRAIN_weeks-Jump
    COUNTIES = 3142
    TRAIN_SPLIT = Jump*COUNTIES*7+TRAIN_weeks*COUNTIES*7

    #get date info
    dates = MTS['date'].values
    dateStart = np.datetime64(dates[0])
    dateEnd = np.datetime64(dates[-1])
    dateRange = np.arange(dateStart, dateEnd+np.timedelta64(1,'D'), dtype='datetime64[D]')
    days = len(dateRange)

    #grab feature and target data
    featuresNames = ['beds', 'helipads', 'nonProf', 'private', 'governm', 'tests']
    features = MTS[featuresNames].to_numpy()
    targetsNames = ['cases']
    targets = MTS[targetsNames].to_numpy()

    validate_features = features[TRAIN_SPLIT:].reshape(VAL_weeks*7,COUNTIES, len(featuresNames))
    validate_targets = targets[TRAIN_SPLIT:].reshape(VAL_weeks*7,COUNTIES, len(targetsNames))
    features = features[Jump*COUNTIES*7:TRAIN_SPLIT].reshape(TRAIN_weeks*7,COUNTIES, len(featuresNames))
    targets = targets[Jump*COUNTIES*7:TRAIN_SPLIT].reshape(TRAIN_weeks*7,COUNTIES, len(targetsNames))
    
    return features, targets, validate_features, validate_targets, dateRange   


class Location:#simple class for holding the important location data obtained from Nominatim
    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon
    def set_name(self, new_name):
        self.name = new_name
    def set_lat(self, new_lat):
        self.lat = new_lat
    def set_lon(self, new_lon):
        self.lon = new_lon

def countyState_to_LatLong(counties, states):
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="schoolResearchCounties")
    locObjList = np.empty(counties.shape, dtype=Location)

    for n, (county, state) in enumerate(zip(counties, states)):
        location = county+', '+state
        geoLoc = geolocator.geocode(location, timeout=100)
        if geoLoc is not None:
            loc = Location(name = location,lat = geoLoc.latitude,lon = geoLoc.longitude)
            locObjList[n] = loc
        if(n%100==0):
            print(location+', ', n)
            #print(loc)
            time.sleep(120)
    
    return locObjList

def saveDictAsCSV(data_dict, data_name):
    #create dataframe from dictionary
    df=pd.DataFrame(data_dict)
    #save dataframe as csv
    df.to_csv(data_name,index=False)

def plotPreds(countyHistory, countyFuture, predictions):
    import matplotlib.pyplot as plt
    histIndex = np.arange(len(countyHistory))
    futureIndex = np.arange(len(countyHistory),len(countyHistory)+len(countyFuture))
    predIndex = np.arange(len(countyHistory),len(countyHistory)+len(predictions))
    lastHeight=countyHistory[-1]
    for pred in predictions:
        pred+=lastHeight
    
    plt.figure()
    plt.plot(histIndex, countyHistory, 'b--', label='History')
    plt.plot(futureIndex, countyFuture, 'b:', label='Future')
    plt.plot(predIndex, predictions, 'r:', label='Prediction')
    plt.ylabel('Cases as proportion of Pop')
    plt.xlabel('Time')
    plt.legend(loc='upper left')
    plt.show()

stateDict = {
        "AL": "Alabama" 	                                 ,
        "AK": "Alaska" 	                                 ,
        "AZ": "Arizona" 	                                 ,
        "AR": "Arkansas" 	                                 ,
        "CA": "California"                                 ,
        "CO": "Colorado" 	                                 ,
        "CT": "Connecticut"                                ,
        "DE": "Delaware" 	                                 ,
        "DC": "District of Columbia"                       ,
        "FL": "Florida" 	                                 ,
        "GA": "Georgia" 	                                 ,
        "HI": "Hawaii" 	                                 ,
        "ID": "Idaho" 	                                 ,
        "IL": "Illinois" 	 	                             ,
        "IN": "Indiana" 	 	                             ,
        "IA": "Iowa" 	                                     ,
        "KS": "Kansas" 	                                 ,
        "KY": "Kentucky" 	                                 ,
        "LA": "Louisiana" 	                             ,
        "ME": "Maine" 	                                 ,
        "MD": "Maryland"                                   ,
        "MA": "Massachusetts"                              ,
        "MI": "Michigan" 	                                 ,
        "MN": "Minnesota" 	                             ,
        "MS": "Mississippi"                                ,
        "MO": "Missouri" 	                                 ,
        "MT": "Montana" 	                                 ,
        "NE": "Nebraska" 	                                 ,
        "NV": "Nevada" 	                                 ,
        "NH": "New Hampshire"                              ,
        "NJ": "New Jersey"                                 ,
        "NM": "New Mexico"                                 ,
        "NY": "New York" 	                                 ,
        "NC": "North Carolina"                             ,
        "ND": "North Dakota"                               ,
        "OH": "Ohio"                                       ,
        "OK": "Oklahoma" 	                                 ,
        "OR": "Oregon" 	                                 ,
        "PA": "Pennsylvania"                               ,
        "RI": "Rhode Island"                               ,
        "SC": "South Carolina"                             ,
        "SD": "South Dakota" 	                             ,
        "TN": "Tennessee" 	                             ,
        "TX": "Texas" 	                                 ,
        "UT": "Utah" 	                                     ,
        "VT": "Vermont" 	                                 ,
        "VA": "Virginia" 	                                 ,
        "WA": "Washington" 	                             ,
        "WV": "West Virginia" 	                         ,
        "WI": "Wisconsin" 	                             ,
        "WY": "Wyoming" 	                                 ,
        "AS": "American Samoa"                             ,
        "GU": "Guam" 	                                     ,
        "MP": "Northern Mariana Islands" 	                 ,
        "PR": "Puerto Rico" 	                             ,
        "VI": "U.S. Virgin Islands" 	                     ,
        "UM": "U.S. Minor Outlying Islands" 	             ,
        "FM": "Micronesia" 	                             ,
        "MH": "Marshall Islands" 	                         ,
        "PW": "Palau" 	                                 ,
        "AA": "U.S. Armed Forces – Americas[d]"	            ,
        "AE": "U.S. Armed Forces – Europe[e]"	                ,
        "AP": "U.S. Armed Forces – Pacific[f]"	            ,
        "CM": "Northern Mariana Islands Obsolete postal code",
        "PZ": "Panama Canal Zone Obsolete postal code" 	 ,
        "NB": "Nebraska Obsolete postal code"				    ,
        "PH": "Philippine Islands Obsolete postal code" ,  
 	    "PC": "Trust Territory of the Pacific Islands Obsolete postal code"
}
