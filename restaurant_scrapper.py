import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse

def scrape_restaurant_menus(search_query="restaurants in Sydney CBD"):
    """
    This function scrapes restaurant menu data from Google search results based on a search query.

    Parameters:
        search_query (str): The search term to be used for finding restaurants (default: 'restaurants in Sydney CBD').

    Returns:
        list: A list of dictionaries containing restaurant names and their respective menus.
    """
    # Initialize the WebDriver
    driver = webdriver.Chrome()

    try:
        # 1. Open Google and search for restaurants
        driver.get("https://www.google.com/")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)

        time.sleep(7)  # Wait for the results to load

        # 2. Click on the "See more places" button
        try:
            more_places_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'More places')]"))
            )
            more_places_button.click()
            print("Clicked on 'More places' button.")
        except Exception as e:
            print(f"Error clicking 'More places' button: {e}")
            return []

        # Initialize list for storing menu data
        menus_data = []

        # 3. Loop through restaurant listings
        restaurants = driver.find_elements(By.XPATH, "//span[@class='OSrXXb']")
        
        for index, restaurant in enumerate(restaurants):
            try:
                print(f"Clicking on restaurant {index + 1}: {restaurant.text}")
                restaurant.click()

                time.sleep(10)  # Wait for the restaurant page to load

                # 4. Click on the "Menu" span if available
                try:
                    menu_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Menu')]"))
                    )
                    menu_button.click()
                    time.sleep(3)  # Wait for the menu page to load

                    # 5. Extract the menu information
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')

                    # Find all divs with the class that contains the menu
                    menu_divs = soup.find_all('div', class_='Mqe04b bKZn5 aGLRdf a5uske')
                    menus_data.append({
                        'restaurant': restaurant.text,
                        'menu': [menu_div.get_text() for menu_div in menu_divs]
                    })

                except Exception as e:
                    print(f"No menu found for restaurant {index + 1}: {e}")

                # Wait before returning to the restaurant list
                time.sleep(5)

            except Exception as e:
                print(f"Error clicking on restaurant {index + 1}: {e}")

        return menus_data

    finally:
        # Quit the driver after finishing
        driver.quit()

def main():
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Scrape restaurant menus based on a search query.")
    
    # Add a command-line argument for the search query
    parser.add_argument(
        'search_query', 
        type=str, 
        help="Search query to find restaurants (e.g., 'restaurants in Sydney CBD')"
    )
    
    # Parse the arguments
    args = parser.parse_args()

    # Pass the search query to the scrape_restaurant_menus function
    menu_data = scrape_restaurant_menus(search_query=args.search_query)
    
    # Convert the list of menus to a DataFrame and print it
    df = pd.DataFrame(menu_data)
    print(df)

# Entry point for script execution
if __name__ == "__main__":
    main()