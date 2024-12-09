from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = 'oPj9W6iVIJRsa6fqPQ5o1zHA1Xe6k6WP'

def retrieve_weather_data(city_list, api_key):
    result_data = []
    for city in city_list:
        location_key = get_location_key(city, api_key)
        if location_key:
            forecast = get_forecast(location_key, api_key)
            if forecast:
                forecast['city'] = city
                result_data.append(forecast)
    return result_data

def get_location_key(city_name, api_key):
    endpoint = "http://dataservice.accuweather.com/locations/v1/cities/search"
    parameters = {'apikey': api_key, 'q': city_name}
    response = requests.get(endpoint, params=parameters)
    if response.status_code == 200 and response.json():
        return response.json()[0].get('Key')
    print(f"Ошибка: Город {city_name} не найден или не удалось получить данные.")
    return None

def get_forecast(location_key, api_key):
    forecast_endpoint = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
    params = {'apikey': api_key, 'metric': True, 'details': True}
    response = requests.get(forecast_endpoint, params=params)
    if response.status_code == 200:
        daily_data = response.json().get('DailyForecasts', [{}])[0]
        return {
            'temperature': daily_data.get('Temperature', {}).get('Maximum', {}).get('Value', 0),
            'wind_speed': round(daily_data.get('Day', {}).get('Wind', {}).get('Speed', {}).get('Value', 0) * 0.27778, 2),
            'precipitation_probability': daily_data.get('Day', {}).get('PrecipitationProbability', 0)
        }
    print(f"Ошибка: Не удалось получить прогноз для ключа {location_key}.")
    return None

def evaluate_weather_conditions(forecast):
    weather_issues = []
    if forecast['temperature'] < 0:
        weather_issues.append("низкая температура")
    elif forecast['temperature'] > 30:
        weather_issues.append("высокая температура")
    if forecast['wind_speed'] > 40:
        weather_issues.append("сильный ветер")
    if forecast['precipitation_probability'] > 50:
        weather_issues.append("вероятны осадки")
    return weather_issues

@app.route('/', methods=['GET', 'POST'])
def homepage():
    weather_results = []
    error = None
    if request.method == 'POST':
        first_city = request.form.get('city1')
        second_city = request.form.get('city2')
        if first_city and second_city:
            cities = [first_city.strip(), second_city.strip()]
            weather_results = retrieve_weather_data(cities, API_KEY)
            for result in weather_results:
                issues = evaluate_weather_conditions(result)
                result['condition'] = "Неблагоприятная погода: " + ", ".join(issues) if issues else "Благоприятная погода"
        else:
            error = 'Введите оба города.'
    return render_template('index.html', weather_info=weather_results, error_message=error)

if __name__ == '__main__':
    app.run(debug=True)
