import csv
from datetime import datetime
import matplotlib.pyplot as plt
import configparser
import os

# check if path to config file exists
assert os.path.exists('venv/config.cfg')

# load in config file
config = configparser.RawConfigParser()
config.read('venv/config.cfg')

# set all the parameters for the program
startBrewDay = config.get('Parameters', 'startBrewDay')
endBrewDay = config.get('Parameters', 'endBrewDay')
movingWindow = config.getint('Parameters', 'movingWindow')
brewCountDay = config.get('Parameters', 'brewCountDay')
csvPath = config.get('Parameters', 'csvPath')

# convert loaded date strings into a date format for easy comparisons
startBrewDate = datetime.strptime(startBrewDay, '%m/%d/%Y').date()
endBrewDate = datetime.strptime(endBrewDay, '%m/%d/%Y').date()

# method to track contiguous days each customer has brewed coffee within specified period
def track_brew_duration(customer, custBrewDuration, currentDate):
    if customer not in custBrewDuration:    # if looking at new customer, then add to the dictionary and initialize
        custBrewDuration[customer] = {}
        custBrewDuration[customer]['previousDate'] = currentDate
        custBrewDuration[customer]['currentDuration'] = 1
        custBrewDuration[customer]['totalDurations'] = []
    else:
        if custBrewDuration[customer]['previousDate'] == currentDate:
            return custBrewDuration     # check case of customer brewing on already tracked date and skip
        if (currentDate - custBrewDuration[customer]['previousDate']).days == 1:
            custBrewDuration[customer]['currentDuration'] += 1      # increment counter for contiguous days
        if (currentDate - custBrewDuration[customer]['previousDate']).days > 1:
            custBrewDuration[customer]['totalDurations'].append(custBrewDuration[customer]['currentDuration'])
            custBrewDuration[customer]['currentDuration'] = 1       # store contiguous days and reset counter after skip

    custBrewDuration[customer]['previousDate'] = currentDate    # set last date checked for each customer
    return custBrewDuration

# primary method for reading through the data and solving each challenge
def solve_challenges():
    custBrewDuration = {}   # initialize dictionary for tracking contiguous brewing

    # create dictionary to be used to plot amount of customers for each brew duration
    plotDurs = {}
    for dur in range(1, (endBrewDate - startBrewDate).days + 2):
        plotDurs[dur] = 0

    # open the dataset file and read in data line by line
    with open(csvPath) as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')

        print(next(csvReader))      # skip first row containing header information

        row = next(csvReader)

        # initialize data using first row from dataset
        customer = row[1]

        currentDay = row[2]
        currentDate = datetime.strptime(currentDay, '%m/%d/%Y').date()

        dayCustCounter = {}     # dictionary to be used to count the number of customers brewing coffee each day
        dayCustCounter[currentDay] = {}
        dayCustCounter[currentDay]['count'] = 1
        if currentDay == brewCountDay:
            dayCustCounter[currentDay]['uniqueCount'] = 1
            dayCustCounter[currentDay]['customerList'] = [customer]
        avgList = []
        sumVal = 0

        # arrays for populating results of challenge 2 and 3 for saving to file
        chal2Vals = []
        chal3Vals = []

        if startBrewDate <= currentDate <= endBrewDate:     # check if date is in relevant period for challenge 2
            track_brew_duration(customer, custBrewDuration, currentDate)

        for row in csvReader:
            if currentDay != row[2]:    # check if a new day has started
                # add data from previous day for number of customers and moving average calculation
                avgList.append(dayCustCounter[currentDay]['count'])
                if len(avgList) < movingWindow:     # null out values that can't yet be averaged
                    dayCustCounter[currentDay]['average'] = None
                if len(avgList) == movingWindow:     # begin averaging once #days in window has passed
                    sumVal = sum(avgList)
                    dayCustCounter[currentDay]['average'] = sumVal/movingWindow
                if len(avgList) > movingWindow:   # remove old values to calculate new average
                    subVal = avgList.pop(0)
                    sumVal += (dayCustCounter[currentDay]['count'] - subVal)
                    dayCustCounter[currentDay]['average'] = sumVal/movingWindow

                # reinitialize data for new day
                customer = row[1]
                currentDay = row[2]
                currentDate = datetime.strptime(currentDay, '%m/%d/%Y').date()

                if startBrewDate <= currentDate <= endBrewDate:
                    track_brew_duration(customer, custBrewDuration, currentDate)

                if (currentDate - endBrewDate).days == 1:   # check that period for brew duration has passed
                    # add any remaining contiguous brew days to list for each customer
                    for custItem in custBrewDuration.keys():
                        custBrewDuration[custItem]['totalDurations'].append(custBrewDuration[custItem]['currentDuration'])
                        custBrewDuration[custItem]['currentDuration'] = 0
                        # populate dictionary with number of customers for each brew duration for plotting
                        for i in custBrewDuration[custItem]['totalDurations']:
                            plotDurs[i] += 1
                        chal2Vals.append((custItem, custBrewDuration[custItem]['totalDurations']))

                # reinitialize daily count of customers at the start of each new day
                dayCustCounter[currentDay] = {}
                dayCustCounter[currentDay]['count'] = 1
                if currentDay == brewCountDay:
                    dayCustCounter[currentDay]['uniqueCount'] = 1
                    dayCustCounter[currentDay]['customerList'] = [customer]
                continue

            customer = row[1]
            if startBrewDate <= currentDate <= endBrewDate:
                track_brew_duration(customer, custBrewDuration, currentDate)

            dayCustCounter[currentDay]['count'] += 1    # add to daily brew count

            if currentDay == brewCountDay:
                if customer not in dayCustCounter[currentDay]['customerList']:
                    dayCustCounter[currentDay]['uniqueCount'] += 1
                    dayCustCounter[currentDay]['customerList'].append(customer)

        # add data for last day for number of customers and moving average calculation
        avgList.append(dayCustCounter[currentDay]['count'])
        if len(avgList) < movingWindow:  # null out values that can't yet be averaged
            dayCustCounter[currentDay]['average'] = None
        if len(avgList) == movingWindow:  # begin averaging once #days in window has passed
            sumVal = sum(avgList)
            dayCustCounter[currentDay]['average'] = sumVal / movingWindow
        if len(avgList) > movingWindow:  # remove old values to calculate new average
            subVal = avgList.pop(0)
            sumVal += (dayCustCounter[currentDay]['count'] - subVal)
            dayCustCounter[currentDay]['average'] = sumVal / movingWindow

        # fill out challenge 3 values for saving
        for item in dayCustCounter.keys():
            chal3Vals.append((item, dayCustCounter[item]['average']))

        # print and save challenge solutions to files
        print('Challenge 1: '+str(dayCustCounter[brewCountDay]['uniqueCount'])+' unique customers on '+brewCountDay)
        with open('challenge_2.csv', 'w') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(['customer', 'contiguous days'])
            for row in chal2Vals:
                csv_out.writerow(row)
        print('Challenge 2: saved to file challenge_2.csv')
        with open('challenge_3.csv', 'w') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(['date', 'average brews'])
            for row in chal3Vals:
                csv_out.writerow(row)
        print('Challenge 3: saved to file challenge_3.csv')
        plt.bar(plotDurs.keys(), plotDurs.values())
        plt.gca().set(title='Distribution of Contiguous Brew Days '+startBrewDay+'-'+endBrewDay,
                      ylabel='Number of Customers', xlabel='Contiguous Days')
        plt.savefig('challenge_4.png')
        print('Challenge 4: saved to file challenge_4.png')


if __name__ == '__main__':
    solve_challenges()

