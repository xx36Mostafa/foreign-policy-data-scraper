# Foreign Policy Article Scraper

This Python project automates the process of scraping articles from the Foreign Policy website, storing the data in a SQLite database for later use. The script includes functions to authenticate, retrieve, and save articles with their metadata such as title, date, content, and link.

## Features

- **SQLite Database Integration**: Saves scraped articles with unique IDs and avoids duplicates.
- **Customizable Date Range**: Allows scraping data between specific months and years.
- **Article Filtering**: Filters results based on a specific topic or keyword.
- **Authorization Key Extraction**: Automatically retrieves the required API key for authenticated requests.
- **JSON Export**: Outputs raw API responses to a JSON file for debugging or analysis.

## Requirements

- Python 3.7 or higher
- Required Python libraries:
  - `requests`
  - `sqlite3`
  - `json`
  - `datetime`

Install the required libraries using pip:

```bash
pip install requests
```
## How to Use
- **Step 1**: Clone the Repository
Clone the project to your local machine:
```bash
git clone https://github.com/xx36Mostafa/foreign-policy-scraper.git
cd foreign-policy-scraper
```
- **Step 2**: Configure the Script
Open main.py and configure the scraper settings:

Number of Articles: Specify the number of articles to scrape using the articles parameter.
Date Range: Define the start and end months/years with s_month, e_month, s_year, and e_year.
Topic: Set your topic of interest (e.g., "Gaza").

## Example configuration:
```bash
scraper = scrape_data(s_month=1, e_month=11, s_year=2022, e_year=2024, articles=50)
scraper.get_auth('Gaza')
```

- **Step 3**: Run the Script 
    Execute the script using:
```bash
python main.py
```
The script will fetch articles and store them in articles.db while saving the raw API response to response.json.
