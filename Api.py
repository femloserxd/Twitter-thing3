import os
import requests
import base64
from flask import Flask, request, redirect, jsonify
from requests_oauthlib import OAuth1Session

# 🔑 Credenciais da API do Twitter (pegar no Developer Portal)
API_KEY = os.getenv("nPPvHphiR1czKevRmzzYs9sxl")
API_SECRET = os.getenv("d9PKRUSissrcjImsLfvGFz1smdt1XFkajXh1CouYcQJIsKB1CK")
CALLBACK_URL = os.getenv("https://emily-ai.vercel.app/")  # URL do seu app no Vercel

# 🔗 URLs da API do Twitter para autenticação e atualização do perfil
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZATION_URL = "https://api.twitter.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
URL_PROFILE_IMAGE = "https://api.twitter.com/1.1/account/update_profile_image.json"
URL_BANNER = "https://api.twitter.com/1.1/account/update_profile_banner.json"
URL_PROFILE_INFO = "https://api.twitter.com/1.1/account/update_profile.json"

# 📷 Arquivos de imagem (coloque esses arquivos no Vercel)
PROFILE_IMAGE_PATH = "profile.jpg"
BANNER_IMAGE_PATH = "banner.png"

# 🔄 Função para converter imagens para Base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# 🚀 Criando a aplicação Flask
app = Flask(__name__)

# 🌍 Rota para iniciar a autorização
@app.route("/authorize")
def authorize():
    oauth = OAuth1Session(API_KEY, client_secret=API_SECRET, callback_uri=CALLBACK_URL)
    response = oauth.fetch_request_token(REQUEST_TOKEN_URL)

    oauth_token = response.get("oauth_token")
    authorization_url = f"{AUTHORIZATION_URL}?oauth_token={oauth_token}"

    return redirect(authorization_url)

# 🔄 Rota para processar o retorno da autorização
@app.route("/callback")
def callback():
    oauth_token = request.args.get("oauth_token")
    oauth_verifier = request.args.get("oauth_verifier")

    oauth = OAuth1Session(API_KEY, client_secret=API_SECRET, resource_owner_key=oauth_token)
    oauth_tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL, verifier=oauth_verifier)

    access_token = oauth_tokens.get("oauth_token")
    access_secret = oauth_tokens.get("oauth_token_secret")

    # Atualiza o perfil do usuário autorizado
    update_twitter_profile(access_token, access_secret)

    return "✅ Perfil atualizado com sucesso!"

# 🔄 Função para atualizar o perfil do usuário
def update_twitter_profile(access_token, access_secret):
    auth = OAuth1Session(API_KEY, client_secret=API_SECRET, resource_owner_key=access_token, resource_owner_secret=access_secret)

    # Atualizar foto de perfil
    profile_image_base64 = encode_image(PROFILE_IMAGE_PATH)
    requests.post(URL_PROFILE_IMAGE, auth=auth, data={"image": profile_image_base64})

    # Atualizar banner
    banner_image_base64 = encode_image(BANNER_IMAGE_PATH)
    requests.post(URL_BANNER, auth=auth, data={"banner": banner_image_base64})

    # Atualizar nome com variante
    new_name = generate_unique_name("Emily's puppy")
    requests.post(URL_PROFILE_INFO, auth=auth, data={"name": new_name, "description": "A little good Emily's puppy account. 🐾"})

# 🔢 Função para gerar um nome único com contador
def generate_unique_name(base_name):
    counter = 1
    return f"{base_name} - {str(counter).zfill(4)}"

# 🚀 Rota principal
@app.route("/")
def home():
    return "✅ O bot está rodando no Vercel! Acesse /authorize para iniciar."

if __name__ == "__main__":
    app.run(debug=True)
