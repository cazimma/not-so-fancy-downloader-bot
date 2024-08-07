import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    #filename='bot.log',  # Specify the log file name here
    #filemode='a'  # 'a' for append mode, 'w' to overwrite each time
)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! I convert TikTok links to videos that can be easily downloaded!")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    if 'tiktok.com/' in message:
        try:
            # Configure Selenium options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode (without opening browser window)
            driver = webdriver.Chrome(options=chrome_options)

            # Navigate to the ttdownloader page
            driver.get("https://ttdownloader.com/")

            # Wait for the input field to be present
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "url")))

            # Fill in the URL directly into the field
            url_input = driver.find_element(By.ID, "url")
            url_input.send_keys(message)

            # Click the 'Get video' button (assuming there's a button to be clicked to start the download process)
            submit_button = driver.find_element(By.XPATH, "//button[@id='submit']")
            actions = ActionChains(driver)
            actions.move_to_element(submit_button).click().perform()
            
            # Click again 2 times on the submit button to trigger ads
            actions.move_to_element(submit_button).click().perform()
            actions.move_to_element(submit_button).click().perform()
            
            download_link = None
            
            try: 
                # Wait for the download button container to appear and then save the link
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "download-link")))
                download_container = driver.find_element(By.CLASS_NAME, "download")
                download_link = download_container.find_element(By.CLASS_NAME, "download-link").get_attribute("href")
            except Exception as e:
                logging.error(f"Error while extracting download link: {e}")

            if download_link:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=download_link)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="No download link found. Insert a valid link.")
        except Exception as e:
            logging.error(f"Error: {e}. Exception raised.")
        finally:
            # Quit the WebDriver
            driver.quit()   
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please send a valid TikTok link.")

if __name__ == '__main__':
    token = Path('token.txt').read_text()
    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    download_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), download)

    application.add_handler(start_handler)
    application.add_handler(download_handler)

    application.run_polling()
