# Create your views here.
import json
import os

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPEN_ROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1"
)
products = [
    {
        "id": 1,
        "name": "iPhone 17",
        "price": 799,
        "description": "Premium Apple smartphone",
    },
    {
        "id": 2,
        "name": "Samsung A55",
        "price": 450,
        "description": "Midrange Android phone",
    },
    {
        "id": 3,
        "name": "Pixel 8a",
        "price": 499,
        "description": "Google smartphone with great camera",
    },
    {
        "id": 4,
        "name": "OnePlus 13R",
        "price": 549,
        "description": "Fast Android phone with large battery",
    },
    {
        "id": 5,
        "name": "Nothing Phone 3",
        "price": 479,
        "description": "Stylish Android phone with clean software",
    },
]


catalog = "\n".join(
    [f"{p['id']} - {p['name']} - ${p['price']} - {p['description']}" for p in products]
)


def home(request):
    return render(request, "index.html", {"products": products})


@csrf_exempt
def recommend(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    body = json.loads(request.body)
    preference = body.get("preference")
    prompt = f"""
Available products:

{catalog}

User request:
{preference}

Recommend ONLY products from the list.

If matching products exist, return:

### Product Name

Price: $XXX

Why it matches:
- Reason 1
- Reason 2

### Product Name

Price: $XXX

Why it matches:
- Reason 1
- Reason 2

If no matching products exist, return ONLY:

Sorry, there are no products matching your requirements.

Do NOT output:
- Recommendations
- ## Recommendations
- Any introduction
- Any conclusion

Maximum 2 products.
Use proper markdown.
"""
    try:
        response = client.chat.completions.create(
            model="cohere/north-mini-code:free",
            messages=[{"role": "user", "content": prompt}],
            timeout=10,
        )

    except Exception as e:
        return JsonResponse({"recommendations": str(e)}, status=500)
    recommendation_text = response.choices[0].message.content
    return JsonResponse({"recommendations": recommendation_text})
