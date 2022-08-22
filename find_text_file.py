import PyPDF2
import re

def download():
    with open("Artigo.pdf", 'rb') as arquivo:
        print("Aguarde o Download...")
        texto = PyPDF2.PdfReader(arquivo)
        num = texto.numPages
        for i in range(0, num):
            page = texto.pages[i]
            page.extract_text()
            padrao = "RH"
            x = page.extract_text()
            resultado = re.findall(padrao, x)
            print(resultado)
        print("Download Completo!")

download()