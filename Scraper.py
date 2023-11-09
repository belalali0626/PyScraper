from bs4 import BeautifulSoup
import requests

url = 'https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population'

page = requests.get(url)

soup = BeautifulSoup(page.text, 'html.parser')

table = soup.find('table', {'class': 'nowraplinks mw-collapsible autocollapse navbox-inner'})
list_items = table.find_all('li')

header = soup.find('tr', {'is-sticky'})
list_header = header.find_all('')

# Extract and print the country names
countries = [item.a.text for item in list_items if item.a]
headers = [item.a.text for item in list_header if item.a]

print(countries)
print(header)

print(headers)

# countries = soup.find('table',class_='nowraplinks mw-collapsible autocollapse navbox-inner')
#countries_titles = [title.text.strip() for title in countries]







