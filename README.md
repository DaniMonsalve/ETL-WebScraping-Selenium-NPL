# ETL-WebScraping-Selenium-NPL
Proceso de Web Scraping para la extracción de ofertas de trabajo en LinkedIn, y análisis NPL entre ofertas dirigidas a perfiles "Data Analyst" y/o "Data Scientist" 

El notebook "scraping_master" recoge todo el proceso de extracción con Selenium, junto con la creación de los archivos csv.

El notebook "análisis_DataAnalyst_vs_DataScientist" realiza el análisis NPL, con las librerías pandas, numpy, seaborn, matplotlib, worldcloud y Spacy.

El notebook "análisis_correlaciones", a diferencia del análisis NPL (notebook "análisis_DataAnalyst_vs_DataScientist"), en el que utilizaba la lematización con la librería Spacy, he decidido trabajar con un diccionario de términos que me interesa destacar. Los términos seleccionados tienen relación directa con los puestos de "Científico de datos" y "analista de datos", y se refieren a aptitudes y tecnologías usualmente requeridas para estos dos puestos de trabajo. La razón de utilizar este filtro de términos es la misma por la que me decidí a utilizar la lematización, el gran volumen de texto a analizar.

Para futuros pasos, se insertarán todos los csv generados dentro de una bbd MongoDB.

*Para el momento en el que se crea este repositorio (26/02/2023) se analizan 1343 ofertas.
