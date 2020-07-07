import json
import requests
import time
from pprint import pprint
from pymongo import MongoClient
import pymongo
from additional_api_functions import get_photo
from urllib.parse import urlencode

APP_ID = 7523772
OAUTH_URL = 'https://oauth.vk.com/authorize'
OAUTH_PARAMS = {
    'client_id': APP_ID,
    'scope': 'friends,photos,audio,status,groups',
    'display': 'page',
    'v': '5.52',
    'response_type': 'token'
}



class Find_couple():

    def __init__(self):
        self.information = []
        self.id_list = []
        self.Token = '67c3fbfa8cd925119ee6eae8a9c2941f70318428afa8b3d540d277af55e6651b2d00c17ed251c5ea237ca'
        client = MongoClient()
        # выбираем базу данных
        db = client.db_course
        # выбираем коллекцию документов
        self.collection_users = db.test_collection

    def main_information(self, id):
        """Получение информации о пользователе"""
        main = requests.get('https://api.vk.com/method/users.get',
                                    params={
                                        'access_token': self.Token,
                                        'user_ids': id,
                                        'fields': 'universities, music, movies, group, country, relation, bdate, city, photo_max_orig, screen_name,sex, photo_id',
                                        'v': 5.122
                                    })

        my_information = main.json()
        try:
            date = my_information['response'][0]
        except KeyError:
            print("Проблема с токеном")
            print("Пройдите по ссылке и обновите токен")
            print('?'.join((OAUTH_URL, urlencode(OAUTH_PARAMS))))
            raise SystemExit(1)
        if 'country' in date.keys() and date['country']['title']:
            self.country_utilizer = date['country']['title']
        else:
            self.country_utilizer = "Россия"

        if 'city' in date.keys() and date['city']['title']:
            self.city_utilizer = date['city']['title']
        else:
            self.city_utilizer = "Москва"

        # возраст
        if 'bdate' in date.keys() and len(date['bdate']) >= 7:
            self.year_utilizer = f'{date["bdate"][-4:-1]}{date["bdate"][-1]}'
        else:
            self.year_utilizer = input("Введите год своего рождения")
        self.sex_utulizer = date['sex']
        print(f' Пол: {self.sex_utulizer} \n Страна: {self.country_utilizer} \n Город: {self.city_utilizer} \n Год рождения: {self.year_utilizer}')
        try:
            # университет
            if 'universities' in date.keys():
                self.universities_utilizer = date['universities'][0]['name']
        except IndexError:
            self.universities_utilizer = "Не указан"

        try:
            # любимая музыка
            self.music_utilizer = date['music']
        except IndexError:
            self.music_utilizer = "Не указан"

        try:
            # любымые фильмы
            self.movies_utulizer = date['movies']
        except IndexError:
            self.movies_utulizer = "Не указан"

        return self.sex_utulizer, self.country_utilizer, self.city_utilizer, self.year_utilizer, self.universities_utilizer, self.music_utilizer, self.movies_utulizer

    def loading_random_users(self):
        """ Сбор данных о людях """
        count = 0
        while count < 25:
            self.random_users = requests.get('https://api.vk.com/method/users.search',
                                             params={
                                                 'access_token': self.Token,
                                                 'count': 100,
                                                 'fields': 'universities, music, movies, country, relation, bdate, city, photo_max_orig, screen_name,sex, photo_id',
                                                 'v': 5.103
                                             })

            self.list_users = self.random_users.json()
            #pprint(self.list_users)
            date = self.list_users['response']['items']
            for item in date:
                if 'country' in item.keys():
                    pass
                else:
                    item['country'] = {'title': 'Нет'}
                if 'city' in item.keys():
                    pass
                else:
                    item['city'] = {'title': 'Нет'}
                if 'bdate' in item.keys():
                    if len(item['bdate']) > 6:
                        year = f'{item["bdate"][-4:-1]}{item["bdate"][-1]}'
                        item['bdate'] = year
                    else:
                        item['bdate'] = 'Нет'
                else:
                    item['bdate'] = 'Нет'

                # дополнительная информация
                if 'universities' in item.keys():
                    if item['universities'] != []:
                        item['universities'] = item['universities'][0]['name']
                    else:
                        item['universities'] = 'Нет'
                else:
                    item['universities'] = 'Нет'
                if 'music' in item.keys():
                    pass
                else:
                    item['music'] = 'Нет'
                if 'movies' in item.keys():
                    pass
                else:
                    item['movies'] = 'Нет'

                user = {'first_name': item['first_name'], 'last_name': item['last_name'], 'id': item['id'],
                        'city':item['city']['title'], 'sex':item['sex'],'music': item['music'],'movies': item['movies'],
                        'country': item['country']['title'], 'year': item['bdate'], 'universities': item['universities'] }
                #print(user)

                if user['id'] not in self.id_list:
                    self.id_list.append(user['id'])
                    self.information.append(user)
                else:
                    continue
            time.sleep(0.6)

            count += 1

        print(len(self.information))
        return  self.information


    # Запись в базу данных
    def write_db(self):
        """ Добавляем индекс уникальности для исключения повторений"""
        self.collection_users.create_index([('id', pymongo.ASCENDING)], unique=True)
        for part in self.information:
            try:
                self.post_id = self.collection_users.insert_one(part)
            except:
                continue

    def find_index(self):
        """ Выявление совместимости """
        if self.sex_utulizer == 2:
            #self.collection_users.find().sort([("sex", 1)])
            for people in self.collection_users.find({"sex": 1}):

                index = 0
                # Проверка возраста
                if people['year'] != 'Нет':
                    if (int(1997) - int(people['year'])) <= 3:
                        index += 25
                    elif 3 < (int(self.year_utilizer) - int(people['year'])) <= 6:
                        index += 10
                    else:
                        index -= 30
                # Проверка на совместимость
                if self.city_utilizer == people['city']:
                    index += 10
                if self.universities_utilizer == people['universities'] and people['universities'] != 'Нет':
                    index += 20
                if self.music_utilizer == people['music'] and people['music'] != 'Нет':
                    index += 20
                if self.movies_utulizer == people['movies'] and people['movies'] != 'Нет':
                    index += 20
                if self.country_utilizer == people['country']:
                    index += 5
                #print(people['first_name'], index)
                self.collection_users.update_one({'first_name': people['first_name']}, {"$set": {"index": index}})
                self.collection_users.update_one({'first_name': people['first_name']}, {"$set": {"repetition": False}})

    def top_couple(self, assigment='Нет'):
        """ Добавление фотографий юзерам в базу данных """
        top_list = self.collection_users.find({"repetition": {'$eq': False}}).sort([("index", -1)]).limit(10)
        print('Результат поиска \n')
        for user in top_list:
            photo = get_photo(self.Token, user['id'], user['first_name'], save=assigment)
            self.collection_users.update_one({'first_name': user['first_name']}, {"$set": {"photo": photo}})
            self.collection_users.update_one({'first_name': user['first_name']}, {"$set": {"vk": photo[0][2]}})

        top_list_whith_photo = self.collection_users.find({"repetition": {'$eq': False}}).sort([("index", -1)]).limit(10)

        # запись в JSON
        with open('output_information.json', 'w', encoding='utf-8') as files:
            users = []
            for user in top_list_whith_photo:
                self.collection_users.update_one({'first_name': user['first_name']}, {"$set": {"repetition": True}})
                information = {'first_name': user['first_name'],
                        'last_name': user['last_name'],
                        'link': f'https://vk.com/id{user["id"]}',
                        'photo': user['photo']
                        }
                print(information)
                users.append(information)
            json.dump(users, files, indent=4, ensure_ascii=False)
        print("Результаты записаны в JSON файл")
        act = input("Устраивает ли вас набор вариантов? Попробовать поискать еще с новыми вариантами?")
        if act in ['Да', 'да']:
            self.top_couple()


    # Удаление всего
    def delate_all(self):
        self.collection_users.delete_many({})

if __name__ == "__main__":

    one = Find_couple()
    one.delate_all()
    print("Получение информации о искателе")
    one.main_information(108889917)

    # получение информации о людях
    one.loading_random_users()

    # запись в базу данных
    one.write_db()
    # присвоение балла совместимости
    one.find_index()
    # загрузка фотографий и запись в JSON файл и скачивание фотографий если передать в функцию "Сохранить"
    one.top_couple("Сохранить")
