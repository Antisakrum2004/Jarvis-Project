import requests
from datetime import datetime

def fetch_currency_rates():
    # URL API ЦБ РФ для получения курсов валют
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    
    try:
        # Отправляем GET-запрос
        response = requests.get(url)
        response.raise_for_status()  # Проверяем на ошибки
        
        # Парсим JSON-ответ
        data = response.json()
        usd_rate = data["Valute"]["USD"]["Value"]
        eur_rate = data["Valute"]["EUR"]["Value"]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Формируем результат
        result = {
            "date": date,
            "USD": usd_rate,
            "EUR": eur_rate
        }
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return None

if __name__ == "__main__":
    rates = fetch_currency_rates()
    if rates:
        print(f"Курсы валют на {rates['date']}:")
        print(f"USD: {rates['USD']} руб.")
        print(f"EUR: {rates['EUR']} руб.")
    else:
        print("Не удалось получить курсы валют.")