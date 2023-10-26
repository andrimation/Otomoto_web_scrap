import bisect

import pandas as pd
import requests
# import mysql.connector
from bs4 import BeautifulSoup
import time
import re
import datetime
import scrapCarOffer
# import databaseDriver
import pandas
import dataFrameDriver
import os
import threading
import queue
import  carsBrandsAndLocalizations

brands = carsBrandsAndLocalizations.carsBrands
localizations = carsBrandsAndLocalizations.carsLocalizations



currentTable = "otomoto_cars_3"

result_queue_numberOfLinks = queue.Queue()
result_queue_links = queue.Queue()
result_queue_cars_data = queue.Queue()

def getNumberOfPagesGatheringThreads(result_queue,localization,brand):
    numerOfPages = scrapCarOffer.getNumberOfListSites(brand,localization,thread=True)
    # print(numerOfPages)
    result_queue.put(numerOfPages)

def runNumberOfPagesGatheringThreads(result_queue,threads,localizations,brands):
    for localization in localizations:
        for brand in brands:
            thread = threading.Thread(target=getNumberOfPagesGatheringThreads,args=(result_queue,localization,brand))
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()

def getNumberOfLinksFromQueue(result_queue):
    resultList = []
    while not result_queue.empty():
        # print("number of links")
        resultList.append(result_queue.get())

    return resultList

def getLinksInThreads(result_queue,linkSiteEndNum,brand,localization):
    listOflinks = scrapCarOffer.getListOfOffersLinks(linkSiteEndNum,brand,localization)
    # print(listOflinks)
    result_queue.put(listOflinks)

def runLinksGatheringThreads(numberOfPAgesToScrapList,result_queue,threads):
    threadCounter = 1
    for subList in numberOfPAgesToScrapList:
        thread = threading.Thread(target=getLinksInThreads,
                                  args=(result_queue,subList[2],subList[1],subList[0]))
        thread.start()
        threads.append(thread)
        threadCounter += 1
    for thread in threads:
        thread.join()

def mergeThreadsResultsFromQueue(result_queue):
    listOfOffersLinks = []
    while not result_queue.empty():
        smallList = result_queue.get()
        listOfOffersLinks.append(smallList)
    return listOfOffersLinks

def converQueueResultToList(listOfOffersDicts):
    fromDict = []
    # print(len(listOfOffersDicts))
    for dict in listOfOffersDicts:
        print(len(dict))
        for link in dict:
            fromDict.append(link)
    return fromDict

def gatherCarDataThread(result_queue_cars_data,link):
    carDataDict = scrapCarOffer.getCarDataFromOfferSide(link)
    result_queue_cars_data.put(carDataDict)

def runGatheringCarsDataThreads(result_queue_cars_data,linksList,threads):
    for link in linksList:
        thread = threading.Thread(target=gatherCarDataThread,args=(result_queue_cars_data,link))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

def getDataFromCarDataResultQueue(result_queue_Cars_Data):
    resultList = []
    while not result_queue_Cars_Data.empty():
        resultList.append(result_queue_Cars_Data.get())

    return resultList

def updateDataFrame(carsDictsList):
    dataFrameCreated = False
    carNumber = 0
    for car in carsDictsList:
        # print("AddingCarTo Data Frame !",car["car_url"])


        if not dataFrameCreated:
            carsDataFrame = dataFrameDriver.openOrCreateDataFrame(car)
            dataFrameCreated = True
            # print("new data frame created")
        else:
            carsDataFrame = dataFrameDriver.checkIfAllRowsExist(carsDataFrame, car)
            carsDataFrame = dataFrameDriver.updateDataFrame(carsDataFrame, car)
            # print("car added")
        carNumber += 1
        # print("*****  Car number:    ", carNumber)
        if carNumber % 40000 == 0:
            carsDataFrame.to_csv("cars_data_frame.csv", index=False)
            carsDataFrame.to_html("cars.html")

    carsDataFrame.to_csv("cars_data_frame.csv", index=False)
    carsDataFrame.to_html("cars.html")

    # print("Data frame updated !")

def mainProgramFunction():
    startProgram = True
    if startProgram:

        dataFrameCreated = False

        correctDataTest =  scrapCarOffer.checkIfRegexIsCorrect()
        carNumber = 0
        if correctDataTest:
            listOfOffersLinksJoined = set()

            threads = []
            numberOfPagesPerBrandLoc = []

            runNumberOfPagesGatheringThreads(result_queue_numberOfLinks,threads,localizations,brands)
            numberOfLinks = getNumberOfLinksFromQueue(result_queue_numberOfLinks)
            print(numberOfLinks)

            threads = []
            runLinksGatheringThreads(numberOfLinks,result_queue_links,threads)
            linksDict = mergeThreadsResultsFromQueue(result_queue_links)
            linksList = converQueueResultToList(linksDict)

            print(len(linksList))
            # print(linksList)

            threads = []
            runGatheringCarsDataThreads(result_queue_cars_data,linksList,threads)
            carsDataList = getDataFromCarDataResultQueue(result_queue_cars_data)
            print(len(carsDataList))


            updateDataFrame(carsDataList)

                    # numberOfPagesPerBrandLoc.append([localization,brand,scrapCarOffer.getNumberOfListSites(brand,localization)])
                    # NAjpierw muszę mieć liczbę stron dla danej marki i lokalizacji

                    # threads = []
                    # numberOfThreads = 20
                    # runLinksGatheringThreads(numberOfPAgesToScrap,result_queue,threads,numberOfThreads,brand,localization)
                    #
                    # listOfOffersDicts = mergeThreadsResultsFromQueue(result_queue)

                    # listOfOffersLinks = converQueueResultToList(listOfOffersDicts)
                    # print(len(listOfOffersLinks))
                    # result_scrap_queue = queue.Queue()
                    # listOfOffersLinks = scrapCarOffer.getListOfOffersLinks(1,numberOfPAgesToScrap+1,brand,localization)

                    # for link in listOfOffersLinks:
                    #     listOfOffersLinksJoined.add(link)
                    # print("dlugosc wszystkich linków:  ",len(listOfOffersLinksJoined))
                    # # dlaczego jest tylko ok 22 tys ofert ?!!




        # Dodać kolumnę "ilość dni na otomoto - odstęp czasu między dodaniem oferty a jej zniknięciem z otomoto"
        # najcenniejsze są te które najkrócej są na otomoto

        # zrobić tak że w threadach pobierać dane a później tylko w jednym wątku sprawdzać czy cos jest w bazie

        else:
            print("Need to fix regex - data incorrect! Bye :)")
            return

    else:
        return

mainProgramFunction()