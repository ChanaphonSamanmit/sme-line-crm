# 🛒 OpenShop Retail
**An Open-Source SME POS & LINE CRM System**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E.svg)

## 📌 Project Overview
OpenShop Retail is a smart Point of Sale (POS) and Customer Relationship Management (CRM) system designed to empower local SMEs. It bridges the offline-to-online digital gap by combining a fast, cloud-native web cashier system with a zero-friction LINE Official Account integration for automated customer loyalty management.

## 🚀 Core Features
* **Browser-Based POS Dashboard:** Fast checkout system with real-time daily revenue tracking and analytics, requiring zero hardware installation.
* **Frictionless QR Loyalty API:** Automatically generates dynamic QR codes for customers to scan and claim points seamlessly.
* **Interactive LINE Rich Menu:** Customers can instantly check their point balances and view promotions directly via LINE chat.
* **LIFF Integration:** Secure, seamless member profile detection and onboarding using the LINE Frontend Framework.

## 🛠️ Technology Stack
* **Frontend:** HTML, CSS, JavaScript (Bootstrap 5)
* **Backend:** Python (FastAPI)
* **Database & Storage:** Supabase (PostgreSQL)
* **Integrations:** LINE Messaging API, LINE Login (LIFF)
* **Deployment:** Vercel (Serverless)

---

## ⚙️ Getting Started

### Prerequisites
Ensure you have the following installed on your local machine:
* Python 3.10+
* Git
* A Supabase project account
* A LINE Developer account (Messaging API & LINE Login/LIFF enabled)

### Local Development Setup

**1. Clone the repository:**
```bash
git clone https://github.com/your-username/sme-line-crm.git
cd sme-line-crm
```

**2. Create and activate a virtual environment (Recommended):**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables:**
Create a .env file in the root directory and securely add your platform credentials:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
LINE_CHANNEL_ACCESS_TOKEN=your_messaging_api_token
LINE_CHANNEL_SECRET=your_messaging_api_secret
LIFF_URL=your_liff_url
```

**5. Start the FastAPI Development Server:**
```bash
uvicorn app.main:app --reload
```
The API will be available at http://127.0.0.1:8000


**6. Start local tunneling for LINE Webhooks (Optional but required for LINE features):**
```bash
ngrok http 8000
```
Copy the generated HTTPS URL and paste it into your LINE Developer Console Webhook settings.


---

## 📂 Project Structure
```plaintext
sme-line-crm/
├── app/
│   ├── routers/          # API route handlers (product, qr_point, line_bot)
│   ├── static/           # Frontend assets (admin, liff, styles, js)
│   ├── database.py       # Supabase connection setup
│   ├── main.py           # FastAPI application instance & routing
│   └── models.py         # Data schemas and Pydantic models
├── setup_richmenu.py     # Script to initialize LINE Rich Menu
├── requirements.txt      # Python dependencies
└── vercel.json           # Serverless deployment configuration
```

## 🤝 Contributing
Contributions are welcome! If you would like to help improve OpenShop Retail, please fork the repository, create a feature branch, and submit a Pull Request.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.