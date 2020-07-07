from pprint import pprint
import requests
import json


def get_photo_api(id, Token):
    result = requests.get('https://api.vk.com/method/photos.getAll',
                            params={
                                'access_token': Token,
                                'owner_id': id,
                                'album_id': 'profile',
                                'extended': 50,
                                'v': 5.77
                            })
    return result

def get_photo(Token, id, name, **kwargs):
    get_photos = get_photo_api(id, Token)

    photo = get_photos.json()
    id_user_vk = f'https://vk.com/id{id}'
    #pprint(photo)

    title = kwargs
    data_like = []
    try:
        for number in photo['response']['items']:
            like = number['likes']['count']
            size = number['sizes'][-1]['url']
            # print(like)
            # print(size)
            data = (like, size, id_user_vk)
            data_like.append(data)
    except KeyError:
        data_like.append((0, 'Доступ запрещен', id_user_vk))


    #print(data_like)
    sorted_data = sorted(data_like)
    sorted_data.reverse()
    i = 0
    list_photo = []
    try:
        while i < 3:
            # print(sorted_data[i])
            element = sorted_data[i]
            list_photo.append(element)
            i += 1

    except IndexError:
        list_photo.append([])

    for m, n in title.items():
        if m == 'save':
            save = n

    if len(list_photo) == 3 and save == "Сохранить":
        save_photo(list_photo, name)

    return list_photo


def save_photo(list_photo, name):
    number = 1
    for load in list_photo:
        try:
            p = requests.get(load[1])
            if number < 4:
                person = f'{name}_photo_{number}_{load[1].split("/")[-1]}'
                with open('file/%s' % person, 'wb') as fd:
                    fd.write(p.content)
                if number != 3:
                    number += 1
                else:
                    number = 1
        except IndexError:
            continue

