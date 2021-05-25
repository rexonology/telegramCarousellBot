import alarmConstants as keys
from telegram.ext import *
import alarmResponses as r
import alarmCommand as cmd
import alarmJobs as j
import alarmWebScrapeFunctions as ws
import pickle



def handle_message(update, context):
	text = str(update.message.text).lower()
	response = r.sample_responses(text)
	update.message.reply_text(response)

def error(update, context):
	print(f'Update {update} caused error {context.error}')
	
	 
def main():
	# ~ 
	print(ws.searchListDict)
	updater = Updater(keys.API_KEY , use_context = True)
	dp = updater.dispatcher
	dp.add_handler(CommandHandler("start", cmd.start_command))
	dp.add_handler(CommandHandler("help", cmd.help_command))
	dp.add_handler(CommandHandler("add", cmd.addSearch))
	dp.add_handler(CommandHandler("rem", cmd.removeSearchTerms))
	dp.add_handler(CommandHandler("reg", cmd.register_User))
	dp.add_handler(CommandHandler("check", cmd.checkSearch))
	dp.add_handler(CommandHandler("set", cmd.set_Alarm))
	dp.add_handler(CommandHandler("unset", cmd.unset_Alarm))
	dp.add_handler(CommandHandler("saveAdmin", cmd.set_save))
	dp.add_handler(CommandHandler("setupAdmin", cmd.setup))
	# ~ dp.add_handler(CommandHandler("bu", cmd.addBlockedName))
	dp.add_handler(MessageHandler(Filters.text, handle_message))
	
	dp.add_error_handler(error)
	
	
	updater.start_polling() #Number indicates seconds 
	updater.idle()







print('Bot started...')
main()



