from fastapi import HTTPException
from dotenv import load_dotenv
import os
import time
import jwt
import httpx

load_dotenv()

client_id = os.getenv("CLIENT_ID")
raw_key = os.getenv("PRIVATE_KEY")
signing_key = raw_key.replace("\\n", "\n") #


def create_jwt():
  # check
  # https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app#about-json-web-tokens-jwts
  # for the documentation and required parameters
  
  payload = {
    'iat': int(time.time()),
    'exp': int(time.time()) + 600,
    'iss': client_id
  }
  
  # create JWT
  encoded_jwt = jwt.encode(payload, signing_key, algorithm='RS256')
  
  return encoded_jwt


async def get_access_token(installation_id): # the installation id comes from the webhook payload in app.py
  
  # 1- Create the jwt token
  jwt_token = create_jwt()
  
  # 2- Grab the installation ID
  # note: the installation ID is where the app is installed on the repos (diff for every repo) but same app id
  token_url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
  
  headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {jwt_token}",
    "X-GitHub-Api-Version": "2022-11-28"
  }
  
  async with httpx.AsyncClient() as client:
    
    response = await client.post(token_url, headers=headers)
    
  if response.status_code == 201:
    access_token = response.json()["token"]
    
    return access_token
  
  else:
    raise HTTPException(status_code=response.status_code,
                        detail=response.text)