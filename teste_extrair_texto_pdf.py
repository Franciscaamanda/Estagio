import PyPDF2
from datetime import date

ano = date.today().strftime("%Y")
mes = date.today().strftime("%m")
dia = date.today().strftime("%d")
data_completa = ano + "_" + mes + "_" + dia

tipo_dou = ["_do3", "_do2", "_do3"]

def download():
    with open("Artigo.pdf", 'rb') as arquivo:
            print("Aguarde o Download...")
            texto = PyPDF2.PdfReader(arquivo)
            num = texto.numPages
            for i in range(0, num):
                page = texto.pages[i]
                print(page.extract_text())
            print("Download Completo!")

download()


