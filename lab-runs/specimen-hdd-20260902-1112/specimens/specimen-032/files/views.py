from django.http import HttpResponse
import datetime

def cache_demo(request):
    resp = HttpResponse(f"Current content at {datetime.datetime.now()}")
    resp["Cache-Control"] = "no-store"
    return resp
