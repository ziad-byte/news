import requests
from bs4 import BeautifulSoup
import json
import re
import os

# Function to create the JSON file if it doesn't exist
def create_json_file(file_name='urls.json'):
    if not os.path.exists(file_name):
        with open(file_name, 'w') as outfile:
            json.dump([], outfile)  # Initialize with an empty list
        print(f"'{file_name}' has been created.")

# Function to fetch articles from URLs loaded from a JSON file
def fetch_articles():
    urls = load_urls()  # Load URLs from the JSON file
    results = []
    
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            # Extract the page title
            page_title = soup.title.string.strip() if soup.title else 'No title found'

            # Attempt to find article containers
            articles = soup.find_all('article')
            if not articles:
                # Fallback: Look for divs with common article-related classes
                articles = soup.find_all('div', class_=re.compile(r'(post|article|entry|news|story)', re.I))

            if not articles:
                print(f"No articles found on {url}")
                continue

            for article in articles:
                # Extract the title
                title_tag = article.find(re.compile('h[1-6]'))
                title = title_tag.get_text(strip=True) if title_tag else 'No title found'

                # Extract the link
                link_tag = article.find('a', href=True)
                link = link_tag['href'] if link_tag else 'No link found'

                # Extract the description
                description_tag = article.find('p')
                description = description_tag.get_text(strip=True) if description_tag else 'No description found'

                article_data = {
                    "Page Title": page_title,
                    "Link": link,
                    "Title": title,
                    "Description": description
                }
                results.append(article_data)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching the page {url}: {e}")

    # Display the results
    for result in results:
        print(json.dumps(result, indent=4))
        print('-' * 40)

    # Save the articles to a JSON file
    with open('articles_output.json', 'w', encoding='utf-8') as outfile:
        json.dump(results, outfile, indent=4, ensure_ascii=False)

# Function to load URLs from a JSON file
def load_urls(file_name='urls.json'):
    if os.path.exists(file_name):
        with open(file_name, 'r') as infile:
            urls = json.load(infile)
        return urls
    return []

# Function to save URLs to a JSON file
def save_urls(urls, file_name='urls.json'):
    with open(file_name, 'w') as outfile:
        json.dump(urls, outfile, indent=4)

# Function to allow user to add new URLs
def add_urls():
    urls = load_urls()
    while True:
        url = input("Enter a URL to add (or type 'done' to finish): ")
        if url.lower() == 'done':
            break
        urls.append(url)

    save_urls(urls)
    print("URLs saved successfully.")

# Function to remove a URL
def remove_url():
    urls = load_urls()
    
    if not urls:
        print("No URLs to remove.")
        return

    print("Existing URLs:")
    for index, url in enumerate(urls):
        print(f"{index + 1}. {url}")
    
    try:
        choice = int(input("Enter the number of the URL to remove (or 0 to cancel): "))
        if choice == 0:
            return
        elif 1 <= choice <= len(urls):
            removed_url = urls.pop(choice - 1)
            save_urls(urls)
            print(f"URL '{removed_url}' removed successfully.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input. Please enter a number.")

# Function to delete the JSON file
def delete_json_file(file_name='urls.json'):
    if os.path.exists(file_name):
        os.remove(file_name)
        print(f"'{file_name}' has been deleted.")
    else:
        print(f"'{file_name}' does not exist.")

# Main execution block
if __name__ == "__main__":
    print("Welcome to the article scraper!")

    # Create the JSON file if it doesn't exist
    create_json_file()

    # Check if there are any saved URLs
    urls = load_urls()

    if not urls:
        print("No URLs found. Please add some URLs to get started.")
        add_urls()
        urls = load_urls()

    # Ask if the user wants to add or remove URLs
    choice = input("Do you want to add, remove, or continue with URLs? (add/remove/continue): ").lower()
    
    if choice == 'add':
        add_urls()
        urls = load_urls()
    elif choice == 'remove':
        remove_url()
        urls = load_urls()

    # Fetch articles from the saved URLs
    if urls:
        fetch_articles()
    else:
        print("No URLs to fetch articles from.")
