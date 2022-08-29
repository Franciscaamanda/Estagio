from bs4 import BeautifulSoup
import re
import zipfile
import os
import numpy as np

dicionario = {"Escopo": ["Gabinete de Segurança Institucional",
              "Secretaria Especial do Tesouro e Orçamento",
              "Superintendência de Seguros Privados",
              "Superintedência Nacional de Previdência Complementar",
              "Banco Central do Brasil"]}

for escopo, itens in dicionario.items():
    for item in itens:
        print(item)

def buscar_artigo(dicionario):
    nome_arquivo = "2022-08-25-DO1.zip"
    diretorio_arquivo = os.path.dirname(os.path.realpath(nome_arquivo))
    arquivos = list()
    with zipfile.ZipFile(nome_arquivo, 'r') as zip_ref:
        zip_ref.extractall(diretorio_arquivo)
    for arq in zip_ref.namelist():
        extensao = os.path.splitext(arq)
        if extensao[1] == '.xml':
            arquivos.append(arq)

    print('****')
    # Faz a leitura de cada arquivo:
    for file in arquivos:
        with open(file, 'r', encoding="utf-8") as arquivo:
            conteudo_xml = arquivo.read()
            bs_texto = BeautifulSoup(conteudo_xml, 'xml')
            # Extrai o texto do arquivo xml:
            texto_artigo = bs_texto.find('Texto').get_text()
            identifica_artigo = bs_texto.find('Identifica').get_text()
            ementa_artigo = bs_texto.find('Ementa').get_text()
            ementa = bs_texto.find('Ementa').get_text()
            #Percorre os cada item do dicionário:
            escopo = bs_texto.find('article').get('artCategory')
            if True in np.isin(dicionario['Escopo'], escopo.split('/')):
            #if escopo in dicionario['Escopo']:
                print("Nosso dicionário: ") 
                print(dicionario['Escopo'])
                print("artCategory: " + escopo) 
                print(escopo.split('/'))
                print(np.isin(dicionario['Escopo'], escopo.split('/')))
                print('***********************')
                print(escopo + ' --- ' + file)
                print('***********************')
            #else:
            #    print(escopo)


buscar_artigo(dicionario)