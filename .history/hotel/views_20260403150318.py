import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from service.prompt import GeminiService


try:
    ai_service = GeminiService()
    startup_error = ""
except Exception as exc:
    ai_service = None
    startup_error = str(exc)


def home(request):
L
    return render(request, "hotel/index.html", {"rooms": rooms})


@csrf_exempt
def assistant_chat(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    if ai_service is None:
        return JsonResponse({"detail": f"AI service unavailable: {startup_error}"}, status=500)

    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
        message = (payload.get("message") or "").strip()
        if not message:
            return JsonResponse({"detail": "message is required"}, status=400)

        response = ai_service.generate_response(message)
        return JsonResponse({"response": response})
    except Exception as exc:
        return JsonResponse({"detail": f"Failed to generate response: {exc}"}, status=500)
