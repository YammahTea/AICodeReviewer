from fastapi import HTTPException
import httpx

# check
# https://docs.github.com/en/rest/issues/comments?apiVersion=2022-11-28#create-an-issue-comment
# for documentation and required parameters

async def post_comment(ai_response, repo_full_name, pr_number, access_token):
  
  # GitHub endpoint for posting a comment on an issue/pr
  comment_url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
  
  comment_headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {access_token}",
    "X-GitHub-Api-Version": "2022-11-28"
  }
  
  comment_data = {
    "body": ai_response
  }
  
  # the comment request
  async with httpx.AsyncClient() as client:
    comment_response = await client.post(comment_url, headers=comment_headers, json=comment_data)
  
  if comment_response.status_code == 201:
    print("Posted the AI review to github")
    
  else:
    raise HTTPException(status_code=comment_response.status_code,
                        detail=comment_response.text)