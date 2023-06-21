import requests
from bs4 import BeautifulSoup
import mysql.connector
import re
from time import sleep

#----------------------------------- make a cursor for work with mysql database -------------------------------

cnx = mysql.connector.connect(user = 'root',password = '', host = '127.0.0.1')
cursor = cnx.cursor()

#----------------------------------- create db and table if not exist -----------------------------------------

cursor.execute('CREATE DATABASE IF NOT EXISTS truecar;')
cursor.execute('use truecar;')
cursor.execute('CREATE TABLE IF NOT EXISTS cars (id int not null auto_increment primary key, brand varchar(255) not null, model varchar(255), year int(10), mileage int(10), price int(20));')


c = 1

#----------------------------------- extracting data from website with bs4 -----------------------------------------

for page in range(1, 10):
    print('page: ', page)
    req = requests.get('https://www.truecar.com/used-cars-for-sale/listings/?page=%i' %(page))

    while req.status_code != 200:
        req = requests.get('https://www.truecar.com/used-cars-for-sale/listings/?page=%i' %(page))
        sleep(2)

    soup = BeautifulSoup(req.text, 'html.parser')
    cars = soup.find_all("div", class_ = "vehicle-card-body")


    for car in cars:
        # --------- brand and model ----------
        name = car.find("span", class_ = "truncate")

        if name == None or type(name) == 'NoneType':
            continue
        else:
            name = name.text.split(' ')
            brand = name[0]
            model = '-'.join(name[1:])

        # --------- year ----------
        year = car.find("span", class_ = "vehicle-card-year")
        if year.text != None or type(year.text) != 'NoneType':
            year = int(year.text)
        else:
            year = None

        # --------- mileage ----------
        mileage = car.find("div", attrs={'data-test':"vehicleMileage"})
        mileage = mileage.text.strip().split(' ')

        if type(mileage[0]) == 'NoneType' or mileage[0] == None:
            mileage_km = None

        else:
            mileage_km = int(mileage[0].replace(',', ''))

            if mileage[1] == 'miles':
                mileage_km = int(mileage_km * 1.6)
            

        # --------- price ----------
        price = car.find("div", class_ = "heading-3")
        if type(price) == 'NoneType' or price == None:
            car_price = None
        else:
            price = price.text.split('$')
            new_price = [int(re.sub('[\$\,]', '', i)) for i in price[1:]]
            car_price = int(sum(new_price) / len(new_price))


        #------------------------------- store scraped data into database -------------------------------------

        if year != None and mileage_km != None and car_price != None:
            cursor.execute('INSERT IGNORE INTO cars (brand, model, year, mileage, price) values (\'%s\', \'%s\', %i, %i, %i);' % (brand, model, year, mileage_km, car_price))
            # print('({} - {}) made in year ({}) and mileage is ({} km) with price of just ({} $).\n'.format(brand, model, year, mileage_km, car_price))
        if c % 100 == 0:
            cnx.commit()
        if c == 500:
            break
        else:
            c += 1
            # sleep(1.5)

cursor.execute('DELETE a FROM cars AS a, cars AS b WHERE (a.id < b.id) AND (a.model = b.model) AND (a.mileage = b.mileage) AND (a.price = b.price) AND (a.year = b.year);')
cnx.commit()
cnx.close()

        
