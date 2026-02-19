from fastapi import FastAPI, Request, status, HTTPException
import httpx

app = FastAPI()

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
      
      print(f"pull req number: {pr_number}")
      print(f"pull req diff url: {diff_url}")
      
      # to get the code changes
      # follow_redirects or u will get 302 status code
      # as github redirects the request
      async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(diff_url)
        
      if response.status_code == 200:
        diff_text = response.text
        
        print(diff_text) # first 200 chars, just for testing
      
      else:
        raise HTTPException(status_code=response.status_code, detail="Something went wrong")
      
  return {"status": "success"}
  