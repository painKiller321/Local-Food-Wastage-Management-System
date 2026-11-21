# 🍽️ Local Food Wastage Management System

A community-focused platform built with **Python**, **SQL**, and **Streamlit** that connects food donors (restaurants, households, etc.) with receivers (NGOs, individuals) to reduce food waste and enhance food accessibility.

---

## 🧠 Project Overview

This system allows users to:
- List surplus food for donation.
- Claim available food by NGOs or individuals.
- View and analyze food donations, claims, and trends.
- Filter food listings by provider, location, type, and meal.
- Manage and track food listings using a user-friendly interface.

---

## 📊 Key Features

- 🔍 **Food Listings Dashboard**: View all available food items, filter by city, type, or meal.
- 🧾 **Claims Analysis**: See who’s claiming food, most donated items, and top meal types.
- 📇 **Contacts View**: Get contact details of food providers and receivers.
- ⚙️ **Manage Listings**: Perform CRUD operations (Add, Update, Delete food records).
- 📈 **SQL-Driven Insights**: Data retrieved and analyzed using powerful SQL queries.

---

## 🛠️ Tech Stack

| Tool | Description |
|------|-------------|
| 🐍 Python | Main programming language |
| 🐘 Cloud PostgreSQL (Neon) | Production cloud database with auto-fallback to SQLite |
| 🧮 SQL (SQLite) | Offline / local fallback database |
| 📊 Streamlit | Web interface for visualizing and interacting |
| 🧠 Pandas | Data handling and transformation |
| 🧵 SQLAlchemy | SQL engine for cross-database compatibility |
| 📈 Plotly | Interactive visual charts and analytics |

---

## 📁 Project Structure

📦 project-root/
├── app.py                             # Main Streamlit app interface & sidebar navigation
├── queries.py                         # Unified SQL engine (PostgreSQL + SQLite fallback)
├── check.py                           # Diagnostic health check & database validator
├── migrate_to_cloud.py                # Database migration utility (SQLite -> Cloud PostgreSQL)
├── food_waste.db                      # Local SQLite database (offline fallback)
├── requirements.txt                   # Production dependencies
├── Dockerfile                         # Production Docker container configuration
├── .dockerignore                      # Docker ignore rules
├── .streamlit/
│   ├── config.toml                    # Streamlit server & theme configuration
│   ├── secrets.toml.example           # Example secrets configuration template
│   └── secrets.toml                   # Local secrets (git-ignored for security)
├── views/                             # UI Pages (Dashboard, Listings, Analytics, etc.)
└── README.md                          # Project documentation

---

## 🚀 How to Run Locally

1. **Clone the repo:**
   ```bash
   git clone https://github.com/chobheshubham/Local-Food-Wastage-Management-System.git
   cd Local-Food-Wastage-Management-System
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Database (Optional for Cloud):**
   - Create `.streamlit/secrets.toml` (or use local SQLite by default):
     ```toml
     DATABASE_URL = "postgresql://user:password@neon-host/neondb?sslmode=require"
     ```

4. **Verify Database & System Health:**
   ```bash
   python check.py
   ```

5. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

---

## ☁️ How to Deploy

### Option 1: Streamlit Community Cloud (Recommended - Free)
1. Push your repository to GitHub (ensure `.streamlit/secrets.toml` is kept in `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **New app**, select your repository, branch (`main`), and set **Main file path** to `app.py`.
4. Click **Advanced settings...** -> **Secrets** and paste:
   ```toml
   DATABASE_URL = "postgresql://neondb_owner:npg_wvF5pq1gZfnO@ep-proud-river-bdk9ig70-pooler.c-8.us-east-2.aws.neon.tech/neondb?sslmode=require"
   ```
5. Click **Deploy!** Your app is live with real-time cloud data.

### Option 2: Docker / Container (Render, Railway, Hugging Face, GCP)
Build and run the container:
```bash
docker build -t foodbridge .
docker run -p 8501:8501 -e DATABASE_URL="your-database-url" foodbridge
```

## ✅ Outcomes
- A live dashboard showcasing food donation and claim activity.
- SQL insights on food distribution, demand trends, and wastage reduction.
- Scalable architecture ready for cloud deployment or NGO partnerships.

## 🙌 Contributions & Feedback
Have suggestions or want to contribute? Feel free to open issues or pull requests!

## 👨‍💻 Developed By
Shubham Chobhe\
🌐 [GitHub Profile](https://github.com/chobheshubham)
