from bs4 import BeautifulSoup
import re

arquivos = ["530_20220825_14828973.xml", "530_20220825_14829228.xml"]
def buscar_palavras(palavra):
    for arq in arquivos:
        with open(arq, 'r', encoding="utf-8") as arquivo:
            texto = arquivo.read()
            bs_texto = BeautifulSoup(texto, 'xml')
            x = bs_texto.find('Texto').get_text()
            if re.findall(palavra, x, re.IGNORECASE):
                print(f"Arquivo {arq}:")
                print(x)

buscar_palavras("Edmar rodrigues")