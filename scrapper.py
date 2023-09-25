import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import unicodedata
import os
import multiprocessing
from tqdm import tqdm
# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's directory
os.chdir(script_dir)

# Constants for CSV filenames
BRANDS_CSV = 'brands.csv'
CATEGORIES_CSV = 'categories.csv'
URL_CSV = 'urls.csv'
PRICEHISTORY_CSV = 'pricehistory.csv'

# List of filament types
FILAMENT_TYPES = ['PLA+', 'PLA', 'TPU', 'PETG', 'others']

import requests
from fake_useragent import UserAgent

# Create a session with a random user agent
session = requests.Session()
ua = UserAgent()
session.headers.update({'User-Agent': ua.random}) 

def scrape_single_url(url):
    product_name, price, stock, brand, category = scrape_product_info(url)
    return {'Product Name': product_name, 'Price': price, 'Stock': stock, 'Brand': brand, 'Category': category}

# Function to clear the screen based on the OS
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
# Function to load existing URLs from the CSV file
def load_urls_from_csv(filename=URL_CSV):
    try:
        urls = []
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                urls.append(row['URL'])
        return urls
    except FileNotFoundError:
        return []

# Function to save URLs to a CSV file
def save_urls_to_csv(urls, filename=URL_CSV):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for url in urls:
            writer.writerow({'URL': url})

    print(f"URLs have been saved to {filename}")

# Function to add a new URL
def add_new_url(urls):
    while True:
        new_url = input("Enter a new URL (or 'done' to finish adding URLs): ")
        if new_url.lower() == 'done':
            break
        urls.append(new_url)
        save_urls_to_csv(urls)
        display_updated_urls(urls)

# Function to delete a URL
def delete_url(urls, index_to_delete):
    if 0 <= index_to_delete < len(urls):
        deleted_url = urls.pop(index_to_delete)
        save_urls_to_csv(urls)
        print(f"Deleted URL: {deleted_url}")
        display_updated_urls(urls)
    else:
        print("Invalid index.")

# Function to display the list of URLs
def display_initial_urls(urls):
    clear_screen()
    if urls:
        print("\nURLs:")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
    else:
        print("No URLs found.")

# Function to display the updated list of URLs
def display_updated_urls(urls):
    clear_screen()
    if urls:
        print("\nUpdated URLs:")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
    else:
        print("No URLs found.")

# Function to scrape product information from a product URL
def scrape_product_info(url):
    try:
        # Send an HTTP GET request to the URL using the session
        response = session.get(url)
        response.raise_for_status()

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate the element containing the product name using the "subheader" class
        product_name_element = soup.find('h1', {'class': 'subheader'})

        # Locate the element containing the price using the "product-pricing__price--discount" class
        price_element = soup.find('h2', {'class': 'product-pricing__price--discount'})

        # Locate the input element for stock information
        stock_input_element = soup.find('input', {'id': 'input-qty'})

        if product_name_element and price_element and stock_input_element:
            # Extract the product name, price, and stock information
            product_name = product_name_element.text.strip()
            # Remove "$" and "." characters from the price and convert it to a float
            price = float(price_element.text.replace('$', '').replace('.', '').strip())
            stock = stock_input_element.get('max', 'Stock information not found')

            # Extract the brand and category from the product name
            brand = extract_brand(product_name)
            category = extract_category(product_name)

            return product_name, price, stock, brand, category
        else:
            return "Product information not found", "Price not found", "Stock information not found", "Brand not found", "Category not found"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return "Error", "Error", "Error", "Error", "Error"

# Function to extract the brand from the product name
def extract_brand(product_name):
    product_name = product_name.lower()
    with open(BRANDS_CSV, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        brands = [row[0] for row in reader]

    for brand in brands:
        if brand.lower() in product_name:
            return brand.capitalize()
    return 'Other'

def extract_category(product_name):
    # Remove accents (tildes) from the product name
    product_name = remove_accents(product_name.lower())
    with open(CATEGORIES_CSV, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        categories = [row[0] for row in reader]

    for category in categories:
        if category.lower() in product_name:
            if category.lower() == "filamento":
                # Check for filament types
                for filament_type in FILAMENT_TYPES:
                    if filament_type.lower() in product_name:
                        return f"Filamento {filament_type}"
            return category.capitalize()
    return 'Other'

# Function to remove accents (tildes) from a string
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

# Function to load brands from a CSV file
def load_brands(filename=BRANDS_CSV):
    try:
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            brands = [row[0] for row in reader]
        return brands
    except FileNotFoundError:
        return []

# Function to save brands to a CSV file
def save_brands(brands, filename=BRANDS_CSV):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for brand in brands:
            writer.writerow([brand])

# Function to load categories from a CSV file
def load_categories(filename=CATEGORIES_CSV):
    try:
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            categories = [row[0] for row in reader]
        return categories
    except FileNotFoundError:
        return []

# Function to save categories to a CSV file
def save_categories(categories, filename=CATEGORIES_CSV):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for category in categories:
            writer.writerow([category])

# Function to display the brand submenu
def brand_submenu():
    while True:
        clear_screen()
        print("\nBrand Menu:")
        print("1. View Brands")
        print("2. Add Brand")
        print("3. Remove Brand")
        print("4. Back to Main Menu")

        brand_choice = input("Enter your choice: ")

        if brand_choice == '1':
            view_brands()
        elif brand_choice == '2':
            add_brand()
        elif brand_choice == '3':
            remove_brand()
        elif brand_choice == '4':
            break
        else:
            print("Invalid choice. Please enter a valid option (1-4).")

# Function to display the category submenu
def category_submenu():
    while True:
        clear_screen()
        print("\nCategory Menu:")
        print("1. View Categories")
        print("2. Add Category")
        print("3. Remove Category")
        print("4. Back to Main Menu")

        category_choice = input("Enter your choice: ")

        if category_choice == '1':
            view_categories()
        elif category_choice == '2':
            add_category()
        elif category_choice == '3':
            remove_category()
        elif category_choice == '4':
            break
        else:
            print("Invalid choice. Please enter a valid option (1-4).")

# Function to scrape product URLs
def scrape_urls():
    product_urls = []
    with open(URL_CSV, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product_urls.append(row['URL'])

    # Get the current date and time
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Create or open the CSV file to store the scraped product information
    csv_filename = PRICEHISTORY_CSV
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Product Name', 'Price', 'Stock', 'Brand', 'Category', 'Scraped Date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()  # Write header only if the file is empty

        # Set the number of processes to use for parallel scraping
        num_processes = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=num_processes)

        # Use parallel processing to scrape the URLs
        results = list(tqdm(pool.imap(scrape_single_url, product_urls), total=len(product_urls)))

        # Close the pool of processes
        pool.close()
        pool.join()

        # Write the results to the CSV file
        for result in results:
            writer.writerow({**result, 'Scraped Date': current_date})

    print("Scraping complete. Product information is saved in pricehistory.csv")
    input("Press Enter to continue...")


# Function to view brands
def view_brands():
    brands = load_brands()
    print("\nBrands:")
    for i, brand in enumerate(brands, 1):
        print(f"{i}. {brand}")
    input("Press Enter to continue...")  # Wait for user input

# Function to add a brand
def add_brand():
    brand = input("Enter a new brand: ")
    brands = load_brands()
    brands.append(brand)
    save_brands(brands)
    print(f"Brand '{brand}' added.")

# Function to remove a brand
def remove_brand():
    view_brands()
    index_to_remove = int(input("Enter the index of the brand to remove (0 to cancel): ")) - 1
    if index_to_remove == -1:
        return
    brands = load_brands()
    if 0 <= index_to_remove < len(brands):
        removed_brand = brands.pop(index_to_remove)
        save_brands(brands)
        print(f"Removed brand: {removed_brand}")
    else:
        print("Invalid index.")

# Function to view categories
def view_categories():
    categories = load_categories()
    print("\nCategories:")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category}")
    input("Press Enter to continue...")  # Wait for user input

# Function to add a category
def add_category():
    category = input("Enter a new category: ")
    categories = load_categories()
    categories.append(category)
    save_categories(categories)
    print(f"Category '{category}' added.")

# Function to remove a category
def remove_category():
    view_categories()
    index_to_remove = int(input("Enter the index of the category to remove (0 to cancel): ")) - 1
    if index_to_remove == -1:
        return
    categories = load_categories()
    if 0 <= index_to_remove < len(categories):
        removed_category = categories.pop(index_to_remove)
        save_categories(categories)
        print(f"Removed category: {removed_category}")
    else:
        print("Invalid index.")

# Function to display the main menu
import subprocess  # Import the subprocess module

def main_menu():
    while True:
        clear_screen()
        print("\nMain Menu:")
        print("1. Scrape Product URLs")
        print("2. Brand Menu")
        print("3. Category Menu")
        print("4. URL Menu")
        print("5. Run Price Change Program")
        print("6. Run Price List Generator Program")
        print("7. Quit")

        main_choice = input("Enter your choice: ")

        if main_choice == '1':
            scrape_urls()
        elif main_choice == '2':
            brand_submenu()
        elif main_choice == '3':
            category_submenu()
        elif main_choice == '4':
            url_submenu()
        elif main_choice == '5':
            subprocess.run(['python', 'pricechange.py'])  # Run pricechange.py
        elif main_choice == '6':
            subprocess.run(['python', 'pricelistgenerator.py'])  # Run pricelistgenerator.py
        elif main_choice == '7':
            break
        else:
            print("Invalid choice. Please enter a valid option (1-7).")
def url_submenu():
    urls = load_urls_from_csv()
    while True:
        clear_screen()
        display_initial_urls(urls)
        print("\nURL Menu:")
        print("1. Add a new URL")
        print("2. Delete a URL")
        print("3. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_new_url(urls)
        elif choice == '2':
            display_updated_urls(urls)
            index_to_delete = int(input("Enter the index of the URL to delete (0 to cancel): ")) - 1
            if index_to_delete == -1:
                continue
            delete_url(urls, index_to_delete)
        elif choice == '3':
            save_urls_to_csv(urls)
            break
        else:
            print("Invalid choice. Please enter a valid option (1-3).")
# Main program
if __name__ == "__main__":
    main_menu()
