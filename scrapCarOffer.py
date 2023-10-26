import requests
# import mysql.connector
from bs4 import BeautifulSoup
import time
import re
import datetime
#

def getNumberOfListSites(carBrand,localization,thread=False):
    numberOfPages = ""
    while type(numberOfPages) != int:
        try:
            otomotoMain = requests.request("GET", f"https://www.otomoto.pl/osobowe/{carBrand}/{localization}?search%5Badvanced_search_expanded%5D=true").text
            #print(otomotoMain)
            regex = re.search(r'Wszystkie \(\d+\s?\d?\d?\d?',otomotoMain)
            regex = str(regex.group())
            # print(regex[11:])
            # time.sleep(1)
            #print(otomotoMain.index("Ogłoszeń</span></span></button>"),"index")
            # time.sleep(1)
            #numberOfPages = int(otomotoMain[70341:70349].replace(" ", "")) // 32
            numberOfPages = int(regex[11:].replace(" ", ""))//32
            if numberOfPages == 0:
                numberOfPages = 1
            # print("number of pages",numberOfPages)
            # time.sleep(1)
            # if numberOfPages < 6000 or numberOfPages > 6900:
            #     print("Podejrzany number of pages !! Wstrzymano działanie programu w obawie o bazę danych !!")
            #     numberOfPages = str(numberOfPages)
            # print(numberOfPages)

        except:
            if thread == False:
                return 0
            else:
                return [localization,carBrand,1]
    if thread == False:
        return numberOfPages
    else:
        return [localization,carBrand,numberOfPages]


def getListOfOffersLinks(end,brand,localization):
    listOfLinks = []
    for siteNumber in range(1, end+1):
        # print(f"Site with links nr: {siteNumber}")
        otomoto = requests.request("GET", f"https://www.otomoto.pl/osobowe/{brand}/{localization}?page={siteNumber}&search%5Badvanced_search_expanded%5D=true")
        soup = BeautifulSoup(otomoto.text, "html.parser")
        for link in soup.find_all("a"):
            link = str(link.get("href"))
            if link.count("oferta") != 0:
                listOfLinks.append(link)
    return listOfLinks

def unhideVinAndPhoneNumbers():
    pass

def getSiteAndCreateSoupObject(siteLink):
    siteText = requests.request("GET",siteLink).text
    #time.sleep(1)
    soupObject = BeautifulSoup(siteText,"html.parser")
    return soupObject,siteText

def getOfferAddDate(siteText,carDataDict):

    regex = re.search(r"\d\d:\d\d,\s\d\d\s.*\d\d\d\d",siteText)
    if regex != None:
        regex = regex.group()
    else:
        # print("!!! NO DATE ADDED  !")
        regex = 0;

    if regex != 0:
        regexToDate = regex.split()[1:]
        months = {"stycznia":1,"lutego":2,"marca":3,"kwietnia":4,"maja":5,"czerwca":6,"lipca":7,"sierpnia":8,"września":9,"pazdziernika":10,
                  "listopada":11,"grudnia":12}

        carDataDict["offerAddDate"] = datetime.date(int(regexToDate[2]),months[regexToDate[1]],int(regexToDate[0]))
    else:
        carDataDict["offerAddDate"] = None

    carDataDict["offerLastSeenDate"] = datetime.date.today()

    return carDataDict

def fixFirstRegisterDate(carDataDict):
    if "Data pierwszej rejestracji w historii pojazdu" in carDataDict.keys():
        # print("fixing first register date")
        dataToFix = carDataDict.pop("Data pierwszej rejestracji w historii pojazdu")
        dataToFix = dataToFix.split("/")
        fixedData = datetime.date(int(dataToFix[2]), int(dataToFix[1]), int(dataToFix[0]))
        carDataDict["firstRegisterDate"] = fixedData
        return carDataDict
    else:
        return carDataDict

def scrapCarsDataFromOfferSite(soupObject,carDataDict):

    offersParamsLabels = soupObject.select(".offer-params__list")


    for label in offersParamsLabels:
        new = BeautifulSoup(str(label),"html.parser")
        getLabel = soupObject.select(".offer-params__label")
        getValue = soupObject.select(".offer-params__value")
        for label,value in zip(getLabel,getValue):
            labelData = label.text.strip()
            labelValue = value.text.strip()
            labelDataFixed = fixLabelText(labelData)
            carDataDict[labelData] = labelValue


    offersParamsValues = soupObject.select(".parameter-feature-item")


    return carDataDict


def checkIfRegexIsCorrect():
    testDict = dict()
    testListOfLinks = getListOfOffersLinks(2,"ford","zachodniopomorskie")
    soupObject,siteText = getSiteAndCreateSoupObject(testListOfLinks.pop())
    testDict = getOfferAddDate(siteText,testDict)
    testDict = scrapCarsDataFromOfferSite(soupObject,testDict)

    showTestDictData(testDict)

    dataCorrect = input("Is car data correct?: y/n ")
    if dataCorrect == "y":
        return True
    else:
        return False

def showTestDictData(testDict):
    for key in testDict.keys():
        print(key,":  ",testDict[key])

def getGptDictData(soupObject,carDataDict):

    return carDataDict

def getCarEquipmentData(soupObject,carDataDict):

    offersEquipmentLabels = soupObject.select(".parameter-feature-item")

    for label in offersEquipmentLabels:
        labelText = label.text.strip()
        carDataDict[labelText] = 1

    return carDataDict

def fixLabelText(textToFix):
    special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '=', '[', ']', '{', '}', '|',
                     '\\', ';', ':', "'", '"', ',', '<', '>', '.', '/', '?'," ","\n"]
    for sign in special_chars:
        textFixed = textToFix.strip()
        textFixed = textToFix.replace(sign,"_")
        textFixed.strip()

    return textToFix

def countOfferNumberOfDays(carDataDict):
    try:
        daysDatetime = carDataDict["offerLastSeenDate"] - carDataDict["offerAddDate"]
        carDataDict["daysOnInternet"] = daysDatetime.days
    except:
        carDataDict["daysOnInternet"] = "NaN"

    return carDataDict


    #######################################

siteLink = """https://www.otomoto.pl/osobowe/oferta/peugeot-2008-peugeot-2008-2014-r-1-6-vti-active-120-km-125-000-km-ID6FylxS.html"""

def getCarDataFromOfferSide(siteLink):

    carDataDict = {"car_url":siteLink}

    soupObject,siteText = getSiteAndCreateSoupObject(siteLink)

    carDataDict = getOfferAddDate(siteText,carDataDict)

    carDataDict = scrapCarsDataFromOfferSite(soupObject,carDataDict)

    carDataDict = getGptDictData(soupObject,carDataDict)

    carDataDict = getCarEquipmentData(soupObject,carDataDict)

    carDataDict = fixFirstRegisterDate(carDataDict)

    carDataDict = countOfferNumberOfDays(carDataDict)

    # print("Downloaded Car Data !:",carDataDict["car_url"])

    return carDataDict
