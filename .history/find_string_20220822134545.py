import PyPDF2


def download():
    with open("Artigo.pdf", 'rb') as arquivo:
            print("Aguarde o Download...")
            texto = PyPDF2.PdfReader(arquivo)
            num = texto.numPages
            for i in range(0, num):
                page = texto.pages[i]
                print(page.extract_text())
            print("Download Completo!")

#download()

pat = "RH"
text = "RBCRHJKRH"

#indice = text.index(pat,5)
#print(f"Encontrado a partir do índice {indice}")
indices = list()
#for i in range(0,len(text)-1):
#    indice = text.index(pat,i)
#    if indice not in indices:
#        indices.append(indice)
#print(indices)
generator = (text.index(pat, i) for i in range(0, len(text)-1))

for i in generator:
    if i not in indices:
        indices.append(i)
print(indices)
