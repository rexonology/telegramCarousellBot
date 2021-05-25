import alarmWebScrapeFunctions as ws
import re
from telegram.ext import *
from telegram.ext import Updater, CommandHandler, CallbackContext

def register_User(update, context):
	name = update['message'] ['chat'] ['username']
	add = ws.addUserKey(name)
	if add:
		update.message.reply_text('Registered!')
	else: 
		update.message.reply_text('Error or Already Registered!!')
 

def getKey(name):
	keys = ws.getKeys()
	return keys
	
	
def start_command(update, context):
	update.message.reply_text('If you havent done so yet, please use /reg to register your username! use /help to get commands list')
	update.message.reply_text('I will help to alert you to items that pop up on carousell within a price range that you specify. I work best when you choose a price range that has little existing matches.')
	update.message.reply_text('I suggest that you look at carousell, or use carou_scraper_bot, to get a good feel of the price range of your items before using me.')
	
def help_command(update, context):
	string = ''
	string += 'Hello! Here are some commands to get you started with\n'
	string += '/reg: register. register your user name. this is important and is the first thing you should do!\n'
	string += '/add: Add search term. Input format is "item @$minimumValue. eg </as samsung note 8 @$50>\n'
	string += '/rem: remove search term. eg </rs 1> removes the 1 item on your search list\n'
	string += '/check: check search Terms.\n'
	string += '/set: set alarm with your current search terms!\n'
	string += '/unset: unset currrent alarm!\n'
	
	update.message.reply_text(string)
	
		
def addSearch(update, context):
	
	name = update['message'] ['chat'] ['username']
	keyList = getKey(name)# get list of registered users
	
	#check if user is currently registered
	if not name in keyList:
		update.message.reply_text('you are currently not registered. Please use /reg to register first')
		return 0
	
	# Check if there is currently an alarm running 
	
	if check_job_exists(str(name)+" alarm", context) :
		update.message.reply_text('an Alarm is currently running. Please unset the alarm first')
		return 0
	
	# Check if Input is formatted correctly
	appendString = ''
	for word in context.args:
		appendString = appendString + (word)
		appendString = appendString +(' ')
	synthesisedTerms = re.split('\@\$' , appendString)
	if not len(synthesisedTerms) == 3:
		update.message.reply_text('Please Format Search Terms as <item name @$ Min Price @$ max Price>')
		update.message.reply_text('for example, <ipad pro @$ 20 @$ 30>')
		return 0
	# ~ formattedString = synthesisedTerms[0].lstrip().rstrip() + ' @$' + synthesisedTerms[1].lstrip().rstrip() 
	searchName =  synthesisedTerms[0].lstrip().rstrip()
	minPrice = int(synthesisedTerms[1].lstrip().rstrip() )
	maxPrice = int(synthesisedTerms[2].lstrip().rstrip() )
	ws.addSearchList( name , searchName, minPrice, maxPrice)
	TermList = RetrieveSearchTermsAsString(name)
	update.message.reply_text('Updated Search Terms. Current Search Terms Are:\n' + TermList)
	
def removeSearchTerms(update, context):
	
	name = update['message'] ['chat'] ['username']
	#Checking that User is Registered
	keyList = getKey(name) # get list of users
	if not name in keyList:
		update.message.reply_text('you are currently not registered. Please use /reg to register first') #remind user to register if not registered yet
		
	# Check if there is currently an alarm running 
	
	if check_job_exists(str(name)+" alarm", context) :
		update.message.reply_text('an Alarm is currently running. Please unset the alarm first')
		return 0
	searchTerms = retrieveSearchTermsAsObj(name) #get All search Terms pertaining to the user's username
	#Check that their selected item number is within the range of index values of their search term
	if int(context.args[0]) > len(searchTerms):
		update.message.reply_text('search term number does not exist!') #inform user that their chosen item index is not within the range of their current item index ranmge
		return 0 
		
	index = context.args[0]
	ws.removeSearchTerm(name, int(index)) #call on function to remove the search term
	TermList = RetrieveSearchTermsAsString(name)
	update.message.reply_text('Updated Search Terms. Current Search Terms Are:\n' + TermList)
	return 1
	
def checkSearch(update, context):
	
	name = update['message'] ['chat'] ['username']
	keyList = getKey(name)
	if not name in keyList:
		update.message.reply_text('you are currently not registered. Please use /reg to register first')
		return 0
	appendString = ''
	TermList = RetrieveSearchTermsAsString(name)
	update.message.reply_text('Current Search Terms Are:\n' + TermList)
	
def checkDict(update,context):
	print(ws.searchListDict)
	
	
def RetrieveSearchTermsAsString(name): #This function retrieves the search term as the string and name
	terms = ws.getSearchTerms(name)
	stringAppend = ''
	i = 1;
	for term in terms:
		stringAppend += str(i) + ':'+ term.termName + '@$' + str(term.minPrice)+ '@$' + str(term.maxPrice)+'\n'
		i += 1
	return stringAppend


def retrieveSearchTermsAsObj(name):
	terms = ws.getSearchTerms(name)
	return terms

def updateSearchItem(name, index, newItem):
	terms = ws.updateItem(name, index, newItem)
	return 1

def addBlockedName(update, context):
	name = update['message'] ['chat'] ['username'] # Get Name of User
	#Check if User is registered
	keyList = getKey(name) 
	if not name in keyList:
		update.message.reply_text('you are currently not registered. Please use /reg to register first')
		return 0 #If not registered, remind user to register first
		
	# Check if User inputted command correctly 
	OverallString = ''
	for word in context.args:
		OverallString += word + ' '
	if not re.search( '[\d+][\s]([\w\W])+', OverallString):
		update.message.reply_text('wrong format detected! please input as <searchItemNumber> <name>')
		return 0 
	
	
	searchTerms = retrieveSearchTermsAsObj(name) #get search terms in object form
	
	# Check if their chosen index is within the range of current search term index range
	if int(context.args[0]) > len(searchTerms):
		update.message.reply_text('search term number does not exist!')
		return 0 
		
	index = int(context.args[0])
	blockedName = context.args[1]
	
	Item = searchTerms[index-1]
	Item.blockedNames.append(blockedName)
	updateSearchItem(name, index, Item)
	
	newSearchTerms = retrieveSearchTermsAsObj(name)
	newItem = newSearchTerms[index-1]
	BlockedListString = ''
	for blockedName in newItem.blockedNames:
		BlockedListString += blockedName + '\n'
	update.message.reply_text('current block names for ' + newItem.termName + ' is:\n' + BlockedListString)
	return 1
	

# ~ def startSearch(update, context):
	# ~ name = update['message'] ['chat'] ['username']
	# ~ keyList = getKey(name)
	# ~ if not name in keyList:
		# ~ update.message.reply_text('you are currently not registered. Please use /reg to register first')
		# ~ return 0
	# ~ update.message.reply_text('Starting Search... Please Hold')
	# ~ searchTerms = ws.getSearchTerms(name)
	# ~ for term in searchTerms:
		# ~ synthesisedTerms = re.split('\@\$' , term)
		# ~ results = ws.searchMaster(searchTerm = synthesisedTerms[0] ,  MinPrice = int(synthesisedTerms[1]))
		# ~ resultsToPrint = []
		# ~ if 3 < len(results):
			# ~ maxRange=3
		# ~ else:
			# ~ maxRange = len(results)
		# ~ for i in range(maxRange):
			# ~ resultsToPrint.append(results[i])
		# ~ resultsToPrint.reverse()
		# ~ stringToPrint = ''
		# ~ print('hi')
		# ~ if len(resultsToPrint) == 0:
			# ~ print('hi2')
			# ~ update.message.reply_text('search term' + synthesisedTerms[0] + 'yields no results\n')
			# ~ return 0
		# ~ else:
			# ~ for item in resultsToPrint:
				# ~ stringToPrint += 'user is: ' + item.user +'\n'
				# ~ stringToPrint += 'timeListed is: ' + item.timeListed+'\n'
				# ~ stringToPrint += 'title is: ' + item.title+'\n'
				# ~ stringToPrint += 'price is: ' + str(item.price)+'\n'
				# ~ stringToPrint += 'link is:\n' + item.link+'\n'
				# ~ stringToPrint += '\n\n'
			# ~ update.message.reply_text(stringToPrint)
	# ~ update.message.reply_text('finished Searches! If search returns are blank, please check if you have updated search terms')
	
def startSearchLink(update, context):
	name = update['message'] ['chat'] ['username']
	
	# Check if User is in the registered user list
	keyList = getKey(name)
	if not name in keyList:
		update.message.reply_text('you are currently not registered. Please use /reg to register first')
		return 0
	
	# Inform
	update.message.reply_text('Starting Search... Please Hold')
	searchTerms = retrieveSearchTermsAsObj(name)
	
	
	for term in searchTerms:
		results = ws.searchMaster(searchTerm = term.termName,  MinPrice = term.minPrice) #Get Scraped Results 
		BannedUser = term.blockedNames #get list of banned names

		toExclude = [] #create list of indexes that match with the banned names
		for i in range( len(results)):
			if results[i].user in BannedUser:
				toExclude.append(i) #if the user of the search result matches the banned user, mark out the index
				
		resultsTemp = [] #resultsTemp will hold the list of non-excluded user items
		for i in range(len(results)):
			if not i in toExclude:
				resultsTemp.append(results[i])
		results = resultsTemp #update results with the new list of non excluded items
		resultsToPrint = [] #this will store all the results that would be sent through the telegram bot
		if 3 < len(results):
			maxRange=3 
		else:
			maxRange = len(results) #This ensure that the number of searches sent over telegram would not exceed 3
			
		for i in range(maxRange):
			resultsToPrint.append(results[i])
		resultsToPrint.reverse()
		stringToPrint = ''
		if len(resultsToPrint) == 0:
			update.message.reply_text('search term ' + term.termName + 'yields no results\n')
		else:
			for item in resultsToPrint:
				stringToPrint += 'user is: ' + item.user +'\n'
				stringToPrint += 'timeListed is: ' + item.timeListed+'\n'
				stringToPrint += 'title is: ' + item.title+'\n'
				stringToPrint += 'price is: ' + str(item.price)+'\n'
				stringToPrint += 'link is:\n' + item.link+'\n'
				stringToPrint += '\n\n'
			update.message.reply_text(stringToPrint)
	update.message.reply_text('finished Searches! If search returns are blank, please check if you have updated search terms')

def getData(update, context):
	print(update)

def remove_job_if_exists(name: str, context: CallbackContext):
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True
    
def check_job_exists(name: str, context: CallbackContext):
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    return True

def alarm(context) -> None:
	job = context.job
	synthesisedterms = context.job.name.split()
	name = synthesisedterms[0]
	searchTerms = retrieveSearchTermsAsObj(name)
	
	for term in searchTerms:
		results = ws.searchMaster(searchTerm = term.termName,  MinPrice = term.minPrice, MaxPrice = term.maxPrice) #Get Scraped Results 
		BannedUser = term.blockedNames #get list of banned names
		printedAlready = term.printedAlready #get list of printed already stuff
	
		toExclude = [] #create list of indexes that match with the banned names and items printed Already
		for i in range( len(results)):
			if (results[i].user in BannedUser) or (results[i].user+results[i].title+str(results[i].price) in printedAlready):
				toExclude.append(i) #if the user of the search result matches the banned user, mark out the index
		resultsTemp = [] #resultsTemp will hold the list of non-excluded user items
		for i in range(len(results)):
			if not i in toExclude:
				resultsTemp.append(results[i])
		results = resultsTemp #update results with the new list of non excluded items
		
		#add New Terms into Printed Already attribute of each object
		for result in results:
			term.printedAlready.append(result.user+result.title+str(result.price))
		
		resultsToPrint = [] #this will store all the results that would be sent through the telegram bot

		if len(results) > 5:
			strpr = ''
			strpr += 'currently, there are ' + str(len(results))+ ' existing/ newly added items that match ' + term.termName + '.\n\n'
			strpr += 'we suggest that you look at carousell or use carou_scraper_bot to get a feel of what are the price ranges of the item. For now, I will just show the lowest priced 5 results.\n\n'
			strpr += 'The other results will not be alerted to you. But I will still alert you of any new results that match your price range in the future.'
			context.bot.send_message(job.context, text=strpr)
		maxRange = min(5, len(results))
		for i in range(  maxRange):
			resultsToPrint.append(results[i])
		resultsToPrint.reverse()
		stringToPrint =  '@@@@@@@@@@' +'new results for ' + term.termName  + ':@@@@@@@@@@\n'
		if len(resultsToPrint) == 0:
			p = 1 #random placeholder
		else:
			for item in resultsToPrint:
				stringToPrint += 'user is: ' + item.user +'\n'
				stringToPrint += 'timeListed is: ' + item.timeListed+'\n'
				stringToPrint += 'title is: ' + item.title+'\n'
				stringToPrint += 'price is: ' + str(item.price)+'\n'
				stringToPrint += 'link is:\n' + item.link+'\n'
				stringToPrint += '\n\n'
			context.bot.send_message(job.context, text=stringToPrint)
		

def saveDict(context):
	ws.save()
	return 1

def setup(update, context):
	ws.setup()
	print('setup done')
	return 1

def set_save(update, context):
	chat_id = update.message.chat_id
	context.job_queue.run_repeating(saveDict, interval = 5 , first = 1, context=chat_id, name="save") #note that job is titled as <userName alarm>
	print('save mode on')
	# ~ print(ws.searchListDict)

def set_Alarm(update, context):
	name = update['message'] ['chat'] ['username']
	# Check if User is in the registered user list
	keyList = getKey(name)
	if not name in keyList:
		update.message.reply_text('you are currently not registered. Please use /reg to register first')
		return 0
	
	searchTermList = RetrieveSearchTermsAsString(name)
	if(check_job_exists(str(name)+ " alarm", context)):
		update.message.reply_text('Alarm Has Already Been Set for:\n' + searchTermList)
		return 0

	chat_id = update.message.chat_id
	context.job_queue.run_repeating(alarm, interval = 300 , first = 1, context=chat_id, name=str(name)+" alarm") #note that job is titled as <userName alarm>
	
	update.message.reply_text('Alarm Has Been Set for:\n' + searchTermList)


 
def unset_Alarm(update, context):
	name = update['message'] ['chat'] ['username']
	chat_id = update.message.chat_id
	jobName = " alarm"
	job_removed = remove_job_if_exists(str(name)+ jobName, context)
	if job_removed:
		update.message.reply_text('Alarm has been unset')
	else:
		update.message.reply_text('Alarm was already not active')
