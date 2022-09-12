from datetime import date
import requests
import zipfile
import os
from bs4 import BeautifulSoup
import re
import numpy as np

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
                        "Banco Central do Brasil",
                        "Conselho de Controle de Atividades Financeiras",
                        "Presidência da República"], #novo
              "Titulo": ["Resolução Coremec",
                         "([ ]CMN[ ])|([ ]CMN[0-9])",
                         "PORTARIA SETO",
                         "Resolução BCB",
                         "Instrução Normativa BCB",
                         "Despachos do Presidente da República"],
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
                         "(Poder (.*?Executivo))|(Poderes (.*?Executivo))"],
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
                           "(Exposição de Motivos ((.*?afastamento )(.*?Ministro de Estado da Economia))) | (Exposições de Motivos ((.*?afastamento )(.*?Ministro de Estado da Economia))) | (Exposição de Motivos ((.*?férias )(.*?Ministro de Estado da Economia))) | (Exposições de Motivos ((.*?férias )(.*?Ministro de Estado da Economia)))"
                           "((A Diretora) | (O Diretor)) de Administração do Banco Central do Brasil",
                           "((PORTARIA)(.*?O MINISTRO DE ESTADO DA ECONOMIA)(.*?afastamento)(.*?Banco Central))",
                           "Despacho do Presidente do Banco Central do Brasil",
                           "Comissão Técnica da Moeda e do Crédito",
                           "Secretário-Executivo Adjunto da Secretaria-Executiva do Ministério do Trabalho e Previdência",
                           "Comitê de Regulação e Fiscalização dos Mercados Financeiro, de Capitais, de Seguros, de Previdência e Capitalização",
                           "temas jurídicos relevantes para a administração pública",
                           "cargo de Secretária Especial Adjunta da Secretaria Especial de Comércio Exterior e Assuntos Internacionais do Ministério da Economia"] #novo
              } #código DAS 101.6


def buscar_artigo(dicionario):
    for dou_secao in tipo_dou.split(' '):
        nome_arquivo = data_completa + "-" + dou_secao + ".zip"
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
                    # Faz a busca pelo atributo artCategory:
                    if True in np.isin(dicionario['Escopo'][1], escopo.split('/')) and titulo is not None:
                        nova_lista.append(file)
                    elif True in np.isin(dicionario['Escopo'][5], escopo.split('/')) \
                            and re.findall("DO1", pub_name_secao, re.IGNORECASE) \
                            and re.findall("Portaria", tipo_normativo, re.IGNORECASE):
                        nova_lista.append(file)
                    elif True in np.isin(dicionario['Escopo'][0], escopo.split('/')) \
                            or True in np.isin(dicionario['Escopo'][2:5], escopo.split('/')) \
                            or True in np.isin(dicionario['Escopo'][6], escopo.split('/')):
                        nova_lista.append(file)
            #arquivos encontrados pelo escopo
            for arq in nova_lista:
                with open(arq, 'r', encoding="utf-8") as arquivo:
                    conteudo_xml = arquivo.read()
                    bs_texto = BeautifulSoup(conteudo_xml, 'xml')
                    # Extrai o conteúdo do identifica do arquivo xml:
                    titulo = bs_texto.find('Identifica').get_text()
                    ementa = bs_texto.find('Ementa').get_text()
                    texto = bs_texto.find('Texto').get_text()
                    # Faz a busca pelo atributo artCategory:
                    for item in dicionario['Titulo']:
                        if item in dicionario['Titulo'][2]:
                            if re.findall(item, titulo, re.IGNORECASE) \
                                    and (re.findall("Banco Central", ementa, re.IGNORECASE) or
                                         re.findall("Banco Central", texto, re.IGNORECASE)):
                                print(titulo + " --- " + arq)
                        else:
                            if re.findall(item, titulo, re.IGNORECASE):
                                print(titulo + " --- " + arq)
                with open(arq, 'r', encoding="utf-8") as arquivo:
                    conteudo_xml = arquivo.read()
                    bs_texto = BeautifulSoup(conteudo_xml, 'xml')
                    # Extrai o conteúdo da ementa do arquivo xml:
                    ementa = bs_texto.find('Ementa').get_text()
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
                        elif item in dicionario['Ementa'][19]:
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
                        else:
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
                    #Faz a busca pelo atributo Texto:
                    for item in dicionario['Conteudo']:
                        if item in dicionario['Conteudo'][18] or item in dicionario['Conteudo'][19]:
                            if texto_conteudo.find('Exposição de Motivos'):
                                inicio_busca = texto_conteudo.find('Exposição de Motivos')
                                fim_busca = inicio_busca + len('Exposição de Motivos') + 200
                            elif texto_conteudo.find('Exposições de Motivos'):
                                inicio_busca = texto_conteudo.find('Exposições de Motivos')
                                fim_busca = inicio_busca + len('Exposições de Motivos') + 200
                            if re.findall(item, conteudo, re.IGNORECASE) \
                                    and re.findall(item, conteudo[inicio_busca:fim_busca], re.IGNORECASE):
                                print(texto_conteudo + " --- " + arq)
                        elif item in dicionario['Conteudo'][22]:
                            padrao = 'Presidente do COAF'
                            if re.findall(item, conteudo, re.IGNORECASE) \
                                    and re.findall(padrao, conteudo, re.IGNORECASE):
                                print(texto_conteudo + " --- " + arq)
                        else:
                            if re.findall(item, conteudo, re.IGNORECASE):
                                print(texto_conteudo + " --- " + arq)
    print("Busca Encerrada!")


def login():
    try:
        response = s.request("POST", url_login, data=payload, headers=headers)
        download()
        #selecionar_data('09', '09', '2022')
        #selecionar_secao('DO1')
    except requests.exceptions.ConnectionError:
        login()


login()
buscar_artigo(dicionario)