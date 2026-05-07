# Makkah Geo-AI 🕋📍

Makkah Geo-AI is an advanced AI-powered spatial middleware platform designed to bridge the gap between natural language and complex geospatial analysis. Developed during my Co-op Internship at the Makkah Region Development Authority, the platform enables intuitive interaction with spatial datasets through Arabic natural language queries and real-time GIS visualization.

---

# 🚀 Key Features

- **Arabic Natural Language to SQL (NL2SQL)**: Converts Arabic user queries into syntax-perfect PostGIS SQL queries using **Qwen2.5:7B** via **Ollama**.
- **Dynamic Spatial Visualization**: Real-time rendering of GeoJSON layers including Points, Polygons, and MultiPolygons on an interactive map.
- **Administrative Hierarchy Support**: Automatic identification of Governorates and Centers with detailed metadata displayed in map popups.
- **Spatial Performance Optimization**: Uses `ST_Simplify` and `ST_Transform` to optimize geometry transmission and rendering performance.
- **Interactive GIS Interface**: Responsive frontend with smooth spatial interaction and layer visualization.
- **Asynchronous High-Performance Backend**: Built using **FastAPI** and **Async SQLAlchemy** for scalable performance.

---

# 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **ORM:** SQLAlchemy (Async) & GeoAlchemy2
- **AI Orchestration:** LangChain

### Frontend
- **Library:** React
- **Mapping:** Leaflet
- **Styling:** Tailwind CSS

### Database & AI
- **Database:** PostgreSQL + PostGIS
- **LLM Engine:** Ollama (Model: Qwen2.5:7B)

---

# 📋 Database Schema

The system supports key spatial layers in the Makkah Region:

| Layer | Description |
| :--- | :--- |
| **Governorate** | Administrative boundaries and area statistics |
| **المراكز** | Administrative centers linked to governorates |
| **الخدمات_التعليمية** | Educational facilities and schools |
| **الخدمات_الصحية** | Hospitals and healthcare centers |

---
# ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/ibtesamalmarashi/makkah-geo-ai.git](https://github.com/ibtesamalmarashi/makkah-geo-ai.git)
cd makkah-geo-ai

  2. Backend Setup
Create Virtual Environment:
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate

Install Dependencies:
cd backend
pip install -r requirements.txt

  3. AI / Ollama Setup 
  
Download and install Ollama.

Pull the required model:
ollama pull qwen2.5:7b
ollama serve

 4. Database Setup
Ensure PostgreSQL and PostGIS are installed.

Create the database:
CREATE DATABASE makkah_gis;
\c makkah_gis;
CREATE EXTENSION postgis;

📡 API Endpoints

Endpoint,Method,Description
/query,POST,Process Arabic NL query
/health,GET,Health check endpoint
/layers,GET,Retrieve available GIS layers

🤝 Acknowledgments
I would like to express my sincere gratitude to the Makkah Region Development Authority for providing a professional environment during my Co-op training.

Special thanks to my supervisor, Ali Alamri, for his invaluable mentorship, technical guidance, and continuous support throughout the development of this project.

👩‍💻 Author
Ibtesam Almarashi

Geospatial Data Scientist & Software Developer
