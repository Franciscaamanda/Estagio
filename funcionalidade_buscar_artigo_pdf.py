from datetime import date
import requests
import re
import PyPDF2

login = ""
senha = ""

## Tipos de Diários Oficiais da União permitidos: do1 do2 do3 (Contempla as edições extras) ##
tipo_dou = "do1 do2 do3"

# Montagem da URL:
ano = date.today().strftime("%Y")
mes = date.today().strftime("%m")
dia = date.today().strftime("%d")
data_completa = ano + "-" + mes + "-" + dia

url_login = "https://inlabs.in.gov.br/logar.php"
url_download = "https://inlabs.in.gov.br/index.php?p="

payload = {"email": login, "password": senha}
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}
s = requests.Session()


def download():
    if s.cookies.get('inlabs_session_cookie'):
        cookie = s.cookies.get('inlabs_session_cookie')
    else:
        print("Falha ao obter cookie. Verifique suas credenciais")
        exit(37)

    # Download inicial
    for dou_secao in tipo_dou.split(' '):
        print("Aguarde Download...")
        url_arquivo = url_download + data_completa + "&dl=" + ano + "_" + mes + "_" + dia + "_ASSINADO_" + dou_secao + ".pdf"
        cabecalho_arquivo = {'Cookie': 'inlabs_session_cookie=' + cookie, 'origem': '736372697074'}
        response_arquivo = s.request("GET", url_arquivo, headers=cabecalho_arquivo)
        if response_arquivo.status_code == 200:
            with open(data_completa + "-" + dou_secao + ".pdf", "wb") as f:
                f.write(response_arquivo.content)
                print("Arquivo %s salvo." % (ano + "_" + mes + "_" + dia + "_ASSINADO_" + dou_secao + ".pdf"))
                del response_arquivo
                del f
        elif response_arquivo.status_code == 404:
            print("Arquivo não encontrado: %s" % (ano + "_" + mes + "_" + dia + "_ASSINADO_" + dou_secao + ".pdf"))
    print("Aplicação encerrada")


def buscar_palavras(padrao):
    for dou_secao in tipo_dou.split(' '):
        nome_arquivo = data_completa + "-" + dou_secao + ".pdf"
        print(f"Procurando ocorrências da palavra {padrao} no arquivo {nome_arquivo}...")
        with open(nome_arquivo, 'rb') as arquivo:
            texto = PyPDF2.PdfReader(arquivo)
            num = texto.numPages
            #Extrai o texto do arquivo por página:
            for i in range(0, num):
                page = texto.pages[i]
                page.extract_text()
                x = page.extract_text()
                #Verifica se o artigo contém a palavra pesquisada:
                if re.findall(padrao, x, re.IGNORECASE):
                    print(f"Ocorrências encontradas da palavra {padrao} no arquivo {nome_arquivo}:")
                    print(f"Página {i + 1}:")
                    #Imprime o texto do artigo:
                    print(x)
            print(f"Busca Encerrada no Arquivo {nome_arquivo}!")
    print("Procedimento Encerrado!")


def login():
    try:
        response = s.request("POST", url_login, data=payload, headers=headers)
        download()
    except requests.exceptions.ConnectionError:
        login()


login()
buscar_palavras("O MINISTRO DE ESTADO DA AGRICULTURA")