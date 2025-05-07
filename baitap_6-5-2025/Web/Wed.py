from flask import Flask, render_template
import requests
import json

app = Flask(__name__)

# API URLs
GOLD_API_URL = 'https://www.metals-api.com/api/latest?base=USD'  # Không sử dụng vì không có access_key
WEATHER_API_URL = 'https://api.open-meteo.com/v1/forecast?latitude=21.0285&longitude=105.8542&current_weather=true'
CURRENCY_API_URL = 'https://v6.exchangerate-api.com/v6/10847939a53a6ec288583b1c/latest/USD'

# Dữ liệu mẫu cố định (chỉ cho giá vàng)
GOLD_PRICE = 3409.30  # USD/ounce

# Ánh xạ weathercode thành mô tả thời tiết (theo chuẩn WMO)
WEATHER_CODES = {
    0: "Trời quang",
    1: "Chủ yếu quang đãng",
    2: "Có mây một phần",
    3: "Nhiều mây",
    45: "Sương mù",
    48: "Sương mù đóng băng",
    51: "Mưa phùn nhẹ",
    53: "Mưa phùn vừa",
    55: "Mưa phùn dày",
    61: "Mưa nhẹ",
    63: "Mưa vừa",
    65: "Mưa to",
    71: "Tuyết rơi nhẹ",
    73: "Tuyết rơi vừa",
    75: "Tuyết rơi dày",
    95: "Giông bão",
}

@app.route('/')
def index():
    # Khởi tạo dữ liệu mặc định
    gold = {'rates': {'USD': GOLD_PRICE}}  # Dùng dữ liệu mẫu vì không có access_key
    weather = {'name': 'Hà Nội', 'weather': [{'description': 'N/A'}], 'current_weather': {'temperature': 'N/A'}}
    currency = {'rates': {'VND': 'N/A'}}
    gold_history = {
        'years': [2019, 2020, 2021, 2022, 2023, 2024],
        'prices': [1500, 1700, 1800, 1900, 2000, GOLD_PRICE]
    }
    error = None

    try:
        # Lấy dữ liệu thời tiết từ Open-Meteo API
        weather_response = requests.get(WEATHER_API_URL)
        print("Weather API Response Status:", weather_response.status_code)
        print("Weather API Response Data:", weather_response.text)  # In dữ liệu thô để kiểm tra
        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            print("Weather Data Parsed:", weather_data)  # In dữ liệu đã parse để kiểm tra
            if 'current_weather' in weather_data:
                weather_code = weather_data['current_weather'].get('weathercode', 0)
                weather_temp = weather_data['current_weather'].get('temperature', 'N/A')
                weather = {
                    'name': 'Hà Nội',
                    'weather': [{'description': WEATHER_CODES.get(weather_code, "Không xác định")}],
                    'current_weather': {'temperature': weather_temp}
                }
            else:
                error = "Dữ liệu thời tiết không đúng định dạng: 'current_weather' không tồn tại"
        else:
            error = f"Không thể lấy dữ liệu thời tiết từ API. Status code: {weather_response.status_code}"

        # Lấy dữ liệu tỷ giá từ ExchangeRate-API
        currency_response = requests.get(CURRENCY_API_URL)
        print("Currency API Response Status:", currency_response.status_code)
        print("Currency API Response Data:", currency_response.text)  # In dữ liệu thô để kiểm tra
        if currency_response.status_code == 200:
            currency_data = currency_response.json()
            print("Currency Data Parsed:", currency_data)  # In dữ liệu đã parse để kiểm tra
            if 'conversion_rates' in currency_data and 'VND' in currency_data['conversion_rates']:
                currency = {'rates': {'VND': currency_data['conversion_rates']['VND']}}
            else:
                error = error or "Dữ liệu tỷ giá không đúng định dạng: 'conversion_rates' hoặc 'VND' không tồn tại"
        else:
            error = error or f"Không thể lấy dữ liệu tỷ giá từ API. Status code: {currency_response.status_code}"

    except Exception as e:
        error = f"Lỗi: {str(e)}"

    return render_template('index.html', gold=gold, weather=weather, currency=currency, gold_history=json.dumps(gold_history), error=error)

if __name__ == '__main__':
    app.run(debug=True)