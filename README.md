# Manifest AI 

This tool creates a personalized web experience in three steps:

1. **Scrape**  
   Data is collected from websites using **Selenium**.

2. **Enrich**  
   The scraped data is enhanced using **Gemini** (Google's generative AI) for deeper insights.

3. **Personalize**  
   A custom **JavaScript snippet** is generated and saved as a bookmarklet.  
   When clicked, it personalizes the target website based on the enriched user data.

---

Us in action: 

![2025-05-18 12 26 18](https://github.com/user-attachments/assets/c4cd48ad-9b08-42f8-82a7-62c71cfe56e9)

---
Local Run Instructions

### 1. Install dependencies

Make sure you have Python installed, then install the required packages:

```bash
pip install -r requirements.txt
```

Start the app by running:

```bash
python app.py
```

Test the endpoints: 
```bash
curl -X POST http://127.0.0.1:8080/get_image_data \
     -H "Content-Type: application/json" \
     -d '{"website_url": "https://www.azazie.com/gb/products/harmony-mauve-floral-maxi-dress-atelier-dress/6586582?sourceTag=atelier_formal_dresses", "user_prompt": "I am interested in dresses made from natural materials"}'
```


