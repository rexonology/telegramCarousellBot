
from urllib.request import urlopen as ureq
from urllib.request import Request
from bs4 import BeautifulSoup as soup
import re
import webbrowser
import pickle
# ~ searchlist = []

searchListDict = {}

class Item: #This is a Class that stores all the item information
	def __init__(self, user, timeListed , title, price , link): 
		self.user = user
		self.timeListed = timeListed
		self.title = title
		self.price = price
		self.link = link
	def printAll(self):# Function to Print out all info of an item
		print('user is: ' + self.user)
		print('timeListed is: ' + self.timeListed)
		print('title is: ' + self.title)
		print('price is: ' + str(self.price))
		print('link is:\n' + self.link)

class userSearchTerm:
	def __init__(self, termName = '' , minPrice = 0, maxPrice = 100000,blockedNames = [], printedAlready = [], firstTime = 1 ):
		self.termName = termName
		self.minPrice = minPrice
		self.maxPrice = maxPrice
		self.blockedNames = blockedNames
		self.printedAlready = printedAlready
		self.firstTime = 1

def setup():
	global searchListDict
	searchListDict = pickle.load( open( "save.p", "rb" ) )
	print('annie')
	print(searchListDict)
	print('annie')
	return 1

def save():
	pickle.dump( searchListDict, open( "save.p", "wb" ) )
	return 1
		
def sortItems(list): # Function to sort all items in a list based on their price
	n = len(list)
	for i in range(n):
		for j in range(0 , n-i-1):
			if list[j].price >  list[j+1].price:
				list[j],list[j+1] = list[j+1],list[j]
	return list

def addSearchList(name, searchName, userMinPrice, userMaxPrice):
	searchlist = searchListDict[name]
	item = userSearchTerm(termName = searchName, minPrice = userMinPrice, maxPrice = userMaxPrice)
	searchlist.append(item)
	# ~ print("current search list is " + str(searchlist))
	return 1

def getSearchTerms(name ):
	searchlist = searchListDict[name]
	return searchlist
	
def removeSearchTerm(name, index):
	searchlist = searchListDict[name]
	if index-1 in range(len(searchlist)):
		searchlist.pop(index-1)
		return 1
	else:
		return 0

def getKeys():
	return searchListDict.keys()

def addUserKey(name):
	if name in searchListDict.keys():
		return 0
	else:
		searchListDict[name] = []
		return 1
	
def updateItem(name, index, newItem):
	searchListDict[name][index-1] = newItem
	return 1
	
def searchMaster(searchTerm = 'blank' , MinPrice = 0, MaxPrice = 100000, exactMode = 1): #This is the main function that searches and scrapes through carousell
	searchTerm = searchTerm.lower()
	searchTermSegments = searchTerm.split()
	searchTerm = searchTerm.replace(' ', '%20') #spacebar in url needs to be replaced with %20
	headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'
	} #Create a Header so as to access carousell
	myUrl = 'https://www.carousell.sg/search/' + searchTerm + '?canChangeKeyword=true' #Key in URL with relevant search term
	
	

	myRequest = Request(url = myUrl, headers = headers) #Create Request
	myClient = ureq(myRequest) # Read Request
	html = myClient.read() #Get HTML File
	myClient.close() # Close the CLient

	myPageSoup = soup(html, "html.parser")  #Parse HTML File
	paragraphs = myPageSoup.find_all('p' ) # Get all the paragraphs out


	itemList = []
	for paragraph in paragraphs:
		if re.match( "\S\$\d+", paragraph.text):
			itemList.append(paragraph.parent.parent)
	itemInfoList = []
	for item in itemList:
		
		linkList = item.find_all('a')
		link = 'www.carousell.sg' + linkList[1]['href']
		details = item.find_all('p')
		user = details[0].text
		timeListed = details[1].text
		title = details[2].text
		price = details[3].text
		price =  float(re.findall("\d+\.*\d*", price)[0])
		itemCollatedDetail = Item(user, timeListed , title, price , link)
		if (price >= MinPrice and price <= MaxPrice):
			if (exactMode == 1) and ( any(word in searchTermSegments for word in  title.lower().split()) ):
				itemInfoList.append(itemCollatedDetail)
			elif exactMode == 0:
				itemInfoList.append(itemCollatedDetail)
				
	itemInfoList = sortItems(itemInfoList)
	count = (len(itemInfoList))
	# ~ for item in reversed(itemInfoList):
		# ~ print('ItemNumber is: ' + str(count))
		# ~ print('user is: ' + item.user)
		# ~ print('timeListed is: ' + item.timeListed)
		# ~ print('title is: ' + item.title)
		# ~ print('price is: ' + str(item.price))
		# ~ print('link is:\n' + item.link)
		# ~ print('\n-------------------------------------------\n')
		# ~ count -= 1
	return itemInfoList
