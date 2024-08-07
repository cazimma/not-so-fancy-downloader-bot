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
    filename='bot.log',  # Specify the log file name here
    filemode='a'  # 'a' for append mode, 'w' to overwrite each time
)

def close_ad_window(main_window: str, driver: webdriver.Chrome):
    # If a new window is opened, it is closed
    current_window = driver.current_window_handle
    if current_window != main_window:
        logging.info("AD window closed.")
        driver.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

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

            main_window = driver.current_window_handle

            # Wait for the input field to be present
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "url")))

            # Fill in the URL directly into the field
            url_input = driver.find_element(By.ID, "url")
            url_input.send_keys(message)

            # Click the 'Get video' button (assuming there's a button to be clicked to start the download process)
            submit_button = driver.find_element(By.XPATH, "//button[@id='submit']")
            actions = ActionChains(driver)
            actions.move_to_element(submit_button).click().perform()
            
            
            # Wait for new windows/tabs to appear
            #WebDriverWait(driver, 10).until(EC.new_window_is_opened)

            # Click again 2 times on the submit button
            actions.move_to_element(submit_button).click().perform()
            actions.move_to_element(submit_button).click().perform()
            
            # Wait for the download button container to appear and then save the link
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "download-link")))
            download_container = driver.find_element(By.CLASS_NAME, "download")
            download_link = download_container.find_element(By.CLASS_NAME, "download-link").get_attribute("href")

            # Handle multiple tabs/windows
            #all_windows = driver.window_handles

            #download_link = None

            # Wait for the download link container
            # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "download-link")))
            
            # download_container = driver.find_element(By.CLASS_NAME, "download")
            # download_button = download_container.find_element(By.CLASS_NAME, "download-link")
            # actions.move_to_element(download_button).click().perform()

            # close_ad_window(main_window, driver)

            # for window in all_windows:
            #     if window != main_window:
            #         driver.switch_to.window(window)
            #         # Check if this window is the correct one by verifying the URL
            #         if "ttdownloader.com" in driver.current_url:
            #             try:
            #                 # Wait for the download link container
            #                 WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "download-link")))

            #                 # Extract the download link
            #                 download_container = driver.find_element(By.CLASS_NAME, "download")
            #                 download_button = download_container.find_element(By.CLASS_NAME, "download-link") #.get_attribute("href")
            #                 actions.move_to_element(download_button).click().perform()
            #                 download_link = download_container.find_element(By.CLASS_NAME, "download-link").get_attribute("href")

            #                 if download_link:
            #                     break
            #             except Exception as e:
            #                 logging.error(f"Error while extracting download link: {e}")
            #         # Close the ad window if no download link is found
            #         driver.close()
            #         driver.switch_to.window(main_window)

            if download_link:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=download_link)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="No download link.")
        except Exception as e:
            logging.error(f"Error: {e}. Exception raised.")
        finally:
            # Quit the WebDriver
            driver.quit()
            
            #await context.bot.send_message(chat_id=update.effective_chat.id, text="Quit the WebDriver.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please send a valid TikTok link.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please send a TikTok link to download the video.")

if __name__ == '__main__':
    token = Path('token.txt').read_text()
    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    download_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), download)
    echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    application.add_handler(start_handler)
    application.add_handler(download_handler)
    application.add_handler(echo_handler)

    application.run_polling()
