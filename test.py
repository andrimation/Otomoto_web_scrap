import requests
from bs4 import BeautifulSoup

def getListOfOffersLinks(link):
    listOfLinks = [1]

    # print(f"Site with links nr: {siteNumber}")
    otomoto = requests.request("GET", link)
    soup = BeautifulSoup(otomoto.text, "html.parser")
    for link in soup.find_all("a"):
        link = str(link.get("href"))
        if link.count("oferta") != 0:
            print(link)
            listOfLinks.append(link)
    return listOfLinks

site = requests.request("GET",f"https://www.otomoto.pl/osobowe?page={600}")

getListOfOffersLinks(f"https://www.otomoto.pl/osobowe?page={5500}")