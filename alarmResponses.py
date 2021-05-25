from datetime import datetime

def sample_responses(input_text):
	user_message = str(input_text).lower()
	
	if user_message in( 'hello', 'hi'):
		return "hello there!"
	if user_message in( 'who are you?'):
		return "I am webscrape bot!"
		
	if user_message in( 'time'):
		now = datetime.now()
		date_time = now.strftime("%d/%m/%y, %H:%M:%S ")
		return date_time
	return 'I dont understand what you just said'
