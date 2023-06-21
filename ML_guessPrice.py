import mysql.connector
from sklearn import tree, preprocessing
import numpy as np
from datetime import datetime
from random import choice, randint
from time import sleep

#-- make a cursor for work with mysql database --
cnx = mysql.connector.connect(user='root', host='127.0.0.1', password='', database='truecar')
cursor = cnx.cursor(buffered=True)


#-- fetch data from database --
cursor.execute('SELECT brand, year, mileage, price FROM cars;')
cnx.commit()

data = cursor.fetchall()
data = np.array(data)
brands = data[: , 0]

#-- prepare data to create a ML model --
le = preprocessing.LabelEncoder()
clf = tree.DecisionTreeClassifier()

brand_coder = le.fit(brands)
brands = brand_coder.transform(brands)

x = []
y = []

#-- add data to x and y list and create sample of input and output --
for i in range(len(data)):
    x.append([brands[i], data[i][1], data[i][2]])
    y.append(data[i][3])

clf = clf.fit(x, y)

#-- function of predicting price --
def price_predictor(brand, year, mileage):
    year = int(year)

    if year > datetime.now().year or len(str(year)) != 4 or type(brand) != str:
        print('You Entered Incorrect Data.')
    
    elif brand not in brand_coder.classes_:
        print('Sorry We Don\'t Support Your Car\'s Model !!!\nOr You Entered Incorrect Data.')

    else:
        brand_code = le.transform([brand])
        brand_code = int(brand_code[0])

        mileage = int(mileage)

        price = clf.predict([[brand_code, year, mileage]])
        price = int(price[0])

        print('Estimated Price Of Your Car (Brand: {} - Year: {} - Mileage: {:,} km) Is About: {:,} $ .'.format(brand, year, mileage, price))


Supported_car = brand_coder.classes_

#-- just for testing function with existing data --

# for i in Supported_car:
#     c = choice(Supported_car)
#     y = randint(2000, 2023)
#     m = randint(0, 500000)

#     price_predictor(c, y, m)
#     sleep(2)

#-- get data from user --
user_car = input("Welcome To \"Car Price Predictor\" !!!\nRemember that you can only use brands that exist in this list.\n{}\nFormat of your input should be like this:\n\'Brand year mileage\'\nPlease Enter Your Data: ".format(Supported_car))
user_car = user_car.strip().split(' ')
price_predictor(user_car[0], user_car[1], user_car[2])