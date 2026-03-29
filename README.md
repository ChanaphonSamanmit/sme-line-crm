# 🛒 OpenShop Retail: SME POS & LINE CRM

## 📌 Project Overview
OpenShop Retail is a smart Point of Sale (POS) and Customer Relationship Management (CRM) system designed for local SMEs. It bridges the offline-to-online gap by combining a fast web-based cashier system with a LINE Official Account integration for automatic loyalty point collection.

## 🚀 Key Features
* **Web POS Dashboard:** Fast checkout and real-time daily revenue calculation.
* **LINE QR Point API:** Automatically generates unique QR codes for customers to scan and claim points.
* **Interactive LINE Rich Menu:** Customers can instantly check their point balances and view promotions via the LINE chat.
* **LIFF Integration:** Seamless member profile detection using LINE Frontend Framework.

## 🛠️ Technology Stack
* **Frontend:** HTML, CSS, JavaScript (Bootstrap)
* **Backend:** Python (FastAPI)
* **Database:** Supabase (PostgreSQL)
* **Integrations:** LINE Messaging API, LINE Login (LIFF)

## ⚙️ How to Run Locally

**1. Clone the repository and install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Set up environment variables:**
Create a .env file in the root directory and add your API keys:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
LINE_CHANNEL_ACCESS_TOKEN=your_messaging_api_token
LINE_CHANNEL_SECRET=your_messaging_api_secret
<<<<<<< HEAD
=======
LIFF_URL=your_liff_url
>>>>>>> d434d997d3fb45e82604498a33a053a7d002bd97
```

**3. Start the FastAPI Server:**
```bash
uvicorn app.main:app --reload
```

**4. Start ngrok (for LINE Webhooks & LIFF):**
```bash
ngrok http 8000
```