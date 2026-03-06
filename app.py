from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# ✅ OpenWeatherMap API details
API_KEY = "803f77a96502ec00149f4b07055e5dd5"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


@app.route('/')
def index():
    """Home page to enter city name"""
    return render_template('index.html')


@app.route('/weather', methods=['POST'])
def weather():
    """Fetch and display weather information for the entered city"""
    city = request.form.get('city', '').strip()

    if not city:
        return render_template('result.html', error="⚠️ Please enter a city name.", weather=None)

    try:
        # Call OpenWeatherMap API
        params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        # Handle invalid city or API issues
        if data.get('cod') != 200:
            message = data.get('message', 'City not found!')
            return render_template('result.html', error=message.capitalize(), weather=None)

        # Extract weather details
        weather_data = {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': round(data['main']['temp'], 1),
            'description': data['weather'][0]['description'].title(),
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed']
        }

        return render_template('result.html', weather=weather_data, error=None)

    except Exception as e:
        return render_template('result.html', error=f"❌ Error: {str(e)}", weather=None)


if __name__ == '__main__':
    # Run app on all interfaces (important for EC2/Jenkins)
    app.run(host='0.0.0.0', port=5000, debug=True)
