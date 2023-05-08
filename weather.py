import argparse
import json
import sys
from configparser import ConfigParser
from urllib import error, parse, request

import style

BASE_WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather" 

THUNDERSTORM = range(200, 300)
DRIZZLE = range(300, 400)
RAIN = range(500, 600)
SNOW = range(600, 700)
ATMOSPHERE = range(700, 800)
CLEAR = range(800, 801)
CLOUDY = range(801, 900)


def read_user_cli_args():
    parser = argparse.ArgumentParser(
        description="gets weather and temperature information for a city"
    )
    parser.add_argument(
        "city", nargs = "+", type = str, help = "enter the city name"
    )
    parser.add_argument(
        "-i",
        "--imperial",
        action = "store_true",
        help = "display the temperature in imperial units",
    )
    return parser.parse_args()


def build_weather_query (city_input, imperial=False):
    api_key = _get_api_key()
    city_name = " ".join(city_input)
    url_encoded_city_name = parse.quote_plus(city_name)
    units = "imperial" if imperial else "metric"
    url = (
        f"{BASE_WEATHER_API_URL}?q={url_encoded_city_name}"
        f"&units={units}&appid={api_key}"
    )
    return url
    

def _get_api_key():
    config = ConfigParser()
    config.read("secrets.ini")
    return config["openweather"]["api_key"]


def get_weather_data(query_url):
    try:
        response = request.urlopen(query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:
            sys.exit("Access denied. Check your API key.")
        elif http_error.code == 404:  # 404 - Not Found
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong... ({http_error.code})")
            
    data = response.read()
    
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the response from the server.")
        
    
def display_weather_info(weather_data, imperial=False):
    city = weather_data ["name"]
    weather_id = weather_data["weather"][0]["id"]
    weather_description = weather_data ["weather"][0]["description"]
    temperature = weather_data ["main"]["temp"]
    
    style.change_color(style.REVERSE)
    print(f"{city:^{style.PADDING}}", end="")
    style.change_color(style.RESET)

    weather_symbol, color = _select_weather_display_params(weather_id)
    style.change_color(color)

    print(f"\t{weather_symbol}", end=" ")
    print(
        f"\t{weather_description.capitalize():^{style.PADDING}}",
        end=" ",
    )
    style.change_color(style.RESET)

    print(f"({temperature}°{'F' if imperial else 'C'})")


def _select_weather_display_params(weather_id):
    if weather_id in THUNDERSTORM:
        display_params = ("💥", style.RED)
    elif weather_id in DRIZZLE:
        display_params = ("💧", style.CYAN)
    elif weather_id in RAIN:
        display_params = ("💦", style.BLUE)
    elif weather_id in SNOW:
        display_params = ("⛄️", style.WHITE)
    elif weather_id in ATMOSPHERE:
        display_params = ("🌀", style.BLUE)
    elif weather_id in CLEAR:
        display_params = ("🔆", style.YELLOW)
    elif weather_id in CLOUDY:
        display_params = ("💨", style.WHITE)
    else:  # In case the API adds new weather codes
        display_params = ("🌈", style.RESET)
    return display_params


if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = build_weather_query(user_args.city, user_args.imperial)
    weather_data = get_weather_data(query_url)
    display_weather_info(weather_data, user_args.imperial)
