
import os
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-extensions')
options.add_experimental_option('prefs', {
        "download.prompt_for_download": False,
        "download.default_directory" : r"C:\Users\CESAR\Desktop\GitHub",
        "savefile.default_directory": r"C:\Users\CESAR\Desktop\GitHub"})
chromedriver = "C:/Program Files/Chromedriver/chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver,chrome_options=options)

#En Lima existen las siguientes estaciones sobre contaminacion del aire
estaciones = ["111286","111287","112192","112193","112194","112208","112233","112265","112266","112267"]
listas = []

#Para cada estacion se abre una pagina, debido a que el URL cambia de acuerdo a cada estacion
for est in estaciones:
	#Pagina web
	driver.get('https://www.senamhi.gob.pe/?p=calidad_del_aire-estadistica&e=' + str(est))
	time.sleep(2)

	#Nueva ventana
	driver.find_element('xpath','/html/body/div[3]/div/div/div[1]/table/tbody/tr[2]/td[6]/a').click()
	time.sleep(2)

	#Nuevo frame
	frame1 = driver.find_element('xpath','//*[@id="iframeGraficas"]')
	driver.switch_to.frame(frame1)
	time.sleep(2)

	#Parametro contaminante
	n_pc = driver.find_element('id','cboConta')
	q_pc = n_pc.find_elements(By.TAG_NAME,'option')
	for pc in range(1,len(q_pc)):
		s_pc = Select(driver.find_element('id','cboConta'))
		s_pc.select_by_index(pc)

		#Fecha (Desde)
		fecha1 = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="datepickerFch1"]')))
		fecha1.clear()
		fecha1.send_keys("12/09/2014")
		fecha1.send_keys(Keys.RETURN)
		time.sleep(2)

		#Consultar
		driver.find_element('xpath','/html/body/div[1]/div[1]/form/div[7]/button').click()
		time.sleep(10)

		#Nuevo frame
		frame2 = driver.find_element('xpath','/html/body/div[1]/div[2]/iframe')
		driver.switch_to.frame(frame2)
		time.sleep(2)

		#Extraer información
		informacion = driver.find_element('xpath','/html/body/script[3]')
		data = informacion.get_attribute('innerHTML')
		data_tabla = data.split("{")
		time.sleep(2)

		#Fecha
		data_fecha = data_tabla[5]
		time.sleep(3)
		data_fecha = data_fecha.replace("categories: ","").replace("},","").replace("yAxis:","").replace("[","").replace("]","").replace("\n","").strip()
		time.sleep(3)
		lista_fecha = data_fecha.split("','")
		time.sleep(3)
		
		#Valores de contaminacion
		#El oxido de nitrogeno (N_NO2) tiene un valor adicional que desconfigura la informacion
		if pc==4:
			data_valor = data_tabla[16]
		else:
			data_valor = data_tabla[14]
		time.sleep(3)
		data_valor = data_valor.replace("radius: 0,","").replace("},","").replace("data: [","").replace("]","").replace("}","").replace(")","").replace(";","").replace("\n","").strip()
		time.sleep(3)
		lista_valor = data_valor.split(",")
		time.sleep(3)

		#El oxido de nitrogeno (N_NO2) tiene un valor adicional que desconfigura la informacion
		if pc==4:
			data_nombre = data_tabla[15] 
		else:
			data_nombre = data_tabla[13] 
		data_nombre = data_nombre.replace("name: '","").replace("',","").replace("marker:","").replace("\n","").strip()
		time.sleep(3)
		lista_nombre = [data_nombre] * len(lista_fecha) 

		#Estacion
		data_estacion = data_tabla[3]
		data_estacion = data_estacion.replace("text: 'ESTACI\\u00D3N: ","").replace("'","").replace("},","").replace("subtitle:","").replace("\n","").strip()
		time.sleep(3)
		lista_estacion = [data_estacion] * len(lista_fecha)

		#Descarga
		df = pd.DataFrame(list(zip(lista_fecha, lista_valor, lista_nombre, lista_estacion)), columns=['fecha', 'valor','nombre','estacion']) 
		filename = 'A_' + str(est) + '.csv' 
		if not df.empty:
			df.to_csv(filename, mode='a', header=not os.path.exists(filename), encoding='utf-8-sig', index=False)

		#Regresar al frame anterior
		driver.switch_to.parent_frame()

	#Cerrar página
	driver.switch_to.parent_frame()
	driver.find_element('xpath','/html/body/div[3]/div/div/div[2]/div/div/div[2]/button').click()
	time.sleep(5)

driver.close()