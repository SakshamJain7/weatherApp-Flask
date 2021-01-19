import requests
from flask import Flask,render_template,request,redirect,url_for,flash
from flask_mysqldb import MySQL


app = Flask(__name__)

app.config['DEBUG'] = True
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'weather'
app.config['MYSQL_HOST'] = 'localhost'
app.config['SECRET_KEY'] = 'thisisasecret'

mysql = MySQL(app)

def get_weather_data(City):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ City }&units=metric&appid=028fc6818cfe185e2ab82e92c025e9d8'
    r = requests.get(url).json()
    return r

@app.route('/')
def index_get():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM city")
    datas = cur.fetchall()
    cur.close()

    total_cities = []
    for id,city in datas:
        total_cities.append(city)
    print(total_cities)

    weather_data = []

    for city in total_cities:
        r = get_weather_data(city)

        weather = {
            'city': city,
            'temperature': r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon']
        }

        weather_data.append(weather)
    return render_template('weather.html', weathers = weather_data)


@app.route('/', methods=['POST'])
def index_post():
    error_msg = ''
    new_city = request.form.get('city')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM city")
    data = cur.fetchall()
    cur.close()

    cities = []
    for id,city in data:
        cities.append(city)

    if new_city:

        existing_city = [new_city for c in cities if new_city == c]
        if not existing_city:
            new_city_data = get_weather_data(new_city)

            if new_city_data['cod'] == 200:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO city (cities) VALUES (%s)", (new_city,))
                mysql.connection.commit()
            else:
                error_msg = 'City not existed in the world!'
        else:
            error_msg = "City Already Existed in database!"

    if error_msg:
        flash(error_msg,'error')
    else:
        flash('City successfully added.')

    return redirect(url_for('index_get'))


@app.route('/delete/<city>')
def delete(city):

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM city")
    data = cur.fetchall()
    cur.close()
    all_cities = []
    for id, cities in data:
        all_cities.append(cities)

    for c in all_cities:
        if city == c:
            cur = mysql.connection.cursor()
            cur.execute('DELETE FROM city WHERE cities = %s', (city,))
            mysql.connection.commit()

    flash(f'Successfully deleted {city}','success')
    return redirect(url_for('index_get'))

if __name__ == '__main__':
    app.run()
