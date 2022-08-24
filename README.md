Este projeto contém funcionalidades aplicadas aos arquivos do sistema de Imprensa Nacional - INLABS

# __Funcionalidades__:

1- Extrair texto dos arquivos em PDF;

2- Buscar palavras nos arquivos em PDF (funcionalidade semelhante ao Ctrl + F).

# __Pré-Requisitos__:

É necessário rodar os seguintes comandos no terminal para que o código execute corretamente: 
>>pip install --upgrade certifi
>
>>pip install requests
>
>>pip install PyPDF2

As instruções abaixo descrevem o passo a passo para exportar o certificado digital do sistema no navegador Google Chrome, 
sendo este procedimento fundamental para permitir o download dos arquivos.

Passo 1 - Executar os seguintes comandos no terminal para localizar o diretório do arquivo cacert.pem referente a
biblioteca certifi do Python:

>>python
>
>>import certifi
>
>>certifi.where()

Passo 2 - Abra a url "https://inlabs.in.gov.br/logar.php" no navegador;

Passo 3 - Clique no ícone cadeado -> "A ligação é segura" -> "O certificado é válido";


Passo 4 - Logo em seguida, abrirá uma janela contendo algumas informações acerca do certificado digital,
clique na aba "Certificação";

Passo 5 - Neste item, aparecem 3 certificados, clique no "Autoridade Certificadora Raiz Brasileira v10" e logo em seguida, 
selecione o botão "Exibir Certificado";

Passo 6 - Com isto, aparecerá uma nova janela contendo as informações deste certificado. Clique em "Detalhes" e, no item 
"Mostrar" deixe definido a opção "Todas" e clique no botão "Copiar para Arquivo...";

Passo 7 - Aparecerá disponível uma nova janela, clique em "Avançar";

Passo 8 - No formato do arquivo de exportação, marque a opção "codificado na base 64 (*.cer)" e depois clique em 
"Avançar";

Passo 9 - Selecione o local em que salvará o arquivo e salve na mesma pasta que está o arquivo cacert.pem e clique em 
"Avançar";

Passo 10 - Faça o mesmo procedimento para o certificado "Autoridade Certificadora do SERPRO SSLv1" em "Caminho de
Certificação";

Passo 11 - Esta operação só é necessária nos dois certificados mencionados acima;

Passo 12 - Tendo os certificados salvos, copiei todas as informações contidas nos arquivos e salve-as no final do arquivo
cacert.pem.