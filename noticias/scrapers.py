from .models import Noticia, Fuente
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime 
from googletrans import Translator
from datetime import datetime
import urllib3
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_ukrinform():
    # Define la URL de la página principal que se va a analizar
    main_page_url = "https://www.ukrinform.es/rubric-ato"

    # Crea un objeto PoolManager de urllib3 para manejar las solicitudes HTTP
    req = urllib3.PoolManager()

    # Realiza una solicitud GET a la URL de la página principal y guarda la respuesta en la variable res
    res = req.request('GET', main_page_url)

    # Utiliza BeautifulSoup para analizar el HTML de la respuesta y crea un objeto soup que representa la estructura del documento HTML
    soup = BeautifulSoup(res.data, 'html.parser')

    # Busca el primer elemento <div> con la clase 'rest' en el documento HTML analizado y guarda el resultado en primer_articulo
    primer_articulo = soup.find('div', class_='rest')

    # Comienza un bloque condicional para verificar si se encontró el primer artículo
    if primer_articulo:
        # Encontrar la etiqueta img dentro del div 'rest'
        img_tag = primer_articulo.find("img")

        # Verificar si se encontró la etiqueta img
        if img_tag:
            # Obtener la URL de la imagen desde el atributo src
            urlimagen = img_tag["src"]

        # Si se encuentra el primer artículo, busca el enlace dentro de ese artículo y lo imprime
        enlace_articulo = primer_articulo.find('a')['href']

        # Crea la URL completa del nuevo artículo utilizando el enlace encontrado
        enlace = 'https://www.ukrinform.es{}'.format(enlace_articulo)

        # Realiza una nueva solicitud GET a la URL del nuevo artículo y crea una nueva sopa para analizar el HTML de la página del nuevo artículo
        res_new = req.request('GET', enlace)
        soup_new = BeautifulSoup(res_new.data, 'html.parser')

        # Extraer los datos del artículo
        nfuente = soup_new.find('div', class_='newsPublisher').text.strip()
        titular = soup_new.find('h1', class_='newsTitle').text.strip()

        cadena = "Redacción de Ukrinform"
        autores = ''.join(caracter for caracter in cadena if caracter.isalnum() or caracter.isspace())

        # Encuentra todos los elementos <p> con el estilo "text-align: justify;"
        contenidos = soup_new.find_all('p', style='text-align: justify;')
        contenido_texto = [contenido.get_text(strip=True) for contenido in contenidos]

        # Captura la fecha y hora actual como fecha y hora de extracción del hecho noticiable
        fextraccion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Comprueba si la noticia ya existe en la base de datos antes de guardarla
    if Noticia.objects.filter(titular=titular).exists():
        print('La noticia ya existe en la base de datos')
    else:
        nueva_noticia = Noticia.objects.create(
            urlimagen=urlimagen,
            enlace=enlace,
            titular=titular,
            autores=autores,
            contenido='\n'.join(contenido_texto),
            fextraccion=fextraccion
        )

        # Crea una nueva instancia del modelo Fuente y almacena la fuente en ella
        nueva_fuente = Fuente.objects.create(
            nfuente=nfuente,
            noticia=nueva_noticia
        )

        # Guarda ambas instancias en la base de datos
        nueva_noticia.save()
        nueva_fuente.save()

def scrape_bbc():
    try:
        # Configura el controlador del navegador (asegúrate de tener el controlador adecuado instalado, por ejemplo, Chromedriver)
        driver = webdriver.Chrome()

        # Abre la página web
        driver.get("https://www.bbc.com/news/war-in-ukraine")

        # Espera hasta que el botón close esté presente
        close_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "close-button"))
        )

        # Haz clic en el botón close después de esperar 10 segundos
        close_button.click()

        # Encuentra el enlace utilizando XPath
        enlace = driver.find_element(By.XPATH, '/html/body/div[2]/main/article/section[1]/div/div[2]/div[1]/div/div/div[1]/a').get_attribute("href")

        if "live" in enlace:
            # Si "live" está presente en el enlace, cierra el driver y finaliza la función
            driver.quit()
            return
        
        # Encontrar el elemento de la imagen por su XPath
        image_element = driver.find_element(By.XPATH, '/html/body/div[2]/main/article/section[1]/div/div[2]/div[1]/div/div/div[1]/a/div/div[1]/div/div/img')

        # Obtener el atributo src de la etiqueta img
        urlimagen = image_element.get_attribute("src")
        
        primer_articulo = driver.find_element(By.XPATH, '/html/body/div[2]/main/article/section[1]/div/div[2]/div[1]/div/div/div[1]/a')
        primer_articulo.click()
        
        # Encuentra y procesa la información sobre los autores del artículo
        autors_element = driver.find_element(By.XPATH, '/html/body/div[2]/main/section[2]/div/div[1]/div[2]/div/span[1]')
        if autors_element:
            autores = autors_element.text
        else:
            autores = "Redacción de BBC"
            # Encuentra el elemento que contiene los autores utilizando WebDriverWait si es necesario
        autores_element = autors_element
        if not autores_element:
            autores_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, autors_element))
            )
        autores_text = autores_element.text
        autores_sin_by = autores_text.replace("By ", "")
        lista_autores = autores_sin_by.split(" & ")
        autores = ', '.join(lista_autores)
        autores = autores.rstrip(',')
        autores = autores.replace(" and ", ", ")  # Reemplaza "and" por ","
                
        # Encuentra y traduce el titular del artículo
        title_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/main/section[1]/h1'))
        )
        title = title_element.text
        traductor = Translator()
        titular = traductor.translate(title, dest='es').text

        # Encuentra y procesa la información sobre la fuente del artículo
        fuente = driver.find_element(By.XPATH, '/html/body/div[2]/main/footer/section[1]/nav/ul/li[11]/div/a').text
        segunda_parte = fuente.split('BBC', 1)[-1].strip()
        nfuente = fuente.replace(segunda_parte, "", 1).strip()

        # Encuentra y traduce el contenido del artículo
        contents = driver.find_elements(By.XPATH, '//section[@data-component="text-block"]')
        # Excluir el primer elemento de la lista
        contents = contents[1:]
        contenidos = [traductor.translate(content.text, dest='es').text for content in contents]

        # Obtiene la fecha y hora de extracción del artículo
        fextraccion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Comprueba si la noticia ya existe en la base de datos antes de guardarla
        if Noticia.objects.filter(titular=titular).exists():
            print('La noticia ya existe en la base de datos')
        else:
            nueva_noticia = Noticia.objects.create(
                urlimagen=urlimagen,
                enlace=enlace,
                titular=titular,
                autores=autores,
                contenido='\n'.join(contenidos),
                fextraccion=fextraccion
            )

            # Crea una nueva instancia del modelo Fuente y almacena la fuente en ella
            nueva_fuente = Fuente.objects.create(
                nfuente=nfuente,
                noticia=nueva_noticia
            )

            # Guarda ambas instancias en la base de datos
            nueva_noticia.save()
            nueva_fuente.save()
            
    except Exception as e:
        print("Ocurrió un error:", e)
        # En caso de error, asegúrate de cerrar el navegador
        driver.quit()

def scrape_cnn():

    # Define la URL de la página principal que se va a analizar
    main_page_url = "https://cnnespanol.cnn.com/tag/guerra-en-ucrania/"

    # Crea un objeto PoolManager de urllib3 para manejar las solicitudes HTTP
    req = urllib3.PoolManager()

    # Realiza una solicitud GET a la URL de la página principal y guarda la respuesta en la variable res
    res = req.request('GET', main_page_url)

    # Utiliza BeautifulSoup para analizar el HTML de la respuesta y crea un objeto soup que representa la estructura del documento HTML
    soup = BeautifulSoup(res.data, 'html.parser')

    primer_articulo = soup.find('div', class_='news__data')

    if primer_articulo:
        enlace = primer_articulo.find('a')['href']
        
        if 'video' not in enlace:
            new_page_url = '{}'.format(enlace)
            res_new = req.request('GET', new_page_url)
            soup_new = BeautifulSoup(res_new.data, 'html.parser')

            # Encontrar el div con la clase 'news__media'
            div_news_media = soup.find("div", class_="news__media")

            # Verificar si se encontró el div 'news__media'
            if div_news_media:
                # Encontrar la etiqueta img dentro del div 'news__media' con la clase 'image'
                img_tag = div_news_media.find("img", class_="image")

                # Verificar si se encontró la etiqueta img
                if img_tag:
                    # Obtener la URL de la imagen desde el atributo src
                    urlimagen = img_tag["data-lazy-src"]
            
            nfuente = 'CNN Español'
            titular = soup_new.find('h1', class_='storyfull__title').text.strip()
            
            autores_texto = soup_new.find('p', class_='storyfull__authors')
            if autores_texto:
                autores_texto = autores_texto.find_all('a')  # No necesitas hacer autor.text aquí
                autores = ', '.join([autor.text for autor in autores_texto])  # Ahora usamos list comprehension para extraer los textos
            else:
                autores = "Redacción de CNN Español"
            
            cuerpo = soup_new.find('div', class_='storyfull__body')

            # Si deseas obtener todos los párrafos, puedes cambiar la función de filtro para que solo excluya los párrafos con la clase 'wp-caption-text'
            contenidos = cuerpo.find_all('p', class_=lambda x: x != 'wp-caption-text' if x else True)

            excluir_texto = ['© 2024 Cable News Network.', 'A Warner Bros. Discovery Company.', 'All Rights Reserved.', 'CNN Sans ™ & © 2024 Cable News Network.', 'Guerra de Rusia en Ucrania', 'Guerra en Rusia']

            # Filtrar y limpiar los contenidos
            contenidos_limpios = []
            for contenido in contenidos:
                texto = contenido.text.strip()  # Elimina espacios en blanco al principio y al final del texto
                if not any(excluir in texto for excluir in excluir_texto) and "(CNN Español) --" not in texto and "(CNN) --" not in texto:
                    contenidos_limpios.append(texto)

            # Imprimir cada elemento de la lista contenidos_limpios sin comillas ni corchetes
            for contenido in contenidos_limpios:
                pass
            
            # Captura la fecha y hora actual
            fextraccion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Comprueba si la noticia ya existe en la base de datos antes de guardarla
            if Noticia.objects.filter(titular=titular).exists():
                print('La noticia ya existe en la base de datos')
            else:
                nueva_noticia = Noticia.objects.create(
                    urlimagen=urlimagen,
                    enlace=enlace,
                    titular=titular,
                    autores=autores,
                    contenido='\n'.join(contenidos_limpios),
                    fextraccion=fextraccion
                )

                # Crea una nueva instancia del modelo Fuente y almacena la fuente en ella
                nueva_fuente = Fuente.objects.create(
                    nfuente=nfuente,
                    noticia=nueva_noticia
                )

                # Guarda ambas instancias en la base de datos
                nueva_noticia.save()
                nueva_fuente.save()
                
def scrape_onu():
    # Configura el controlador del navegador (asegúrate de tener el controlador adecuado instalado, por ejemplo, Chromedriver)
    driver = webdriver.Chrome()
    
    # Abre la página web
    driver.get("https://news.un.org/es/news/region/europe")

    # Encuentra el enlace utilizando XPath
    urlenlace = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[4]/div/div/main/section/div[4]/div/div/div/div/div[1]/article/div/div[2]/header/h2/a')

    # Obtiene el atributo 'href' del enlace
    enlace = urlenlace.get_attribute("href")

    # Navega a la URL del enlace
    driver.get(enlace)

    # Encuentra el titular del artículo
    titular = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/section/div/div/div/div/div/div/div/h1/span').text

    # Verifica si "ucrania" está presente en el titular (insensible a mayúsculas y minúsculas)
    if "Ucrania" and "ucraniano" not in titular:
        print("El titular no contiene Ucrania, por eso no se extraerá la noticia")
    else:
        imagen = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/section/div/div/div/div/div/div/div/div[1]/div/div/picture/img')

        urlimagen = imagen.get_attribute("src")

        # Encuentra la fuente del artículo y elimina "Noticias" del principio
        fuente = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[1]/div[1]/div/div/div[1]/div/div[2]/div[1]/a').text
        nfuente = fuente.replace("Noticias ", "")
        
        autores = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[1]/div[1]/div/div/div[1]/div/div[2]/div[1]/a').text

        # Encuentra y muestra el contenido del artículo
        content = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[4]/div/div/main/section/div[4]/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div').text

        # Obtiene la fecha y hora de extracción del artículo
        fextraccion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Cierra el navegador
        driver.quit()

        # Comprueba si la noticia ya existe en la base de datos antes de guardarla
        if Noticia.objects.filter(titular=titular).exists():
            print("La noticia ya existe en la base de datos.")
        else:
            # Crea una instancia de Noticia y guarda la noticia en la base de datos
            nueva_noticia = Noticia.objects.create(
                urlimagen=urlimagen,
                enlace=enlace,
                titular=titular,
                autores=autores,
                contenido=content,
                fextraccion=fextraccion
            )
            # Crea una nueva instancia del modelo Fuente y almacena la fuente en ella
            nueva_fuente = Fuente.objects.create(
                nfuente=nfuente,
                noticia=nueva_noticia
            )

            # Guarda ambas instancias en la base de datos
            nueva_noticia.save()
            nueva_fuente.save()