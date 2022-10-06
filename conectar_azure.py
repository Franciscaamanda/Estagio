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
if "access_token" in result:
    print(result["access_token"])  # Yay!
else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug

headers = {'Authorization': f'Bearer {result["access_token"]}'}

#Requisição para buscar itens na lista do Sharepoint:
r = requests.get("https://bacen.sharepoint.com/sites/sumula/_api/web/lists/GetByTitle('Artigos')/items", headers=headers)
print(r.status_code)

#Requisição para obter o FullEntityTypeFullName:
request = requests.get("https://bacen.sharepoint.com/sites/sumula/_api/web/lists/GetByTitle('Artigos')?select=ListItemEntityTypeFullName",
             headers=headers)
print(request.content)
list_entity_type_full_name = 'SP.Data.ArtigosListItem'
#Requisição para inserir itens na lista do Sharepoint:
#requests.post("https://bacen.sharepoint.com/sites/sumula/_api/web/lists/GetByTitle('Artigos')/items")