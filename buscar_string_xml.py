from bs4 import BeautifulSoup
import re
import zipfile
import os


def buscar_artigo(padrao):
    nome_arquivo = "2022-08-25-DO3.zip"
    diretorio_arquivo = os.path.dirname(os.path.realpath(nome_arquivo))
    arquivos = list()
    with zipfile.ZipFile(nome_arquivo, 'r') as zip_ref:
        zip_ref.extractall(diretorio_arquivo)
    for arq in zip_ref.namelist():
        arquivos.append(arq)
    for file in arquivos:
        print(f"Buscando no arquivo {file}...")
        with open(file, 'r', encoding="utf-8") as arquivo:
            texto = arquivo.read()
            bs_texto = BeautifulSoup(texto, 'xml')
            x = bs_texto.find('Texto').get_text()
            if re.findall(padrao, x, re.IGNORECASE):
                print(f"Arquivo {file}:")
                print(x)
        print(f"Busca Encerrada no arquivo {file}!")


buscar_artigo("Ilana Trombka")