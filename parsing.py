import requests
from bs4 import BeautifulSoup
from database import create_tables, insert_stops, insert_schedule


url = 'https://avtosib-372-375.ru/'


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}
response = requests.get(url, headers=headers)
response.raise_for_status()


soup = BeautifulSoup(response.text, 'html.parser')


table = soup.find('table')

if table:

    stops = [cell.get_text(strip=True) for cell in table.find_all('tr')[0].find_all('td')]


    schedule = []
    for row in table.find_all('tr')[1:]:
        times = [cell.get_text(strip=True) for cell in row.find_all('td')]
        schedule.append(times)

    create_tables()

    insert_stops(stops)

    insert_schedule(schedule)

else:
    print(" Таблица с расписанием не найдена")
