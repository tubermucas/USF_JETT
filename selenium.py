import sys
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

def main(data):
    booking_data = json.loads(data)
    driver = webdriver.Chrome()

    try:
        # Open the website
        driver.get("https://calendar.lib.usf.edu/spaces")
        time.sleep(2)

        # Select USF Tampa Library
        location_dropdown = Select(driver.find_element(By.ID, "s-lc-location"))
        location_dropdown.select_by_visible_text("USF Tampa Library")
        time.sleep(2)

        # Fill in other options
        Select(driver.find_element(By.ID, "s-lc-rm-categories")).select_by_visible_text(booking_data["category"])
        Select(driver.find_element(By.ID, "s-lc-rm-capacity")).select_by_visible_text(booking_data["capacity"])
        Select(driver.find_element(By.ID, "s-lc-rm-zones")).select_by_visible_text(booking_data["zone"])

        # Set date
        date_field = driver.find_element(By.ID, "s-lc-rm-date")
        date_field.clear()
        date_field.send_keys(booking_data["date"])

        # Set time
        driver.find_element(By.ID, "s-lc-rm-time-from").send_keys(booking_data["fromTime"])
        driver.find_element(By.ID, "s-lc-rm-time-to").send_keys(booking_data["untilTime"])

        # Check options
        for option in booking_data["options"]:
            checkbox = driver.find_element(By.XPATH, f"//label[contains(text(),'{option}')]/preceding-sibling::input")
            if not checkbox.is_selected():
                checkbox.click()

        # Click Search
        driver.find_element(By.XPATH, "//button[contains(text(),'Search')]").click()
        time.sleep(5)

        print("Booking completed successfully!")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

    finally:
        driver.quit()

if __name__ == "__main__":
    main(sys.argv[1])