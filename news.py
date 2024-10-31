import requests
from bs4 import BeautifulSoup
import json
import re
import os

# Function to create the JSON file if it doesn't exist
def create_json_file(file_name='urls_and_tags.json'):
    if not os.path.exists(file_name):
        with open(file_name, 'w') as outfile:
            json.dump({"urls": [], "tags": {}}, outfile)  # Initialize with URLs and tags structure
        print(f"'{file_name}' has been created.")

# Function to load URLs and tags from a JSON file
def load_data(file_name='urls_and_tags.json'):
    if os.path.exists(file_name):
        with open(file_name, 'r') as infile:
            data = json.load(infile)
        return data.get("urls", []), data.get("tags", {})
    return [], {}

# Function to save URLs and tags to a JSON file
def save_data(urls, tags, file_name='urls_and_tags.json'):
    with open(file_name, 'w') as outfile:
        json.dump({"urls": urls, "tags": tags}, outfile, indent=4)

# Function to allow user to add new URLs and tags
def add_urls_and_tags():
    urls, tags = load_data()
    
    # Get URLs from user
    while True:
        url = input("Enter a URL to add (or type 'done' to finish): ")
        if url.lower() == 'done':
            break
        urls.append(url)

    # Get tags from user once
    if not tags:
        tags["page_title"] = input("Enter the tag for the page title (e.g., 'title'): ")
        tags["article_title"] = input("Enter the tag for the article title (e.g., 'h1'): ")
        tags["link"] = input("Enter the tag for the article link (e.g., 'a'): ")
        tags["description"] = input("Enter the tag for the description (e.g., 'p'): ")
    
    save_data(urls, tags)
    print("URLs and tags saved successfully.")

# Function to fetch articles using the user-defined tags
def fetch_articles():
    urls, tags = load_data()  # Load URLs and tags from JSON file
    results = []
    
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            # Extract the page title
            page_title_tag = tags.get("page_title", "title")
            page_title = soup.find(page_title_tag).get_text(strip=True) if soup.find(page_title_tag) else 'No title found'

            # Attempt to find article containers
            articles = soup.find_all('article')
            if not articles:
                articles = soup.find_all('div', class_=re.compile(r'(post|article|entry|news|story)', re.I))

            if not articles:
                print(f"No articles found on {url}")
                continue

            for article in articles:
                # Extract the title
                title_tag_name = tags.get("article_title", "h1")
                title_tag = article.find(title_tag_name)
                title = title_tag.get_text(strip=True) if title_tag else 'No title found'

                # Extract the link
                link_tag_name = tags.get("link", "a")
                link_tag = article.find(link_tag_name, href=True)
                link = link_tag['href'] if link_tag else 'No link found'

                # Extract the description
                description_tag_name = tags.get("description", "p")
                description_tag = article.find(description_tag_name)
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

# Main execution block
if __name__ == "__main__":
    print("Welcome to the article scraper!")

    # Create the JSON file if it doesn't exist
    create_json_file()

    # Check if there are any saved URLs and tags
    urls, tags = load_data()

    if not urls:
        print("No URLs found. Please add some URLs and tags to get started.")
        add_urls_and_tags()
        urls, tags = load_data()

    # Ask if the user wants to add URLs and tags
    choice = input("Do you want to add URLs and tags, remove URLs, or continue? (add/remove/continue): ").lower()
    
    if choice == 'add':
        add_urls_and_tags()
        urls, tags = load_data()

    # Fetch articles from the saved URLs using the saved tags
    if urls:
        fetch_articles()
    else:
        print("No URLs to fetch articles from.")
