from fastapi import FastAPI, Request


app = FastAPI()

@app.post("/webhook")
async def receive_github_webhook(
        request: Request
):
  event_type = request.headers.get("X-GitHub-Event")
  
  payload = await request.json()
  
  if event_type == "ping":
    zen_message = payload.get("zen")
    print(f"github zen: {zen_message}")
    return {"status": "ping received"}
  
  action = payload.get("action") # example: pull req
  print(f"Action type: {action}")
  
  return {"status": "success"}
  