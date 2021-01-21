import requests
from bs4 import BeautifulSoup

import pandas as pd
import datetime


def _obtener_secciones(url):
    # Generar una solicitud y almacenarla
    p12 = requests.get(url)

    if p12.status_code == 200:

        s = BeautifulSoup(p12.text, 'lxml')

        secciones = s.find('ul', attrs={'class':'horizontal-list main-sections hide-on-dropdown'}).find_all('li')

        links_secciones = [seccion.a.get('href') for seccion in secciones]
    return links_secciones

def _obtener_notas(soup):
    lista_notas = []

    featured_article = soup.find('div', attrs={'class': 'article-item__content'})
    if featured_article:
        try:
            lista_notas.append(featured_article.a.get('href'))
        except Exception as e:
            print('Ocurrió un error, parte A')
            print(featured_article)
            print(e)
            print('\n')

    article_list1 = soup.find_all('h3', attrs={'class': 'title-list'})
    for article in article_list1:
        if article.a:
            try:
                lista_notas.append(article.a.get('href'))
            except Exception as e:
                print('Ocurrió un error, parte B')
                print(article)
                print(e)
                print('\n')

    article_list2 = soup.find_all('h4', attrs={'class': 'title-list'})
    for article in article_list2:
        if article.a:
            try:
                lista_notas.append(article.a.get('href'))
            except Exception as e:
                print('Ocurrió un error, parte C')
                print(article)
                print(e)
                print('\n')

    return lista_notas

def _scrape_nota(url):
    try:
        nota = requests.get(url)
    except Exception as e:
        print('Error scrapeando URL', url)
        print(e)
        return None

    if nota.status_code != 200:
        print(f'Error obteniendo nota {url}')
        print(f'status Code = {nota.status_code}')
        return None
    s_nota = BeautifulSoup(nota.text, 'lxml')

    ret_dict = _obtener_detalles_nota(s_nota)
    ret_dict['url'] = url

    return ret_dict

def _obtener_detalles_nota(soup_nota):

    detalles_nota_dict = {}

    # Extraer la fecha
    fecha_corta = soup_nota.find('span', attrs={'pubdate':'pubdate'}).get('datetime')
    if fecha_corta:
        detalles_nota_dict['fecha'] = fecha_corta
    else:
        detalles_nota_dict['fecha'] = None

    # Extraemos el título
    titulo = soup_nota.find('h1', attrs={'class':'article-title'})
    if titulo:
        detalles_nota_dict['titulo'] = titulo.text
    else:
        detalles_nota_dict['titulo'] = None

    # Extraer la volanta
    volanta = soup_nota.find('h2', attrs={'class':'article-prefix'})
    if volanta:
        detalles_nota_dict['volanta'] = volanta.get_text()
    else:
        detalles_nota_dict['volanta'] = None

    # Extraer el copete o bajada (summary)
    copete = soup_nota.find('div', attrs={'class':'article-summary'})
    if copete:
        detalles_nota_dict['copete'] = copete.get_text()
    else:
        detalles_nota_dict['copete'] = None

    # Extraer el autor
    autor = soup_nota.find('div', attrs={'class':'article-inner'}).find('div', attrs={'class':'article-author'})
    if autor and autor.a:
        detalles_nota_dict['autor'] = autor.a.text
    else:
        detalles_nota_dict['autor'] = None

    media = soup_nota.find('div', attrs={'class':'article-main-media-image'})
    if media:
        imagenes = media.find_all('img')
        if len(imagenes) == 0:
            print('No se encontraron imágenes')
        else:
            imagen = imagenes[-1]
            img_src = imagen.get('data-src')
            try:
                img_req = requests.get(img_src)
                if img_req.status_code == 200:
                    detalles_nota_dict['imagen'] = img_req.content
                else:
                    detalles_nota_dict['imagen'] = None

            except:
                print('No se pudo obtener la imagen')
    else:
        print('No se encontró media')

    # Extraer el cuerpo
    cuerpo = soup_nota.find('div', attrs={'class':'article-text'})
    if cuerpo:
        detalles_nota_dict['cuerpo'] = cuerpo.text
    else:
        detalles_nota_dict['cuerpo'] = None

    return detalles_nota_dict

def _save_data(data):
    now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
    out_file_name = 'Notas_Pagina12.{datetime}.csv'.format(
        datetime=now)

    out_file = './csv_files/{}'.format(out_file_name)

    df = pd.DataFrame(data)
    df.head()

    df.to_csv(out_file)

    return out_file


if __name__ == '__main__':
    notas = []

    links_secciones = _obtener_secciones('https://www.pagina12.com.ar/')
    print(links_secciones)

    for link in links_secciones:
        try:
            r = requests.get(link)
            print('Obteniendo notas de:', link)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'lxml')
                notas.extend(_obtener_notas(soup))
                print('Notas encontradas al momento:', len(notas))
            else:
                print(r.status_code)
                print('No se pudo obtener la seccion', link)

        except:
            print('No se pudo obtener las secciones', link)

    print('Total de Notas encontradas:', len(notas))
    #print('Notas:', notas)

    data = []

    for i, nota in enumerate(notas):
        print(f'Scrapeando nota {i + 1} / {len(notas)}')
        data.append(_scrape_nota(nota))

    #print(data)
    out_file = _save_data(data)
    print('\n')
    print('Data en: ', out_file)
