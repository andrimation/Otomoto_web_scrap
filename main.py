import pandas as pd
import requests
import mysql.connector
from bs4 import BeautifulSoup
import time
import re
import datetime
import scrapCarOffer
import databaseDriver
import pandas
import dataFrameDriver
import os
import threading
import queue
import  carsBrandsAndLocalizations

brands = carsBrandsAndLocalizations.carsBrands
localizations = carsBrandsAndLocalizations.carsLocalizations

currentTable = "otomoto_cars_3"

result_queue = queue.Queue()

def getLinksInThreads(result_queue,linkSiteStartNum,linkSiteEndNum,brand,localization):
    listOflinks = scrapCarOffer.getListOfOffersLinks(linkSiteStartNum,linkSiteEndNum,brand,localization)
    print(listOflinks)
    result_queue.put(listOflinks)

def runLinksGatheringThreads(numberOfPAgesToScrap,result_queue,threads,numberOfThreads,brand,localization):
    threadCounter = 1
    for number in range(1, numberOfPAgesToScrap+(numberOfPAgesToScrap//numberOfThreads), numberOfPAgesToScrap // numberOfThreads if numberOfPAgesToScrap // numberOfThreads != 0 else 1):
        localEndNum = number + numberOfPAgesToScrap // numberOfThreads
        if threadCounter == numberOfThreads:
            localEndNum = numberOfPAgesToScrap
        thread = threading.Thread(target=getLinksInThreads,
                                  args=(result_queue, number, localEndNum,brand,localization))
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
    print(len(listOfOffersDicts))
    for dict in listOfOffersDicts:
        print(len(dict))
        for link in dict:
            fromDict.append(link)
    return fromDict


def mainProgramFunction():
    startProgram,databaseCursor,db_connection = databaseDriver.databaseDriver()
    if startProgram:

        dataFrameCreated = False

        correctDataTest =  scrapCarOffer.checkIfRegexIsCorrect()
        carNumber = 0
        if correctDataTest:
            listOfOffersLinksJoined = set()
            for brand in brands:
                for localization in localizations:
                    print(f"Marka {brand}  lokalizacja {localization}")
                    numberOfPAgesToScrap = scrapCarOffer.getNumberOfListSites(brand,localization)
                    # numberOfPAgesToScrap = 80

                    # threads = []
                    # numberOfThreads = 20
                    # runLinksGatheringThreads(numberOfPAgesToScrap,result_queue,threads,numberOfThreads,brand,localization)
                    #
                    # listOfOffersDicts = mergeThreadsResultsFromQueue(result_queue)

                    # listOfOffersLinks = converQueueResultToList(listOfOffersDicts)
                    # print(len(listOfOffersLinks))
                    # result_scrap_queue = queue.Queue()
                    listOfOffersLinks = scrapCarOffer.getListOfOffersLinks(1,numberOfPAgesToScrap+1,brand,localization)

                    for link in listOfOffersLinks:
                        listOfOffersLinksJoined.add(link)
                    print("dlugosc wszystkich linków:  ",len(listOfOffersLinksJoined))
                    # dlaczego jest tylko ok 22 tys ofert ?!!

        for siteLink in listOfOffersLinksJoined:
            carDataDict = scrapCarOffer.getCarDataFromOfferSide(siteLink)
            print(carDataDict)

            if carDataDict == None:
                continue

            if not dataFrameCreated:
                carsDataFrame = dataFrameDriver.openOrCreateDataFrame(carDataDict)
                dataFrameCreated = True
            else:
                carsDataFrame = dataFrameDriver.checkIfAllRowsExist(carsDataFrame,carDataDict)
                carsDataFrame = dataFrameDriver.updateDataFrame(carsDataFrame,carDataDict)

            carNumber += 1
            print("*****  Car number:    ",carNumber)
            if carNumber % 1000 == 0:
                carsDataFrame.to_csv("cars_data_frame.csv", index=False)
                carsDataFrame.to_html("cars.html")


        # Dodać kolumnę "ilość dni na otomoto - odstęp czasu między dodaniem oferty a jej zniknięciem z otomoto"
        # najcenniejsze są te które najkrócej są na otomoto

        # zrobić tak że w threadach pobierać dane a później tylko w jednym wątku sprawdzać czy cos jest w bazie

        else:
            print("Need to fix regex - data incorrect! Bye :)")
            return

    else:
        return

mainProgramFunction()

