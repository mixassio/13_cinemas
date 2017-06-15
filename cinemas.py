import bs4
import re
import requests
import lxml
from kinopoisk.movie import Movie
from urllib.parse import quote

def fetch_afisha_list():
    films_html = requests.get('https://www.afisha.ru/msk/schedule_cinema/')
    soup = bs4.BeautifulSoup(films_html.content, "lxml")
    list_films = []
    for i in soup('h3', {'class': 'usetags'}):
        name_film = i.a.string
        id_film_afisha = re.findall('https://www.afisha.ru/movie/(\d*)', i.a['href'])[0]
        year_film, count_cinema = get_count_schedule_film(id_film_afisha)
        list_films.append({'title': name_film, 'year': year_film, 'count_cinema': count_cinema})
    return list_films



def get_count_schedule_film(id_film):
    url_film_schedule = 'https://www.afisha.ru/msk/schedule_cinema_product/{}/'.format(id_film)
    films_html = requests.get(url_film_schedule)
    soup = bs4.BeautifulSoup(films_html.content, "lxml")
    year_film = re.findall('(\d\d\d\d)', soup('span', {'class': 'creation'})[0].string)[0]
    count_cinema = len(soup.findAll('td', {'class': 'b-td-item'}))
    return year_film, count_cinema


def fetch_idfilm_kp(title_film, year_film):
    url = 'http://www.kinopoisk.ru/s/type/film/find/{}/m_act%5Byear%5D/{}'.format(title_film, year_film)
    response = requests.get(url)
    id_film_kp = re.findall('https://www.kinopoisk.ru/film/(\d*)', response.history[-1].url)
    if id_film_kp:
        return id_film_kp[0]
    else:
        soup = bs4.BeautifulSoup(response.content, "lxml")
        film = soup.findAll('p', {'class': 'pic'})
        if film:
            id_film_kp = re.findall('data-id="(\d*)"', str(film[0]))
            return id_film_kp[0]
        else:
            return None



def get_rating_kp(id_film_kp):
    if id_film_kp is None:
        return 'error', 'error' #Not all movies are on kinopoisk
    url = 'http://www.kinopoisk.ru/rating/{}.xml'.format(id_film_kp)
    raw_xml = requests.get(url).content
    soup = bs4.BeautifulSoup(raw_xml, "lxml")
    count_wiewer = soup('kp_rating')[0]['num_vote']
    rating_kp = soup('kp_rating')[0].string
    return rating_kp, count_wiewer

def output_movies_to_console(movies):
    pass


if __name__ == '__main__':
    list_films = fetch_afisha_list()
    for film in list_films:
        id_film_kp = fetch_idfilm_kp(film['title'], film['year'])
        rating_kp, count_wiewer = get_rating_kp(id_film_kp)
        film['rating_kp'] = rating_kp
        print(film)
    #print(fetch_idfilm_kp('Манифесто', '2015'))
    """id_film_kp = fetch_idfilm_kp(name_film, year_film)
    rating_kp, count_wiewer = get_rating_kp(id_film_kp)
    print(name_film, year_film, count_cinema, id_film_kp, rating_kp)"""