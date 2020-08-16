#Jacob Zahn

import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

sys.path.append('..')
import lib

CCH = lib.loadCCHTimeSeries()

beds = CCH['beds'].to_numpy()
population = CCH['population'].to_numpy()
helipads = CCH['helipads'].to_numpy()
nonProf = CCH['nonProf'].to_numpy()
private = CCH['private'].to_numpy()
governm = CCH['governm'].to_numpy()
totalHosp = nonProf + private + governm
casesLast = CCH['c2020-08-14'].to_numpy()
deathsLast = CCH['d2020-08-14'].to_numpy()

bedsZ = stats.zscore(beds)
populationZ = stats.zscore(population)

print('Explore multivariate relationships among the variables')
plt.figure()
plt.scatter(population,beds, c=casesLast, cmap=matplotlib.cm.cividis)
plt.title('beds vs population, colored by cases')
plt.xlabel('County population')
plt.ylabel('County hospital beds')
plt.colorbar()

plt.figure()
plt.scatter(populationZ,bedsZ, c=casesLast, cmap=matplotlib.cm.cividis)
plt.title('beds vs population, colored by cases')
plt.xlabel('County population Z')
plt.ylabel('County hospital beds Z')
plt.colorbar()

plt.figure()
plt.scatter(population,beds, c=deathsLast, cmap=matplotlib.cm.cividis)
plt.title('beds vs population, colored by deaths')
plt.xlabel('County population')
plt.ylabel('County hospital beds')
plt.colorbar()

plt.figure()
plt.scatter(populationZ,bedsZ, c=deathsLast, cmap=matplotlib.cm.cividis)
plt.title('beds vs population, colored by deaths')
plt.xlabel('County population Z')
plt.ylabel('County hospital beds Z')
plt.colorbar()

plt.show()

plt.figure()
plt.scatter(population,nonProf, c=casesLast, cmap=matplotlib.cm.cividis)
plt.title('Non profit hospitals vs population, colored by cases')
plt.ylabel('Non profit hospitals')
plt.xlabel('Population')
plt.colorbar()

plt.figure()
plt.scatter(population,private, c=casesLast, cmap=matplotlib.cm.cividis)
plt.title('Private hospitals vs population, colored by cases')
plt.ylabel('Private hospitals')
plt.xlabel('Population')
plt.colorbar()

plt.figure()
plt.scatter(population,governm, c=casesLast, cmap=matplotlib.cm.cividis)
plt.title('Government hospitals vs population, colored by cases')
plt.ylabel('Government hospitals')
plt.xlabel('Population')
plt.colorbar()

plt.show()

print('\nDerive new variables basesd on a combination of existing variables')
plt.figure()
plt.scatter(10000*(beds/population),casesLast)
plt.title('beds per 10000 people vs cases')
plt.xlabel('County beds per 10,000 people')
plt.ylabel('Cases')

plt.figure()
plt.scatter(10000*(beds/population),deathsLast)
plt.title('beds per 10000 people vs deaths')
plt.xlabel('County beds per 10,000 people')
plt.ylabel('Cases')

plt.figure()
plt.scatter(10000*(totalHosp/population),casesLast)
plt.title('Total hospitals per 10,000 people vs cases')
plt.xlabel('Total Hospitals per 10,000 people')
plt.ylabel('Cases')

plt.show()