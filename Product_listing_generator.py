from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai


gemini_api_key = "AIzaSyAAg7EDAXW_-Wo_z1fguYCUqzEls6m5rUo"
genai.configure(api_key=gemini_api_key)

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)


app = Flask(__name__)

def extract_product_info(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        
        if "instagram.com" in url:
            title = soup.find("meta", property="og:title")["content"]
            description = soup.find("meta", property="og:description")["content"]
            return {"title": title, "description": description}

        
        elif "youtube.com" in url or "youtu.be" in url:
            title = soup.find("meta", property="og:title")["content"]
            description = soup.find("meta", property="og:description")["content"]
            return {"title": title, "description": description}

        
        else:
            return {"title": "Unsupported URL", "description": "This URL type is not supported."}

    except Exception as e:
        return {"title": "Error", "description": str(e)}


def generate_listing(title, description):
    prompt = f"""
    Generate a professional Amazon product listing:
    Title: {title}
    Description: {description}
    Include:
    1. Catchy product title
    2. Detailed description
    3. 5 key features
    4. Recommended price
    """
    response = model.generate_content(prompt)
    return response.text


HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Product Listing Generator</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center">PRODUCT LISTING GENERATOR</h1>
        <form method="POST">
            <div class="mb-3">
                <label for="url" class="form-label">Enter URL</label>
                <input type="url" class="form-control" id="url" name="url" placeholder="Instagram/YouTube URL" required>
            </div>
            <button type="submit" class="btn btn-primary">Generate</button>
        </form>
    </div>
</body>
</html>
"""

HTML_RESULT = """
<!DOCTYPE html>
<html>
<head>
    <title>Generated Listing</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center">Generated Product Listing</h1>
        <div class="card mt-4">
            <div class="card-body">
                <pre>{{ listing }}</pre>
            </div>
        </div>
        <a href="/" class="btn btn-secondary mt-3">Go Back</a>
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        url = request.form.get("url")
        product_info = extract_product_info(url)
        if product_info:
            listing = generate_listing(product_info["title"], product_info["description"])
            return render_template_string(HTML_RESULT, listing=listing)
    return render_template_string(HTML_FORM)

if __name__ == "__main__":
    app.run(debug=True)
