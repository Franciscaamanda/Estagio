import datetime
from datetime import date,timedelta
import zipfile
import os
from bs4 import BeautifulSoup
import re
import numpy as np
import requests
from msal import PublicClientApplication
import holidays

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

artigos_encontrados = list()
parametros_busca = dict()

cargos_interesse = {"Cargos": ["(Comoc)|(Coremec)",
                            "Ministro da Economia",
                            "Secretário Especial de Fazenda",
                            "Secretário-Executivo do Ministério da Economia",
                            "Secretário de Política Econômica do Ministério da Economia",
                            "Secretário do Tesouro Nacional",
                            "Presidente da Casa da Moeda",
                            "Comissão de Valores Mobiliários",
                            "Superintendência de Seguros Privados",
                            "Superintendência Nacional de Previdência Complementar",
                            "Secretaria de Previdência da Secretaria Especial de Previdência e Trabalho do Ministério da Economia"]
}


def feriados(data=data_completa):
    feriados = holidays.Brazil()
    if data in feriados:
        return True
    else:
        return False


def lista_feriados():
    feriados = holidays.Brazil()
    for feriado in feriados['2022-01-01': '2022-12-31']:
        print(feriado)


def data_anterior_util(data=data_completa):
    data_com = data.split('-')
    ano = data_com[0]
    mes = data_com[1]
    dia = data_com[2]
    # Troca a data de hoje pela data que o usuário definir
    data_escolhida = date.today().replace(int(ano), int(mes), int(dia))
    dia_semana = data_escolhida.weekday()
    if dia_semana == 0: #segunda-feira é representada pelo valor 0
        data_anterior = data_escolhida - timedelta(3)
    else:
        data_anterior = data_escolhida - timedelta(1)
    feriado = feriados(str(data_anterior))
    if feriado is True:
        return data_anterior_util(str(data_anterior))
    else:
        return data_anterior


def download(data=data_completa):
    data_anterior = data_anterior_util()
    if s.cookies.get('inlabs_session_cookie'):
        cookie = s.cookies.get('inlabs_session_cookie')
    else:
        print("Falha ao obter cookie. Verifique suas credenciais");
        exit(37)
    for dou_secao in tipo_dou.split(' '):
        if dou_secao == 'DO1E' or dou_secao == 'DO2E' or dou_secao == 'DO3E':
            data = str(data_anterior)
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
                        "Atos do Poder Executivo",
                        "Controladoria-Geral da União"],
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
                         "Altera a Consolidação das Leis do Trabalho",
                         "Comissão de Valores Mobiliários"],
              "Assinatura": [["Presidente do Banco Central do Brasil[<]", "Roberto de Oliveira Campos Neto"],
                            ["Diretor de Relacionamento, Cidadania e Supervisão de Conduta[<]", "Maurício Costa de Moura"],
                            ["Diretor de Fiscalização[<]", "Paulo sérgio Neves de Souza"],
                            ["Diretor de Política Econômica[<]", "Bruno Serra Fernandes"],
                            ["Diretor de Política Monetária[<]", "Fabio Kanczuk"],
                            ["Diretor de Assuntos Internacionais e de Gestão de Riscos Corporativos[<]", "Fernanda Magalhães Rumenos Guardado"],
                            ["Diretor de Organização do Sistema Financeiro e de Resolução[<]", "João Manoel Pinho de Mello"],
                            ["Diretor de Regulação[<]", "(Otávio Ribeiro Damaso)|(Otavio Ribeiro Damaso)"],
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
                           "(Exposição de Motivos(.*?afastamento )(.*?Presidente do Banco Central do Brasil))|(Exposições de Motivos(.*?afastamento )(.*?Presidente do Banco Central do Brasil))|(Exposição de Motivos(.*?férias )(.*?Presidente do Banco Central do Brasil))|(Exposições de Motivos(.*?férias )(.*?Presidente do Banco Central do Brasil))",
                           "(Exposição de Motivos(.*?afastamento )(.*?Ministro de Estado da Economia))|(Exposições de Motivos(.*?afastamento )(.*?Ministro de Estado da Economia))|(Exposição de Motivos(.*?férias )(.*?Ministro de Estado da Economia))|(Exposições de Motivos(.*?férias )(.*?Ministro de Estado da Economia))",
                           "((A Diretora)|(O Diretor)) de Administração do Banco Central do Brasil",
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
                           "Diretor-Presidente do Conselho Diretor da Autoridade Nacional de Proteção de Dados",
                           "Presidente do Conselho de Controle de Atividades Financeiras",
                           "Portaria nº 179, de 22 de abril de 2019"]
              }


def buscar_artigo(dicionario, data=data_completa):
    data_anterior = data_anterior_util()
    for dou_secao in tipo_dou.split(' '):
        if dou_secao == 'DO1E' or dou_secao == 'DO2E' or dou_secao == 'DO3E':
            data = str(data_anterior)
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
                    art_type = bs_texto.find('article').get('artType')
                    # Faz a busca pelo atributo artCategory:
                    if True in np.isin(dicionario['Escopo'][1], escopo.split('/')) and titulo is not None \
                            and not re.findall("IECP", corpo_texto, re.IGNORECASE) \
                            and not re.findall("PORTARIA DE PESSOAL SEACO/SOF/SETO/ME", titulo, re.IGNORECASE):
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
                    if True in np.isin(dicionario['Escopo'][7], escopo.split('/')) \
                            and not re.findall("Extrato de Inexigibilidade", art_type, re.IGNORECASE) \
                            and not re.findall("IECP", corpo_texto, re.IGNORECASE) \
                            and not re.findall("PORTARIA DE PESSOAL SEACO/SOF/SETO/ME", titulo, re.IGNORECASE):
                            nova_lista.append(file)
                    if True in np.isin(dicionario['Escopo'][8], escopo.split('/')) \
                            and not re.findall("Turismo", ementa, re.IGNORECASE):
                            nova_lista.append(file)
                    if True in np.isin(dicionario['Escopo'][9:fim_dict], escopo.split('/')):
                            nova_lista.append(file)
            #Arquivos encontrados pelo escopo ficam armazenados na nova_lista e as buscas abaixo são feitas somente neles:
            for arq in nova_lista:
                lista_parametros = list()
                with open(arq, 'r', encoding="utf-8") as arquivo:
                    conteudo_xml = arquivo.read()
                    bs_texto = BeautifulSoup(conteudo_xml, 'xml')
                    # Extrai o conteúdo do identifica do arquivo xml:
                    titulo = bs_texto.find('Identifica').get_text()
                    ementa = bs_texto.find('Ementa').get_text()
                    texto = bs_texto.find('Texto').get_text()
                    # Faz a busca pelo atributo título:
                    for item in dicionario['Titulo']:
                        if item in dicionario['Titulo'][2]:
                            if re.findall(item, titulo, re.IGNORECASE) \
                                    and (re.findall("Banco Central", ementa, re.IGNORECASE) or
                                         re.findall("Banco Central", texto, re.IGNORECASE)):
                                print(titulo + " --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario['Titulo'][4]:
                            if re.findall(item, titulo, re.IGNORECASE) \
                                    and (re.findall("Banco Central", ementa, re.IGNORECASE) or
                                         re.findall("Banco Central", texto, re.IGNORECASE)):
                                print(titulo + " --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario['Titulo'][0:2] or item in dicionario['Titulo'][3]:
                            if re.findall(item, titulo, re.IGNORECASE):
                                print(titulo + " --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario['Titulo'][5]:
                            if re.findall(item, titulo, re.IGNORECASE) \
                                    and (re.findall("Comissão de Valores Mobiliários", texto, re.IGNORECASE) or
                                         re.findall("treinamento ou em missões oficiais", texto, re.IGNORECASE)):
                                print(titulo + " --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
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
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario["Ementa"][11]:
                            nome_titulo = bs_texto.find('Identifica').get_text()
                            if re.findall(item, ementa, re.IGNORECASE) \
                                    and not re.findall("Instrução Normativa BCB", nome_titulo, re.IGNORECASE):
                                print(ementa + " --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
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
                                    and re.findall(item, ementa[inicio_busca:fim_busca], re.IGNORECASE) \
                                    and not re.findall("no âmbito da Secretaria de Gestão e Desempenho de Pessoal da Secretaria Especial de Desburocratização, Gestão e Governo Digital do Ministério da Economia", ementa, re.IGNORECASE) \
                                    and not re.findall("no âmbito da", ementa, re.IGNORECASE) \
                                    and not re.findall("Protocolo ao Acordo de Comércio e Cooperação Econômica entre o Governo da República Federativa do Brasil e o Governo dos Estados Unidos da América Relacionado a Regras Comerciais e de Transparência", ementa, re.IGNORECASE):
                                print(ementa + " --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario['Ementa'][0:5] \
                                or item in dicionario['Ementa'][6:10] or item in dicionario['Ementa'][12:15] \
                                or item in dicionario['Ementa'][16:19] \
                                or item in dicionario['Ementa'][20:fim]:
                            if re.findall(item, ementa, re.IGNORECASE):
                                print(ementa + " --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario['Ementa'][10] or item in dicionario['Ementa'][15]:
                            if re.findall(item, ementa, re.IGNORECASE) \
                                    and not re.findall('Transforma a Autoridade Nacional de Proteção de Dados \(ANPD\) em autarquia', ementa, re.IGNORECASE):
                                print(ementa + " --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
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
                                    if item not in lista_parametros:
                                        lista_parametros.append(item)
                                    if arq not in artigos_encontrados:
                                        artigos_encontrados.append(arq)
                                else:
                                    print(str(assinatura.get_text()) + ' --- '+ arq)
                                    if item not in lista_parametros:
                                        lista_parametros.append(item)
                                    if arq not in artigos_encontrados:
                                        artigos_encontrados.append(arq)
                        for cargo in cargos:
                            if re.findall(item[0], str(cargo), re.IGNORECASE):
                                indice_lista = cargos.index(cargo)
                                if bs_texto.find('p', {'class': 'assina'}):
                                    print(str(assinaturas[indice_lista].get_text()) + ' --- ' + str(
                                        cargo.get_text()) + ' --- ' + arq)
                                    if item not in lista_parametros:
                                        lista_parametros.append(item)
                                    if arq not in artigos_encontrados:
                                        artigos_encontrados.append(arq)
                                else:
                                    print(str(cargo.get_text()) + ' --- ' + arq)
                                    if item not in lista_parametros:
                                        lista_parametros.append(item)
                                    if arq not in artigos_encontrados:
                                        artigos_encontrados.append(arq)
                with open(arq, 'r', encoding="utf-8") as arquivo:
                    conteudo_xml = arquivo.read()
                    bs_texto = BeautifulSoup(conteudo_xml, 'xml')
                    #Extrai o conteúdo do identifica do arquivo xml:
                    conteudo = bs_texto.find('Texto').get_text()
                    #Limpa o texto ao eliminar as tags e os atributos:
                    texto_conteudo = re.sub('<[^>]+?>', ' ', conteudo)
                    escopo = bs_texto.find('article').get('artCategory')
                    fim = len(dicionario['Conteudo'])
                    #para obter só o arquivo principal dos arquivos que são divididos em vários arquivos xml:
                    if re.findall('-[2-9]', arq, re.IGNORECASE):
                        numero = arq.find('-')
                        n = arq[numero:numero+2]
                        # deixa no formato xxx_xxxxxxxx_xxxxxxxx-1.xml:
                        arq = arq.replace(n, '-1')
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
                                print(" --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario["Conteudo"][22]:
                            padrao = 'Presidente do COAF'
                            if re.findall(item, conteudo, re.IGNORECASE) \
                                    and re.findall(padrao, conteudo, re.IGNORECASE):
                                print(" --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario["Conteudo"][28]:
                            escopo = bs_texto.find('article').get('artCategory')
                            if re.findall(item, conteudo, re.IGNORECASE) \
                                    and (re.findall("Presidência da República", escopo, re.IGNORECASE) or
                                    re.findall("Secretaria Especial do Tesouro e Orçamento", escopo, re.IGNORECASE)):
                                print(" --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario["Conteudo"][29:33]:
                            escopo = bs_texto.find('article').get('artCategory')
                            if re.findall(item, conteudo, re.IGNORECASE) \
                                    and re.findall("Presidência da República", escopo, re.IGNORECASE):
                                print(" --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario["Conteudo"][23:28] \
                                or item in dicionario["Conteudo"][0:18] or item in dicionario["Conteudo"][20:22]:
                            if re.findall(item, conteudo, re.IGNORECASE):
                                print(" --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario["Conteudo"][33]:
                            pub_name_secao = bs_texto.find('article').get('pubName')
                            if re.findall(item, conteudo, re.IGNORECASE) \
                                    and re.findall("DO2", pub_name_secao, re.IGNORECASE):
                                print(texto_conteudo + " --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario["Conteudo"][34]:
                            if re.findall(item, conteudo, re.IGNORECASE):
                                print(" --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario["Conteudo"][35]:
                            if re.findall(item, conteudo, re.IGNORECASE) and \
                                    re.findall("DO1", pub_name_secao, re.IGNORECASE):
                                print(" --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                        if item in dicionario["Conteudo"][36:fim]:
                            if re.findall(item, conteudo, re.IGNORECASE):
                                print(" --- " + arq)
                                if item not in lista_parametros:
                                    lista_parametros.append(item)
                                if arq not in artigos_encontrados:
                                    artigos_encontrados.append(arq)
                if len(lista_parametros) > 0:
                    parametros_busca[arq] = lista_parametros
    print("Busca Encerrada!")
    print(artigos_encontrados)
    print(parametros_busca)


def login():
    try:
        response = s.request("POST", url_login, data=payload, headers=headers)
        download()
    except requests.exceptions.ConnectionError:
        login()


def share_point_request():
    login()
    buscar_artigo(dicionario)

    client_id = ''
    tenant_id = ''

    app = PublicClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}")

    result = None
    accounts = app.get_accounts()
    if accounts:
        # If so, you could then somehow display these accounts and let end user choose
        print("Pick the account you want to use to proceed:")
        for a in accounts:
            print(a["username"])
        # Assuming the end user chose this one
        chosen = accounts[0]
        # Now let's try to find a token in cache for this account
        result = app.acquire_token_silent([f"https://bacen.sharepoint.com/.default"], account=chosen)

    if not result:
        # So no suitable token exists in cache. Let's get a new one from AAD.
        result = app.acquire_token_interactive(scopes=[f"https://bacen.sharepoint.com/.default"])

    if "access_token" in result:
        print(result["access_token"])  # Yay!
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))  # You may need this when reporting a bug

    for item in artigos_encontrados:
        with open(item, 'r', encoding="utf-8") as arquivo:
            conteudo_xml = arquivo.read()
            bs_texto = BeautifulSoup(conteudo_xml, 'xml')
            titulo_completo = bs_texto.find('Identifica').get_text().split(',')
            titulo = titulo_completo[0]
            escopo_completo = bs_texto.find('article').get('artCategory').split('/')
            escopo = escopo_completo[0]
            subescopo = ""
            if len(escopo_completo) > 1:
                sub = escopo_completo[1:]
                subescopo = str(sub).strip('[]').replace("', '", "/").replace("'", "")

            pub_name_secao = bs_texto.find('article').get('pubName')
            edicao = bs_texto.find('article').get('editionNumber')
            link_artigo = bs_texto.find('article').get('pdfPage')
            data_publicacao = bs_texto.find('article').get('pubDate').split("/")
            dia_pub = data_publicacao[0]
            mes_pub = data_publicacao[1]
            ano_pub = data_publicacao[2]
            data_utc = datetime.datetime.utcnow().replace(int(ano_pub), int(mes_pub), int(dia_pub))

            # Para assinatura, muda o xml para lxml:
            bs_texto_lxml = BeautifulSoup(conteudo_xml, 'lxml')
            # Extrai todas as ocorrências do cargo e da assinatura do arquivo xml caso existam:
            if bs_texto_lxml.find('p', {'class': 'assina'}):
                assinaturas = bs_texto_lxml.find_all('p', {'class': 'assina'})
            else:
                assinaturas = ""
            assinatura_str = list()
            for assinatura in assinaturas:
                assinatura_str.append(str(assinatura.get_text()))
            nova_assinatura = str(assinatura_str).strip('[]').replace("'", "")

            #Concatena o texto de um conjunto de arquivos xml que estão no formato xxx_xxxxxxxx_xxxxxxxx-x.xml:
            lista_arquivo_extenso = list()
            texto_conteudo = ""
            if re.findall('-1', item):
                for i in range(1, 10):
                    numero = item.find('-')
                    n = item[numero:numero + 2]
                    item = item.replace(n, f'-{i}')
                    lista_arquivo_extenso.append(item)
                for arquivo in lista_arquivo_extenso:
                    if os.path.isfile(arquivo):
                        with open(arquivo, 'r', encoding="utf-8") as a:
                            conteudo_xml = a.read()
                            bs_texto = BeautifulSoup(conteudo_xml, 'xml')
                            conteudo = bs_texto.find('Texto').get_text()
                            texto_limpo = re.sub('<[^>]+?>', ' ', conteudo).replace('"', '\\"')
                            texto_conteudo = texto_conteudo + texto_limpo
            else:
                conteudo = bs_texto.find('Texto').get_text()
                # Limpa o texto ao eliminar as tags e os atributos:
                texto_conteudo = re.sub('<[^>]+?>', ' ', conteudo).replace('"', '\\"')

            #Pega a ementa quando tiver no artigo:
            ementa = bs_texto.find('Ementa').get_text()
            #Ementa de despachos:
            if re.findall("Despacho", titulo, re.IGNORECASE) \
                    and re.findall("Banco Central", escopo, re.IGNORECASE) \
                    and re.findall("servidor", texto_conteudo, re.IGNORECASE):
                ementa = "Autoriza o afastamento do país."
            elif re.findall("Despacho", titulo, re.IGNORECASE) \
                    and re.findall("Banco Central", escopo, re.IGNORECASE):
                inicio_texto = texto_conteudo.find('autoriza')
                fim_texto = texto_conteudo.find('País') + len('País')
                ementa = texto_conteudo[inicio_texto:fim_texto].replace("autoriza", "Autoriza") + "."
            elif re.findall("Despacho", titulo, re.IGNORECASE) \
                    and re.findall("Presidência da República", escopo, re.IGNORECASE):
                inicio_texto = texto_conteudo.find('Exposição')
                paragrafo_interesse = texto_conteudo.find('Afastamento')
                fim_texto = texto_conteudo[paragrafo_interesse:].find(',') + paragrafo_interesse
                ementa = texto_conteudo[inicio_texto:fim_texto] + "."
            #Ementa de portarias:
            if re.findall("Portaria ME", titulo, re.IGNORECASE)\
                    and re.findall("Ministério da Economia", escopo, re.IGNORECASE) \
                    and re.findall(pub_name_secao, 'DO2', re.IGNORECASE):
                inicio_texto = texto_conteudo.find('Autorizar')
                frase_interesse = texto_conteudo.find('ocupante')
                fim_texto = texto_conteudo[frase_interesse:].find(',') + frase_interesse
                ementa_completa = texto_conteudo[inicio_texto:fim_texto].replace('Autorizar', 'Autoriza') + "."
                ementa = re.sub('[0-9]{1}[\.][0-9]{3}[\.][0-9]{3}[-][0-9]{1}[,]', '', ementa_completa).replace('matrícula', '').replace('nº', '')
            elif re.findall("Portaria", titulo, re.IGNORECASE) \
                    and re.findall("DO1", pub_name_secao, re.IGNORECASE) \
                    and not re.findall("Banco Central", escopo, re.IGNORECASE) \
                    and not re.findall("Ministério da Economia", escopo, re.IGNORECASE):
                paragrafos = bs_texto_lxml.find_all('p')
                for paragrafo in paragrafos:
                    if re.findall('Art\. 1º', str(paragrafo.get_text())):
                        ementa = str(paragrafo.get_text().replace('Art. 1º ', '').replace('Homologar', 'Homologa').replace('Divulgar', 'Divulga').replace('Autorizar', 'Autoriza').replace('Nomear', 'Nomeia').replace('Exonerar', 'Exonera').replace('Designar', 'Designa'))
            elif re.findall("Portarias", titulo, re.IGNORECASE) \
                    and not re.findall("Banco Central", escopo, re.IGNORECASE) \
                    and not re.findall("Ministério da Economia", escopo, re.IGNORECASE):
                paragrafos = bs_texto_lxml.find_all('p')
                ementa = ""
                for cargo_interesse in cargos_interesse["Cargos"]:
                    for paragrafo in paragrafos:
                        if re.findall(cargo_interesse, str(paragrafo.get_text()), re.IGNORECASE):
                            toda_ementa = str(paragrafo.get_text())
                            # o verbo que inicia a ementa, fica no parágrafo anterior
                            ind = paragrafos.index(paragrafo) - 1
                            toda_ementa = str(paragrafos[ind].get_text()).replace('NOMEAR', 'Nomeia').replace('HOMOLOGAR', 'Homologa').replace('EXONERAR', 'Exonera').replace('AUTORIZAR', 'Autoriza').replace('DIVULGAR', 'Divulga') + " " + toda_ementa
                            ementa = ementa + "\n\n" + toda_ementa
            #Ementa de extrato de ata:
            if re.findall("Extrato de Ata", titulo, re.IGNORECASE):
                inicio_texto = re.search('[0-9]{1}[\.][0-9]{3}', titulo)
                fim_texto = titulo.find(' REALIZADA')
                inicio = inicio_texto.span()[0]
                ementa = titulo[inicio:fim_texto] + "."
            #Ementa de extrato da seção 3:
            if re.findall("Extrato de Acordo", titulo, re.IGNORECASE):
                inicio_texto = texto_conteudo.find('Acordo')
                fim_texto = texto_conteudo[inicio_texto:].find('Objeto') + inicio_texto
                ementa = texto_conteudo[inicio_texto:fim_texto]
            elif re.findall("Extrato de Convênio", titulo, re.IGNORECASE):
                inicio_texto = texto_conteudo.find('Termo')
                fim_texto = texto_conteudo[inicio_texto:].find('Objeto') + inicio_texto
                ementa = texto_conteudo[inicio_texto:fim_texto]
            #Ementa de decreto:
            if re.findall("DECRETO", titulo, re.IGNORECASE) and ementa == "" \
                    and re.findall('DO2', pub_name_secao) \
                    and re.findall("Atos do Poder Executivo", escopo, re.IGNORECASE):
                if re.findall("DESIGNAR", texto_conteudo, re.IGNORECASE):
                    inicio_texto = texto_conteudo.find('DESIGNAR')
                    fim_texto = texto_conteudo[inicio_texto:].find('Brasília') + inicio_texto
                    ementa = texto_conteudo[inicio_texto:fim_texto].replace('DESIGNAR  ', 'Designa')
                elif re.findall("NOMEAR", texto_conteudo, re.IGNORECASE):
                    inicio_texto = texto_conteudo.find('NOMEAR')
                    fim_texto = texto_conteudo[inicio_texto:].find('Brasília') + inicio_texto
                    ementa = texto_conteudo[inicio_texto:fim_texto].replace('NOMEAR  ', 'Nomeia')
                elif re.findall("Autorizar", texto_conteudo, re.IGNORECASE):
                    inicio_texto = texto_conteudo.find('AUTORIZAR')
                    fim_texto = texto_conteudo[inicio_texto:].find('Brasília') + inicio_texto
                    ementa = texto_conteudo[inicio_texto:fim_texto].replace('AUTORIZAR  ', 'Autoriza')
                elif re.findall("EXONERAR", texto_conteudo, re.IGNORECASE):
                    inicio_texto = texto_conteudo.find('EXONERAR')
                    fim_texto = texto_conteudo[inicio_texto:].find('Brasília') + inicio_texto
                    ementa = texto_conteudo[inicio_texto:fim_texto].replace('EXONERAR  ', 'Exonera')
                elif re.findall("HOMOLOGAR", texto_conteudo, re.IGNORECASE):
                    inicio_texto = texto_conteudo.find('HOMOLOGAR')
                    fim_texto = texto_conteudo[inicio_texto:].find('Brasília') + inicio_texto
                    ementa = texto_conteudo[inicio_texto:fim_texto].replace('HOMOLOGAR  ', 'Homologa')

            #Pega os parâmetros das buscas pelo título, ementa, texto, escopo e assinatura:
            filtro_titulo = ""
            filtro_ementa = ""
            filtro_texto = ""
            filtro_assinatura = ""
            filtro_escopo = escopo
            for chave in parametros_busca.keys():
                if item == chave:
                    for filtro in parametros_busca[chave]:
                        if re.findall(filtro, titulo, re.IGNORECASE):
                            filtro_titulo = filtro_titulo + "\n\n" + str(filtro).replace('|', ' ou ').replace('(', '').replace(')', '').replace('[]', ' ')
                        if re.findall(filtro, ementa, re.IGNORECASE):
                            filtro_ementa = filtro_ementa + "\n\n" + str(filtro).replace('|', ' ou ').replace('(', '').replace(')', '').replace('.*?', '...')
                        if re.findall(filtro, texto_conteudo, re.IGNORECASE):
                            filtro_texto = filtro_texto + "\n\n" + str(filtro).replace('|', ' ou ').replace('(', '').replace(')', '').replace('.*?', '...')
                        if re.findall(filtro, nova_assinatura, re.IGNORECASE):
                            filtro_assinatura = filtro_assinatura + "\n\n" + str(filtro).replace('|', ' ou ').replace('(', '').replace(')', '').replace('[<]', '').replace(',', '-')
            print(filtro_assinatura)
            print(filtro_texto)
            print(filtro_ementa)
            print(filtro_titulo)
            print(filtro_escopo)

            print(f'********* {item} *********')

            headers = {'Authorization': f'Bearer {result["access_token"]}',
                        'Accept': 'application/json;odata=verbose',
                        'Content-Type': 'application/json;odata=verbose'}

            header_atualiza = {'Authorization': f'Bearer {result["access_token"]}',
                               'Accept': 'application/json;odata=verbose',
                               'Content-Type': 'application/json;odata=verbose',
                               'If-Match': '*',
                               'X-HTTP-Method': "MERGE"}

            # Requisição para buscar itens na lista do Sharepoint:
            r = requests.get("https://bacen.sharepoint.com/sites/sumula/_api/web/lists/GetByTitle('Artigos')/items",
                            headers=headers)
            #print(r.status_code)

            #Pegar o id de um item da lista no sharepoint pelo título para fazer a atualização:
            dados = r.json()
            lista_itens = dados['d']['results']
            tamanho = len(lista_itens)
            id = 0
            for n in range(0, tamanho):
                lista_item = lista_itens[n]
                if re.findall(titulo, lista_item['Title'], re.IGNORECASE) \
                        and re.findall(str(data_utc)[0:10], lista_item['Data']) \
                        and re.findall("Despacho", lista_item['Title'], re.IGNORECASE) \
                        and texto_conteudo == str(lista_item['Texto']).replace('"', '\\"'):
                    id = lista_item['ID']
                elif re.findall(titulo, lista_item['Title'], re.IGNORECASE) \
                        and re.findall(str(data_utc)[0:10], lista_item['Data']) \
                        and not re.findall("Despacho", lista_item['Title'], re.IGNORECASE):
                    id = lista_item['ID']

            is_update = False
            if id != 0: # nova inserção
                is_update = True

            data = '''{ "__metadata": {"type": "SP.Data.ArtigosListItem"},
                "Title": "%s",
                "Escopo": "%s",
                "Ementa": "%s",
                "Texto": "%s",
                "Assinatura": "%s",
                "Se_x00e7__x00e3_o": "%s",
                "Edi_x00e7__x00e3_o": "%s",
                "Data": "%s",
                "SubEscopo": "%s",
                "LinkArtigo": "%s",
                "IsUpdate": "%s"
            }''' % (titulo, escopo, ementa, texto_conteudo, nova_assinatura, pub_name_secao, edicao, data_utc, subescopo, link_artigo, is_update)

            if id == 0: # não encontrou nenhum item na data de hoje com o título do arquivo encontrado
                # Requisição para inserir itens na lista do Sharepoint:
                request_post = requests.post("https://bacen.sharepoint.com/sites/sumula/_api/web/lists/GetByTitle('Artigos')/items",
                                        headers=headers, data=data.encode('utf-8', 'ignore'))
                print(request_post.status_code)
                print("Artigo inserido na lista do sharepoint!")
                #print(request_post.content)
            else:
                # Requisição para atualizar itens na lista do Sharepoint:
                r_atualiza = requests.post(f"https://bacen.sharepoint.com/sites/sumula/_api/web/lists/GetByTitle('Artigos')/items({id})",
                                        headers=header_atualiza, data=data.encode('utf-8', 'ignore'))
                print(r_atualiza.status_code)
                print("Artigo já existe na lista do sharepoint!")


#login()
#buscar_artigo(dicionario)
share_point_request()
#data_anterior_util("2022-03-03")
#feriados()