from bs4 import BeautifulSoup
import re
import zipfile
import os
import numpy as np

dicionario = {"Escopo": ["Gabinete de Segurança Institucional",
                        "Secretaria Especial do Tesouro e Orçamento",
                        "Superintendência de Seguros Privados",
                        "Superintedência Nacional de Previdência Complementar",
                        "Banco Central do Brasil"],
              "Titulo": ["Resolução Coremec",
                         " CMN",
                         "PORTARIA SETO"]}


for item in dicionario['Titulo']:
    print(item)

def buscar_artigo(dicionario):
    nome_arquivo = "2022-08-30-DO1.zip"
    diretorio_arquivo = os.path.dirname(os.path.realpath(nome_arquivo))
    arquivos = list()
    with zipfile.ZipFile(nome_arquivo, 'r') as zip_ref:
        zip_ref.extractall(diretorio_arquivo)
    for arq in zip_ref.namelist():
        extensao = os.path.splitext(arq)
        if extensao[1] == '.xml':
            arquivos.append(arq)
    # Faz a leitura de cada arquivo:
    for file in arquivos:
        with open(file, 'r', encoding="utf-8") as arquivo:
            conteudo_xml = arquivo.read()
            bs_texto = BeautifulSoup(conteudo_xml, 'xml')
            # Extrai o texto do arquivo xml:
            texto_xml = bs_texto.find('Texto').get_text()
            texto_xml = bs_texto.find('xml').get_text()
            identifica_xml = bs_texto.find('Identifica').get_text()
            #print(identifica_xml)
            ementa_xml = bs_texto.find('Ementa').get_text()
            artcategory_xml = bs_texto.find('article').get('artCategory')
            #Percorre cada item do dicionário:
            #for escopo, itens in dicionario.items():
            #    for item in itens:
            #        if bs_texto.find(artCategory=item):
            #            print(file)
                        #texto_artcategory = bs_texto.select('[artCategory]')
            for chave, itens in dicionario.items():
                for item in itens:
                    if chave == 'Titulo':
                        if re.findall(item, identifica_xml, re.IGNORECASE):
                            print(f"Arquivo {file}")


buscar_artigo(dicionario)