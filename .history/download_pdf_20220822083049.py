import PyPDF2
from datetime import date
import requests

login = "franciscaamanda843@gmail.com"
senha = "0911Af@1"

url_login = "https://inlabs.in.gov.br/logar.php"
url_download = "https://inlabs.in.gov.br/index.php?p="

payload = {"email": login, "password": senha}
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

s = requests.Session()

ano = date.today().strftime("%Y")
mes = date.today().strftime("%m")
dia = date.today().strftime("%d")
data_completa = ano + "-" + mes + "-" + dia

tipo_dou = ["do1", "do2", "do3"]


def download():
    if s.cookies.get('inlabs_session_cookie'):
        cookie = s.cookies.get('inlabs_session_cookie')
    else:
        print("Falha ao obter cookie. Verifique suas credenciais");
        #exit(37)
    for dou_secao in tipo_dou:
        url_arquivo = url_download + data_completa + "&dl=" + ano + "_" + mes + "_" + dia + "_ASSINADO_" + dou_secao + ".pdf"
        cabecalho_arquivo = {'Cookie': 'inlabs_session_cookie=' + cookie, 'origem': '736372697074'}
        response_arquivo = s.request("GET", url_arquivo, headers=cabecalho_arquivo)
        #response_arquivo = s.request("GET", url_arquivo)
        #response_arquivo = requests.get(url_arquivo)
        if response_arquivo.status_code == 200:
            with open(ano + "_" + "mes" + "_" "dia" + "_" + "ASSINADO" + "_" + dou_secao + ".pdf", 'rb') as arquivo:
                print("Aguarde o Download...")
                texto = PyPDF2.PdfReader(arquivo)
                num = texto.numPages
                for i in range(0, num):
                    page = texto.pages[i]
                    print(page.extract_text(0))
                print("Download Completo!")
        elif response_arquivo.status_code == 404:
            print("Arquivo não encontrado.")
        else:
            print("Erro")
    exit(0)


download()
def login():
    try:
        response = s.request("POST", url_login, data=payload, headers=headers)
#        response = s.request("POST", url_login, data=payload)
        download()
    except requests.exceptions.ConnectionError:
        login()


login()