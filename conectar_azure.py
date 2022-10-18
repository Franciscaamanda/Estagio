from msal import PublicClientApplication
import requests

client_id = ''
tenant_id = ''

app = PublicClientApplication(
    client_id,
    authority=f"https://login.microsoftonline.com/{tenant_id}")

print(app.authority.tenant)
result = None
accounts = app.get_accounts()
print(accounts)
#auth_code_flow = app.initiate_auth_code_flow(scopes=["User.Read"],
#                                             redirect_uri="http://localhost")
#print(auth_code_flow)
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
#scope: f"https://bacen.sharepoint.com/.default"
if "access_token" in result:
    print(result["access_token"])  # Yay!
else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug

headers = {'Authorization': f'Bearer {result["access_token"]}',
            'Accept': 'application/json;odata=verbose',
            'Content-Type': 'application/json;odata=verbose'}

#Requisição para buscar itens na lista do Sharepoint:
r = requests.get("https://bacen.sharepoint.com/sites/sumula/_api/web/lists/GetByTitle('Artigos')/items", headers=headers)
print(r.status_code)
print(r.headers)
print(r.encoding)
#print(r.content)

#Requisição para obter o FullEntityTypeFullName:
request = requests.get("https://bacen.sharepoint.com/sites/sumula/_api/web/lists/GetByTitle('Artigos')?select=ListItemEntityTypeFullName",
             headers=headers)
print(request.content)
print(request.apparent_encoding)
list_entity_type_full_name = 'SP.Data.ArtigosListItem'
#Requisição para inserir itens na lista do Sharepoint:
#content-type: application/atom+xml;type=feed;charset=utf-8
#data = {"__metadata": {"type": "SP.Data.ArtigosListItem"},"Title": "Teste"}
titulo = "é"
data = '''{ "__metadata": {"type": "SP.Data.ArtigosListItem"},
    "Title": "%s",
    "Escopo": "Escopo 1"
}''' % (titulo)
#"__metadata": {"type": "SP.Data.ArtigosListItem"}
#request_post = requests.post("https://bacen.sharepoint.com/sites/sumula/_api/web/lists/GetByTitle('Artigos')/items",
#                        headers=headers, data=data.encode('utf-8', 'ignore'))
#print(request_post.status_code)
#print(request_post.encoding)
#print(request_post.apparent_encoding)