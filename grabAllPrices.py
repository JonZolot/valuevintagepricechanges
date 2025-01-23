import requests
import os
import json
import pandas as pd
import datetime


#Define upper Price Limit for card search
upperPriceLimit = 30
# Define the directory to save the bulk data files
save_directory = r'C:/Users/Jonat/Documents/Scryfall/bulk-data/'
os.makedirs(save_directory, exist_ok=True)

# URLs to Scryfall's bulk data
bulk_data_url = 'https://api.scryfall.com/bulk-data'

# File paths for the saved bulk data files
all_cards_path = os.path.join(save_directory, 'all_cards.json')
# all_prices_path = os.path.join(save_directory, 'all_prices.json')

def download_and_save(url, path):
    response = requests.get(url)
    with open(path, 'wb') as file:
        file.write(response.content)

# Check if the files already exist, if not, download and save them
if not os.path.exists(all_cards_path):
    # Get the bulk data information
    response = requests.get(bulk_data_url)
    bulk_data = response.json()

    # Find the 'all_cards' and 'all_prices' files URL
    all_cards_url = next((item['download_uri'] for item in bulk_data['data'] if item['type'] == 'all_cards'), None)

    # Download and save the data files
    download_and_save(all_cards_url, all_cards_path)

# Load the data from the saved files
with open(all_cards_path, 'r', encoding="utf-8") as file:
    all_cards = json.load(file)


# Extract card names and USD prices for testing (limit to 10 entries)
cards_and_prices = []
for card in all_cards[:20]:  # Limit to first 10 entries
    if card['prices']['usd'] != None:
        if float(card['prices']['usd']) < upperPriceLimit:
            card_name = card['name']
            usd_price = float(card['prices']['usd'])
            cards_and_prices.append((card_name, usd_price))

# Print results
today = datetime.date.today()
formatted_today = today.strftime("%Y/%m/%d")

# Path to the Excel file
file_path = 'card_table.xlsx'

# Check if the file already exists
if os.path.exists(file_path):
    # Load the existing file into a DataFrame
    cardTable = pd.read_excel(file_path)
    print("Loaded existing data from 'card_table.xlsx'")
else:
    # If the file doesn't exist, create an empty DataFrame
    print("'card_table.xlsx' does not exist. Created a new empty DataFrame")
    empty_table = {
        'Name':[],
        'Price':[],
        'Date':[]
    }
    cardTable = pd.DataFrame(empty_table)


for name, price in cards_and_prices:
    if name in cardTable['Name'].values:
        current_price = cardTable.loc[cardTable['Name'] == name, 'Price'].values[0]
        last_updated_date = cardTable.loc[cardTable['Name'] == name, 'Date'].values[0]
        if price < current_price and formatted_today == last_updated_date :
            cardTable.loc[cardTable['Name'] == name, 'Price'] = price
            cardTable.loc[cardTable['Name'] == name, 'Date'] = formatted_today
        else:
            cardData = pd.DataFrame([{'Name':name, 'Price':price, 'Date':formatted_today}])
            cardTable = pd.concat([cardTable, cardData], ignore_index=True)
    else:      
        cardData = pd.DataFrame([{'Name':name, 'Price':price, 'Date':formatted_today}])
        cardTable = pd.concat([cardTable, cardData], ignore_index=True)

print(cardTable)
cardTable.to_excel('card_table.xlsx', index=False)