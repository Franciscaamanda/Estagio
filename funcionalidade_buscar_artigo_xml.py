from datetime import date
import requests
import zipfile
import os
from bs4 import BeautifulSoup
import re
import numpy as np

login = ""
senha = ""

tipo_dou = "DO1 DO2 DO3"
#tipo_dou = "DO1 DO2 DO3 DO1E DO2E DO3E"  # Seções separadas por espaço
# Opções DO1 DO2 DO3 DO1E DO2E DO3E

url_login = "https://inlabs.in.gov.br/logar.php"
url_download = "https://inlabs.in.gov.br/index.php?p="

payload = {"email": login, "password": senha}
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}
s = requests.Session()

# Montagem da URL:
ano = date.today().strftime("%Y")
mes = date.today().strftime("%m")
dia = date.today().strftime("%d")
data_completa = ano + "-" + mes + "-" + dia


def download():
    if s.cookies.get('inlabs_session_cookie'):
        cookie = s.cookies.get('inlabs_session_cookie')
    else:
        print("Falha ao obter cookie. Verifique suas credenciais");
        exit(37)

    for dou_secao in tipo_dou.split(' '):
        print("Aguarde Download...")
        url_arquivo = url_download + data_completa + "&dl=" + data_completa + "-" + dou_secao + ".zip"
        cabecalho_arquivo = {'Cookie': 'inlabs_session_cookie=' + cookie, 'origem': '736372697074'}
        response_arquivo = s.request("GET", url_arquivo, headers=cabecalho_arquivo)
        if response_arquivo.status_code == 200:
            with open(data_completa + "-" + dou_secao + ".zip", "wb") as f:
                f.write(response_arquivo.content)
                print("Arquivo %s salvo." % (data_completa + "-" + dou_secao + ".zip"))
            del response_arquivo
            del f
        elif response_arquivo.status_code == 404:
            print("Arquivo não encontrado: %s" % (data_completa + "-" + dou_secao + ".zip"))

    print("Aplicação encerrada")


dicionario = {"Escopo": ["Gabinete de Segurança Institucional",
                        "Secretaria Especial do Tesouro e Orçamento",
                        "Superintendência de Seguros Privados",
                        "Superintendência Nacional de Previdência Complementar",
                        "Banco Central do Brasil"],
              "Titulo": ["Resolução Coremec",
                         "([ ]CMN[ ])|([ ]CMN[0-9])",
                         "PORTARIA SETO",
                         "Resolução BCB",
                         "Instrução Normativa BCB",
                         "Despachos do Presidente da República"]
              }


def buscar_escopo(dicionario):
    for dou_secao in tipo_dou.split(' '):
        nome_arquivo = data_completa + "-" + dou_secao + ".zip"
        diretorio_arquivo = os.path.dirname(os.path.realpath(nome_arquivo))
        arquivos = list()
        #Extrai os arquivos:
        with zipfile.ZipFile(nome_arquivo, 'r') as zip_ref:
            zip_ref.extractall(diretorio_arquivo)
        #Adiciona os arquivos em uma lista
        for arq in zip_ref.namelist():
            extensao = os.path.splitext(arq)
            if extensao[1] == '.xml':
                arquivos.append(arq)
        #Faz a leitura de cada arquivo:
        print('****')
        for file in arquivos:
            with open(file, 'r', encoding="utf-8") as arquivo:
                conteudo_xml = arquivo.read()
                bs_texto = BeautifulSoup(conteudo_xml, 'xml')
                #Extrai o conteúdo do artCategory do arquivo xml:
                escopo = bs_texto.find('article').get('artCategory')
                #Faz a busca pelo atributo artCategory:
                if True in np.isin(dicionario['Escopo'], escopo.split('/')):
                    print(escopo + ' --- ' + file)
                    #print("Nosso dicionário: ")
                    #print(dicionario['Escopo'])
                    #print("artCategory: " + escopo)
                 #   print(escopo.split('/'))
                  #  print(np.isin(dicionario['Escopo'], escopo.split('/')))
    print("Busca Encerrada!")


def buscar_titulo(dicionario):
    for dou_secao in tipo_dou.split(' '):
        nome_arquivo = data_completa + "-" + dou_secao + ".zip"
        diretorio_arquivo = os.path.dirname(os.path.realpath(nome_arquivo))
        arquivos = list()
        #Extrai os arquivos:
        with zipfile.ZipFile(nome_arquivo, 'r') as zip_ref:
            zip_ref.extractall(diretorio_arquivo)
        #Adiciona os arquivos em uma lista
        for arq in zip_ref.namelist():
            extensao = os.path.splitext(arq)
            if extensao[1] == '.xml':
                arquivos.append(arq)
        #Faz a leitura de cada arquivo:
        for file in arquivos:
            with open(file, 'r', encoding="utf-8") as arquivo:
                conteudo_xml = arquivo.read()
                bs_texto = BeautifulSoup(conteudo_xml, 'xml')
                #Extrai o conteúdo do identifica do arquivo xml:
                titulo = bs_texto.find('Identifica').get_text()
                #Faz a busca pelo atributo artCategory:
                for item in dicionario['Titulo']:
                    if re.findall(item, titulo, re.IGNORECASE):
                        print(f"Arquivo encontrado pelo Título:{file}")
    print("Busca Encerrada!")


def login():
    try:
        response = s.request("POST", url_login, data=payload, headers=headers)
        download()
    except requests.exceptions.ConnectionError:
        login()


login()
#buscar_escopo(dicionario)
buscar_titulo(dicionario)