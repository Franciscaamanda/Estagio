from bs4 import BeautifulSoup
import re
import zipfile
import os

dicionario = {"Escopo": ["Gabinete de Segurança Institucional",
              "Secretaria Especial do Tesouro e Orçamento",
              "Superintedência de Seguros Privados",
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
            for escopo, itens in dicionario.items():
                for item in itens:
                    artcategory = bs_texto.find(artCategory=item)
                    if bs_texto.find(artCategory=item):
                        print(file)
            #if re.findall(artcategory, ementa, re.IGNORECASE):
            #        print(f"Arquivo {file}:")
            #        print(identifica_artigo)
            #        print(ementa_artigo)
            #        print(texto_artigo)
            #        print(bs_texto.find('article').get_text())


buscar_artigo(dicionario)

with open("530_20220825_14833382.xml", 'r', encoding="utf-8") as arquivo:
    conteudo_xml = arquivo.read()
    bs_texto = BeautifulSoup(conteudo_xml, 'xml')
    for escopo, itens in dicionario.items():
        for item in itens:
            artcategory = bs_texto.find(artCategory="Ministério da Educação/Universidade Federal do Triângulo Mineiro/Pró-Reitoria de Administração/Departamento de Licitações e Contratos/Divisão de Contratos")
            #print(artcategory)