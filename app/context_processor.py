from .views import api_request
import os

API_URL = os.getenv("API_URL")

def user_context(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return {}

    resp = api_request(request, "GET", f"{API_URL}/user/{user_id}")
    if resp and resp.status_code == 200:
        return {"user_name": resp.json().get("name")}

    return {}
