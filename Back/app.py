from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager

from google import genai
from google.genai import types

from dotenv import load_dotenv
import httpx
import os

# Modules
from Back.auth import get_access_token
from Back.comment import post_comment

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
@asynccontextmanager
async def lifespan(app: FastAPI):
  # the encoding argument has to be there cuz there are emojis in the system prompt (or u will get errors)
  # and the base dir too, or u will get "FileNotFoundError"
  with open(os.path.join(BASE_DIR, "prompts/reviewer.md"), "r", encoding="utf-8") as file:
    app.state.system_prompt = file.read()
  
  yield

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def receive_github_webhook(
        request: Request
):
  event_type = request.headers.get("X-GitHub-Event")
  payload = await request.json()
  
  if event_type == "ping":
    return {"status": "ping received"}
  
  if event_type == "pull_request":
    action = payload.get("action")
    
    # only review the pr when it is opened or updated (synchronize)
    if action in ["opened", "synchronize"]:
      pr_number = payload["pull_request"]["number"]
      diff_url = payload["pull_request"]["diff_url"]
      
      print(f"\nFetching code for pullrequest number: {pr_number}")
      
      # to get the code changes
      # follow_redirects or u will get 302 status code
      # as github redirects the request
      async with httpx.AsyncClient(follow_redirects=True) as cli:
        response = await cli.get(diff_url)
        
      if response.status_code == 200:
        diff_text = response.text
        
          
        # api call + with the system prompt
        ai_response = client.models.generate_content(
          model="gemini-2.5-flash",
          contents=f"Review this code diff:\n {diff_text}",
          config=types.GenerateContentConfig(
            system_instruction=request.app.state.system_prompt,
            temperature=0.1 # lower temperature makes it analytical and less "creative"
          )
        )
        
        # get the installation id in the webhook for the repo the app is installed on
        install_id = payload["installation"]["id"]
        
        # get the access token to be able to post the comment
        access_token = await get_access_token(installation_id=install_id)
        
        # post the comment on the pullrequest
        await post_comment(
          ai_response= ai_response.text,
          repo_full_name= payload["repository"]["full_name"],
          pr_number= pr_number,
          access_token= access_token
          
        )
        
      else:
        raise HTTPException(status_code=response.status_code, detail="Something went wrong")
      
  return {"status": "success"}