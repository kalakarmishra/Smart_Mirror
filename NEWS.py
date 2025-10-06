import requests

NEWS_API_KEY ="73cae16a679b4df090ef1c6e918c4989"
#url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"

response = requests.get(url)
print("HTTP Status Code:", response.status_code)

data = response.json()
print("Full Response:", data)  # See what exactly is returned

if data.get("status") == "ok":
    articles = data.get("articles", [])
    print("Top News:")
    if articles:
        for i, article in enumerate(articles[:5], start=1):
            print(f"{i}. {article['title']}")
    else:
        print("No news articles found.")
else:
    print("Error:", data.get("message"))
