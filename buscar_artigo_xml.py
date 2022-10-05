import json
import time
from datetime import date
import flask
import requests
import zipfile
import os
from bs4 import BeautifulSoup
import re
import numpy as np
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
import msal
import sys
import logging
import webbrowser
import urllib3
from flask import request
import builtwith
from urllib.error import HTTPError
from urllib.error import URLError

login = ""
senha = ""

#tipo_dou = "DO1 DO2 DO3"
tipo_dou = "DO1 DO2 DO3 DO1E DO2E DO3E"  # Seções separadas por espaço
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
nova_data = '2022' + "-" + '09' + "-" + '09'


def download(data=data_completa):
    if s.cookies.get('inlabs_session_cookie'):
        cookie = s.cookies.get('inlabs_session_cookie')
    else:
        print("Falha ao obter cookie. Verifique suas credenciais");
        exit(37)

    for dou_secao in tipo_dou.split(' '):
        print("Aguarde Download...")
        url_arquivo = url_download + data + "&dl=" + data + "-" + dou_secao + ".zip"
        cabecalho_arquivo = {'Cookie': 'inlabs_session_cookie=' + cookie, 'origem': '736372697074'}
        response_arquivo = s.request("GET", url_arquivo, headers=cabecalho_arquivo)
        if response_arquivo.status_code == 200:
            with open(data + "-" + dou_secao + ".zip", "wb") as f:
                f.write(response_arquivo.content)
                print("Arquivo %s salvo." % (data + "-" + dou_secao + ".zip"))
            del response_arquivo
            del f
        elif response_arquivo.status_code == 404:
            print("Arquivo não encontrado: %s" % (data + "-" + dou_secao + ".zip"))
    print("Aplicação encerrada")


dicionario = {"Escopo": ["Gabinete de Segurança Institucional",
                        "Secretaria Especial do Tesouro e Orçamento",
                        "Superintendência de Seguros Privados",
                        "Superintendência Nacional de Previdência Complementar",
                        "Banco Central do Brasil",
                        "Conselho de Controle de Atividades Financeiras",
                        "Presidência da República",
                        "Ministério da Economia",
                        "Atos do Poder Legislativo",
                        "Atos do Poder Executivo"],
              "Titulo": ["Resolução Coremec",
                         "([ ]CMN[ ])|([ ]CMN[0-9])",
                         "PORTARIA SETO",
                         "Resolução BCB",
                         "Despachos do Presidente da República",
                         "Medida Provisória"],
              "Ementa": ["Programa Nacional de Apoio às Microempresas e Empresas de Pequeno Porte",
                         "lavagem de dinheiro",
                         "Administração Pública federal direta, autárquia e fundacional",
                         "Decreto nº 10.835",
                         "Subdelega competências para a prática de atos de gestão de pessoas no âmbito do Ministério da Economia às Autoridades que menciona",
                         "(Sistema de Pessoal Civil da Administração Pública Federal)|(Sistema de Pessoal Civil da Administração Federal)|(SIPEC)",
                         "Comitê Gestor da Segurança da Informação",
                         "Lei nº 8.429",
                         "Lei nº 14.133",
                         "Programa de Estímulo ao Crédito",
                         "(Lei geral de proteção de dados)|(LGPD)",
                         "Banco Central",
                         "Conselho de Controle de Atividades Financeiras",
                         "Grupo de Ação Financeira contra a Lavagem de Dinheiro e o Financiamento do Terrorismo",
                         "Comitê de Regulação e Fiscalização dos Mercados Financeiro, de Capitais, de Seguros, de Previdência e Capitalização",
                         "Proteção de Dados Pessoais",
                         "Comitê de Estabilidade Financeira",
                         "Educação Financeira",
                         "Imposto sobre Operações Financeiras",
                         "(Poder (.*?Executivo))|(Poderes (.*?Executivo))",
                         "Decreto nº 93.872, de 23 de dezembro de 1986",
                         "Altera a Consolidação das Leis do Trabalho"],
              "Assinatura": [["Presidente do Banco Central do Brasil[<]", "Roberto de Oliveira Campos Neto"],
                            ["Diretor de Relacionamento, Cidadania e Supervisão de Conduta[<]", "Maurício Costa de Moura"],
                            ["Diretor de Fiscalização[<]", "Paulo sérgio Neves de Souza"],
                            ["Diretor de Política Econômica[<]", "Bruno Serra Fernandes"],
                            ["Diretor de Política Monetária[<]", "Fabio Kanczuk"],
                            ["Diretor de Assuntos Internacionais e de Gestão de Riscos Corporativos[<]", "Fernanda Magalhães Rumenos Guardado"],
                            ["Diretor de Organização do Sistema Financeiro e de Resolução[<]", "João Manoel Pinho de Mello"],
                            ["Diretor de Regulação[<]", "Otávio Ribeiro Damaso"],
                            ["Diretor de Administração[<]", "Carolina de Assis Barros"]],
              "Conteudo": ["cargo de Presidente do Banco Central",
                           "cargo de (Diretor | Diretora) do Banco Central",
                           "cargo de Ministro de Estado da Economia",
                           "cargo de Secretário Especial de Fazenda do Ministério da Economia",
                           "cargo de Secretário-Executivo do Ministério da Economia",
                           "cargo de Secretário de Política Econômica",
                           "cargo de Secretário do Tesouro Nacional",
                           "cargo de Secretário do Tesouro e Orçamento do Ministério da Economia",
                           "cargo de Presidente da casa da Moeda do Brasil",
                           "cargo de Diretor da Comissão de Valores Mobiliários",
                           "cargo de Superintendente da Superintendência de Seguros Privados",
                           "cargo de Diretor da Superintendência de Seguros Privados",
                           "cargo de Diretor-Superintendente da Superintendência de Seguros Privados",
                           "cargo de Diretor de Licenciamento da Superintendência Nacional de Previdência Complementar",
                           "cargo de Secretário Especial Adjunto da Secfretaria Especial de Previdência e Trabalho do Ministério da Economia",
                           "cargo de Ministro de Estado do Trabalho e Previdência",
                           "cargo de Secretário-Executivo do Ministério do Trabalho e Previdência",
                           "cargo de Procurador-Geral Federal da Advocacia-Geral da União",
                           "(Exposição de Motivos ((.*?afastamento )(.*?Presidente do Banco Central do Brasil))) | (Exposições de Motivos ((.*?afastamento )(.*?Presidente do Banco Central do Brasil))) | (Exposição de Motivos ((.*?férias )(.*?Presidente do Banco Central do Brasil))) | (Exposições de Motivos ((.*?férias )(.*?Presidente do Banco Central do Brasil)))",
                           "(Exposição de Motivos ((.*?afastamento )(.*?Ministro de Estado da Economia))) | (Exposições de Motivos ((.*?afastamento )(.*?Ministro de Estado da Economia))) | (Exposição de Motivos ((.*?férias )(.*?Ministro de Estado da Economia))) | (Exposições de Motivos ((.*?férias )(.*?Ministro de Estado da Economia)))",
                           "((A Diretora) | (O Diretor)) de Administração do Banco Central do Brasil",
                           "((PORTARIA)(.*?O MINISTRO DE ESTADO DA ECONOMIA)(.*?afastamento)(.*?Banco Central))",
                           "Despacho do Presidente do Banco Central do Brasil",
                           "Comissão Técnica da Moeda e do Crédito",
                           "Secretário-Executivo Adjunto da Secretaria-Executiva do Ministério do Trabalho e Previdência",
                           "Comitê de Regulação e Fiscalização dos Mercados Financeiro, de Capitais, de Seguros, de Previdência e Capitalização",
                           "temas jurídicos relevantes para a administração pública",
                           "cargo de Secretária Especial Adjunta da Secretaria Especial de Comércio Exterior e Assuntos Internacionais do Ministério da Economia",
                           "Banco Central",
                           "Procuradores do Banco Central",
                           "Procurador do Banco Central",
                           "Procuradoria-Geral do Banco Central",
                           "Procurador-Geral do Banco Central",
                           "Presidência da CVM",
                           "Diretor-Presidente do Conselho Diretor da Autoridade Nacional de Proteção de Dados"]
              }


def buscar_artigo(dicionario, data=data_completa):
    for dou_secao in tipo_dou.split(' '):
        nome_arquivo = data + "-" + dou_secao + ".zip"
        diretorio_arquivo = os.path.dirname(os.path.realpath(nome_arquivo))
        arquivos = list()
        #Extrai os arquivos:
        if os.path.isfile(nome_arquivo):
            with zipfile.ZipFile(nome_arquivo, 'r') as zip_ref:
                zip_ref.extractall(diretorio_arquivo)
            #Adiciona os arquivos em uma lista
            for arq in zip_ref.namelist():
                extensao = os.path.splitext(arq)
                if extensao[1] == '.xml':
                    arquivos.append(arq)
            print('****')
            nova_lista = list()
            for file in arquivos:
                with open(file, 'r', encoding="utf-8") as arquivo:
                    conteudo_xml = arquivo.read()
                    bs_texto = BeautifulSoup(conteudo_xml, 'xml')
                    titulo = bs_texto.find('Identifica').get_text()
                    # Extrai o conteúdo do artCategory do arquivo xml:
                    escopo = bs_texto.find('article').get('artCategory')
                    tipo_normativo = bs_texto.find('article').get('artType')
                    pub_name_secao = bs_texto.find('article').get('pubName')
                    corpo_texto = bs_texto.find('Texto').get_text()
                    ementa = bs_texto.find('Ementa').get_text()
                    fim_dict = len(dicionario['Escopo'])
                    # Faz a busca pelo atributo artCategory:
                    if True in np.isin(dicionario['Escopo'][1], escopo.split('/')) and titulo is not None:
                        nova_lista.append(file)
                    if True in np.isin(dicionario['Escopo'][5], escopo.split('/')) \
                            and re.findall("DO1", pub_name_secao, re.IGNORECASE) \
                            and re.findall("Portaria", tipo_normativo, re.IGNORECASE):
                        nova_lista.append(file)
                    if True in np.isin(dicionario['Escopo'][0], escopo.split('/')) \
                            or True in np.isin(dicionario['Escopo'][2:5], escopo.split('/')):
                        nova_lista.append(file)
                    if True in np.isin(dicionario['Escopo'][6], escopo.split('/'))\
                            and not re.findall("PORTARIA CHGAB/VPR", titulo, re.IGNORECASE):
                            nova_lista.append(file)
                    if True in np.isin(dicionario['Escopo'][7], escopo.split('/')):
                            nova_lista.append(file)
                    if True in np.isin(dicionario['Escopo'][8], escopo.split('/')) \
                            and not re.findall("Turismo", ementa, re.IGNORECASE):
                            nova_lista.append(file)
                    if True in np.isin(dicionario['Escopo'][9:fim_dict], escopo.split('/')):
                            nova_lista.append(file)
                        #elif re.findall("DO2", pub_name_secao, re.IGNORECASE) \
                        #        and not re.findall("Secretaria Executiva", escopo):
                        #    nova_lista.append(file)
                        #elif re.findall("DO1", pub_name_secao, re.IGNORECASE) \
                        #        and not re.findall("Instituto Nacional de Tecnologia da Informação", escopo):
                        #    nova_lista.append(file)
                        #elif re.findall("DO3", pub_name_secao, re.IGNORECASE):
                        #    nova_lista.append(file)
            #arquivos encontrados pelo escopo ficam armazenados na nova_lista e as buscas abaixo são feitas somente neles:
            for arq in nova_lista:
                with open(arq, 'r', encoding="utf-8") as arquivo:
                    conteudo_xml = arquivo.read()
                    bs_texto = BeautifulSoup(conteudo_xml, 'xml')
                    # Extrai o conteúdo do identifica do arquivo xml:
                    titulo = bs_texto.find('Identifica').get_text()
                    ementa = bs_texto.find('Ementa').get_text()
                    texto = bs_texto.find('Texto').get_text()
                    fim = len(dicionario['Titulo'])
                    # Faz a busca pelo atributo título:
                    for item in dicionario['Titulo']:
                        if item in dicionario['Titulo'][2]:
                            if re.findall(item, titulo, re.IGNORECASE) \
                                    and (re.findall("Banco Central", ementa, re.IGNORECASE) or
                                         re.findall("Banco Central", texto, re.IGNORECASE)):
                                print(titulo + " --- " + arq)
                        if item in dicionario['Titulo'][4]:
                            if re.findall(item, titulo, re.IGNORECASE) \
                                    and (re.findall("Banco Central", ementa, re.IGNORECASE) or
                                         re.findall("Banco Central", texto, re.IGNORECASE)):
                                print(titulo + " --- " + arq)
                        if item in dicionario['Titulo'][0:2] or item in dicionario['Titulo'][3]:
                            if re.findall(item, titulo, re.IGNORECASE):
                                print(titulo + " --- " + arq)
                        if item in dicionario['Titulo'][5]:
                            if re.findall(item, titulo, re.IGNORECASE) \
                                    and (re.findall("Comissão de Valores Mobiliários", texto, re.IGNORECASE) or
                                         re.findall("treinamento ou em missões oficiais", texto, re.IGNORECASE)):
                                print(titulo + " --- " + arq)
                with open(arq, 'r', encoding="utf-8") as arquivo:
                    conteudo_xml = arquivo.read()
                    bs_texto = BeautifulSoup(conteudo_xml, 'xml')
                    # Extrai o conteúdo da ementa do arquivo xml:
                    ementa = bs_texto.find('Ementa').get_text()
                    fim = len(dicionario['Ementa'])
                    # Faz a busca pela tag Ementa:
                    for item in dicionario['Ementa']:
                        if item in dicionario['Ementa'][5]:
                            padrao1 = "revogação de atos normativos"
                            padrao2 = "dos servidores públicos dos Estados, do Distrito Federal e dos Municípios"
                            # Se tiver "no âmbito" só aceitar se for sucedida de "do Banco Central"
                            padrao3 = "(no âmbito )(?!do Banco Central)"
                            if re.findall(item, ementa, re.IGNORECASE) \
                                    and not re.findall(padrao1, ementa, re.IGNORECASE) \
                                    and not re.findall(padrao2, ementa, re.IGNORECASE) \
                                    and not re.findall(padrao3, ementa, re.IGNORECASE):
                                print(ementa + " --- " + arq)
                        if item in dicionario["Ementa"][11]:
                            nome_titulo = bs_texto.find('Identifica').get_text()
                            if re.findall(item, ementa, re.IGNORECASE) \
                                    and not re.findall("Instrução Normativa BCB", nome_titulo, re.IGNORECASE):
                                print(ementa + " --- " + arq)
                        if item in dicionario['Ementa'][19]:
                            # padrao_130 = "(Poder (.*?Executivo))|(Poderes (.*?Executivo))"
                            # Extrai o título do arquivo xml
                            titulo = bs_texto.find('Identifica').get_text()
                            padrao_titulo = "SETO/ME"
                            inicio_busca = ementa.find('Poder')
                            item1 = 'Poder '
                            item2 = 'Poderes'
                            # Calcula o intervalo para realizar a busca no conteúdo da ementa
                            if re.findall(item1, ementa, re.IGNORECASE):
                                fim_busca = inicio_busca + len('Poder') + 130
                            elif re.findall(item2, ementa, re.IGNORECASE):
                                fim_busca = inicio_busca + len('Poderes') + 130
                            if re.findall(item, ementa, re.IGNORECASE) \
                                    and not re.findall(padrao_titulo, titulo, re.IGNORECASE) \
                                    and re.findall(item, ementa[inicio_busca:fim_busca], re.IGNORECASE):
                                print(ementa + " --- " + arq)
                        if item in dicionario['Ementa'][0:5] \
                                or item in dicionario['Ementa'][6:11] or item in dicionario['Ementa'][12:19] \
                                or item in dicionario['Ementa'][20:fim]:
                            if re.findall(item, ementa, re.IGNORECASE):
                                print(ementa + " --- " + arq)
                with open(arq, 'r', encoding="utf-8") as arquivo:
                    conteudo_xml = arquivo.read()
                    #O parâmetro xml foi substituído por lxml para obter o conteúdo de um parágrafo específico:
                    bs_texto = BeautifulSoup(conteudo_xml, 'lxml')
                    #Extrai todas as ocorrências do cargo e da assinatura do arquivo xml caso existam:
                    if bs_texto.find('p', {'class':'assina'}):
                        assinaturas = bs_texto.find_all('p', {'class':'assina'})
                        #assinatura = bs_texto.find('p', {'class':'assina'}).get_text()
                    else:
                        assinaturas = ""
                    if bs_texto.find('p', {'class': 'cargo'}):
                        cargos = bs_texto.find_all('p', {'class': 'cargo'})
                    else:
                        cargos = ""
                    #Faz a busca pela assinatura e pelo cargo:
                    for item in dicionario["Assinatura"]:
                        for assinatura in assinaturas:
                            if re.findall(item[1], str(assinatura), re.IGNORECASE):
                                indice_lista = assinaturas.index(assinatura)
                                if bs_texto.find('p', {'class': 'cargo'}):
                                    print(str(assinatura.get_text()) + ' --- ' + str(
                                        cargos[indice_lista].get_text()) + ' --- '+ arq)
                                else:
                                    print(str(assinatura.get_text()) + ' --- '+ arq)
                        for cargo in cargos:
                            if re.findall(item[0], str(cargo), re.IGNORECASE):
                                indice_lista = cargos.index(cargo)
                                if bs_texto.find('p', {'class': 'assina'}):
                                    print(str(assinaturas[indice_lista].get_text()) + ' --- ' + str(
                                        cargo.get_text()) + ' --- ' + arq)
                                else:
                                    print(str(cargo.get_text()) + ' --- ' + arq)
                with open(arq, 'r', encoding="utf-8") as arquivo:
                    conteudo_xml = arquivo.read()
                    bs_texto = BeautifulSoup(conteudo_xml, 'xml')
                    #Extrai o conteúdo do identifica do arquivo xml:
                    conteudo = bs_texto.find('Texto').get_text()
                    #Limpa o texto ao eliminar as tags e os atributos:
                    texto_conteudo = re.sub('<[^>]+?>', ' ', conteudo)
                    fim = len(dicionario['Conteudo'])
                    #Faz a busca pela tag Texto:
                    for item in dicionario['Conteudo']:
                        if item in dicionario["Conteudo"][18] or item in dicionario["Conteudo"][19]:
                            if texto_conteudo.find('Exposição de Motivos'):
                                inicio_busca = texto_conteudo.find('Exposição de Motivos')
                                fim_busca = inicio_busca + len('Exposição de Motivos') + 200
                            elif texto_conteudo.find('Exposições de Motivos'):
                                inicio_busca = texto_conteudo.find('Exposições de Motivos')
                                fim_busca = inicio_busca + len('Exposições de Motivos') + 200
                            if re.findall(item, conteudo, re.IGNORECASE) \
                                    and re.findall(item, conteudo[inicio_busca:fim_busca], re.IGNORECASE):
                                print(texto_conteudo + " --- " + arq)
                        if item in dicionario["Conteudo"][22]:
                            padrao = 'Presidente do COAF'
                            if re.findall(item, conteudo, re.IGNORECASE) \
                                    and re.findall(padrao, conteudo, re.IGNORECASE):
                                print(texto_conteudo + " --- " + arq)
                        if item in dicionario["Conteudo"][28]:
                            escopo = bs_texto.find('article').get('artCategory')
                            if re.findall(item, conteudo, re.IGNORECASE) \
                                    and (re.findall("Presidência da República", escopo, re.IGNORECASE) or
                                    re.findall("Secretaria Especial do Tesouro e Orçamento", escopo, re.IGNORECASE)):
                                print(" --- " + arq)
                        if item in dicionario["Conteudo"][29:33]:
                            escopo = bs_texto.find('article').get('artCategory')
                            if re.findall(item, conteudo, re.IGNORECASE) \
                                    and re.findall("Presidência da República", escopo, re.IGNORECASE):
                                print(" --- " + arq)
                        if item in dicionario["Conteudo"][23:28] \
                                or item in dicionario["Conteudo"][0:18] or item in dicionario["Conteudo"][20:22]:
                            if re.findall(item, conteudo, re.IGNORECASE):
                                print(" --- " + arq)
                        if item in dicionario["Conteudo"][33]:
                            pub_name_secao = bs_texto.find('article').get('pubName')
                            escopo = bs_texto.find('article').get('artCategory')
                            if re.findall(item, conteudo, re.IGNORECASE) \
                                and re.findall("DO2", pub_name_secao, re.IGNORECASE):
                                print(" --- " + arq)
                        if item in dicionario["Conteudo"][34:fim]:
                            if re.findall(item, conteudo, re.IGNORECASE):
                                print(" --- " + arq)
    print("Busca Encerrada!")


def share_point_request():
    #URLs do sharepoint:
    url_sharepoint = 'https://bacen.sharepoint.com/'
    url_site = 'https://bacen.sharepoint.com/sites/sumula'
    url_list = 'Lists/Artigos/'
    url = "https://bacen.sharepoint.com/_api/web/lists/GetByTitle('Artigos')/items"
    url_lista = "https://bacen.sharepoint.com/sites/sumula/_api/web/lists/GetByTitle('Artigos')"

    #headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
    #lista = requests.get('https://bacen.sharepoint.com/sites/sumula/Lists/Artigos/', headers=headers)

    client_id = ''
    client_secret = ''
    scope = 'User.Read'
    tenant_id = ''
    redirect_uri = 'https://bacen.sharepoint.com/sumula/sites/artigos'
    code = ''
    session_state = ''
    username = ''
    password = ''

    data = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'response_mode': 'query',
        'scope': scope
    }

    h = {'Content-Type': 'application/json'}

    #Requisição para obter o code:
    #s = requests.get(f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?',
    #                 params=data)
    #nova_url = s.url
    #web = webbrowser.open(nova_url)

    params = {
        'client_id': client_id,
        'scope': scope,
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'client_secret': client_secret,
        'session_state': session_state
    }


    #Requisição POST para obter o token:
    #p = requests.post(f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token',
    #                  data=params)
    #print(p.json())

    token = ''
    headers = {'Authorization': f'Bearer {token}'}

    #Requisição para verificar se os dados estão corretos:
    #r = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    #print(r.json())
    #dicio = r.json()
    #print(dicio["displayName"])

    refresh_token = token

    data_refresh_token = {
        'client_id': client_id,
        'scope': scope,
        'code': code,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'client_secret': client_secret,
        'session_state': session_state
    }

    #Requisição para obter um novo token após a expiração:
   # novo_token = requests.post(f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token',
   #                            data=data_refresh_token)
    #print(novo_token.json())
    #dictionary = novo_token.json()
    #token_refresh = dictionary['access_token']
    #tempo_expiracao = dictionary['expires_in']

    playload = {"username": username,
                "password": password}

    r = requests.get(url_site, headers=headers, data=playload)
    #print(r.status_code)

    r = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers, data=playload)
    #print(r.json())

    #Teste com a biblioteca msal:
    connect_msal = msal.PublicClientApplication(client_id=client_id,
                                                authority=f"https://login.microsoftonline.com/{tenant_id}")
    #connect_msal.acquire_token_interactive(scopes=["User.Read"])
    contas = connect_msal.get_accounts()
    print(contas)
    token = connect_msal.acquire_token_silent_with_error(scopes=["User.Read"], account=None)
    print(token)
    flow = connect_msal.initiate_device_flow(scopes=["User.Read"])
    print(flow)
    time.sleep(1)
    token = connect_msal.acquire_token_by_device_flow(flow=flow)
    print(token)

    #token = connect_msal.acquire_token_silent(scopes=["User.Read"])
    #print(token)
    #connect_msal = msal.ClientApplication(client_id=client_id,client_credential=None,
    #                                      authority=f"https://login.microsoftonline.com/{tenant_id}")
    #token = connect_msal.acquire_token_silent(scopes=["User.ReadBasic.All", "User.Read", "Sites.ReadWrite.All",
    #                                               "Sites.Manage.All", "email"], account=None)
    #connect_msal = msal.ConfidentialClientApplication(client_id= client_id, client_credential=None,
    #                                                  authority=f"https://login.microsoftonline.com/{tenant_id}")
    #token = connect_msal.acquire_token_for_client(scopes=["User.ReadBasic.All", "User.Read", "Sites.ReadWrite.All",
    #                                               "Sites.Manage.All", "email"])
    #Conexão e Autenticação no Sharepoint:
    #context_auth = AuthenticationContext(url_site)
    #context_auth.acquire_token_for_app(client_id, client_secret)
    #ctx = ClientContext(url_site, context_auth)
    #web = ctx.web
    #ctx.load(web)
    #ctx.execute_query()
    #print(web.properties)
    #print("Web site title: {0}".format(web.properties['Title']))
    #lista = ctx.web.lists.get_by_title("Artigos")
    #ctx.load(lista)
    #lista2 = lista.items.get_all().execute_query()
    #print(lista2)
    #print(lista.item_count)
    #print(lista.items)
    #teste:
    #sp_lists = ctx.web.lists
    #s_list = sp_lists.get_by_title("Artigos")
    #l_items = s_list.get_items()
    #ctx.load(l_items)
    #ctx.execute_query()

    #for item in l_items:
    #    print(item.properties)

    #items = ctx.web.lists.get_by_title('Artigos').items
    #ctx.load(items)
    #ctx.execute_query()
    #print(len(items))
    #print(items)
    #print(lista.resource_path)
    #l_itens = lista
    #ctx.load(l_itens)
    #ctx.execute_query()
    #print(lista.to_json())

    #teste 2:
    #list_object = ctx.web.lists.get_by_title("Artigos")
    #items = list_object.get_items()
    #ctx.load(items)
    #ctx.execute_query()

    #for item in items:
    #    print("Item title: {0}".format(item.properties["Title"]))
    #Biblioteca msal para obter o token:
    #config = json.load(open(sys.argv[1]))
    # Create a preferably long-lived app instance which maintains a token cache.

    #app = msal.ConfidentialClientApplication(
    #    client_id=client_id, authority='https://login.microsoftonline.com/bacen',
    #    client_credential=""
        # token_cache=...  # Default cache is in memory only.
        # You can learn how to use SerializableTokenCache from
        # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
    #)

    #result = app.acquire_token_silent(scopes='Site.All.Read', account=None)

    #if not result:
    #    logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
    #    result = app.acquire_token_for_client(scopes=scope)

    #if "access_token" in result:
        # Calling graph using the access token
    #    graph_data = requests.get(  # Use token to call downstream service
    #        url='https://graph.microsoft.com/v1.0/me',
    #        headers={'Authorization': 'Bearer ' + result['access_token']}, ).json()
    #    print("Graph API call result: ")
    #    print(json.dumps(graph_data, indent=2))
    #else:
    #    print(result.get("error"))
    #    print(result.get("error_description"))
    #    print(result.get("correlation_id"))  # You may need this when reporting a bug


def login():
    try:
        response = s.request("POST", url_login, data=payload, headers=headers)
        download()
    except requests.exceptions.ConnectionError:
        login()


#login()
#buscar_artigo(dicionario)
share_point_request()