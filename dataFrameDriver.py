import pandas
import time

def createCarsDataFrame(carDataDict):
    carDataDict["index"] = [0]
    carsDataFrame = pandas.DataFrame(carDataDict)

    return carsDataFrame

def openOrCreateDataFrame(carDataDict):
    try:
        carsDataFrame = pandas.read_csv("cars_data_frame.csv")
    except:
        carsDataFrame = createCarsDataFrame(carDataDict)

    return carsDataFrame

def checkIfAllRowsExist(dataFrame,carDataDict):
    listOfColumns = dataFrame.columns.to_list()
    for key in carDataDict.keys():
        if key not in listOfColumns:
            newColumn = pandas.Series(name=key)

            dataFrame = pandas.concat([dataFrame,newColumn],axis=1)

    return dataFrame

def carExistInDataFrame(dataFrame,carDataDict):
    return dataFrame["car_url"].eq(carDataDict["car_url"]).any()


def addNewCarToDataFrame(dataFrame,carDataDict):
    updatedDataFrame = dataFrame._append(carDataDict,ignore_index=True)

    return updatedDataFrame

def updateExistingCarData(dataFrame,carDataDict):
    index = dataFrame[dataFrame["car_url"]==carDataDict["car_url"]].index.tolist()[0]
    dataFrame.at[index,"offerLastSeenDate"] = carDataDict["offerLastSeenDate"]

    try:
        days = carDataDict["offerLastSeenDate"] - carDataDict["offerAddDate"]
        dataFrame.at[index,"daysOnInternet"] = days.days
        print("date Delta updated !!")

    except:
        print("date delta not updated !!!")
        pass


    return dataFrame


def updateDataFrame(dataFrame,carDataDict):

    if carExistInDataFrame(dataFrame,carDataDict):
        updatedDataFrame = updateExistingCarData(dataFrame, carDataDict)
        print("car in base")
    else:
        print("car not in base")
        updatedDataFrame = addNewCarToDataFrame(dataFrame,carDataDict)

    return updatedDataFrame

