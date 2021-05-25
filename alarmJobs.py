from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

def sayhi(context):
    context.bot.send_message(context.job.context, text="hi")

def time(update, context):
    context.job_queue.run_repeating(sayhi, 5, context=update.message.chat_id, name = 'time')
    

def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True
    
def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str('time'), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)
