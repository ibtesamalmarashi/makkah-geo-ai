Makkah Geo-AI 🕋📍

Makkah Geo-AI is an advanced intelligent spatial middleware platform designed to bridge the gap between natural language and complex geospatial data analysis. Developed during my Co-op Internship at the Makkah Region Development Authority, this project focuses on providing intuitive, AI-driven access to the spatial datasets of the Makkah region.

🚀 Key Features

Natural Language to SQL (NL2SQL): Seamlessly converts Arabic natural language queries into syntax-perfect PostGIS SQL queries using the Qwen2.5:7B model.

Dynamic Spatial Visualization: Real-time rendering of GeoJSON features (Points, Polygons, and MultiPolygons) on an interactive map.

Administrative Hierarchy Support: Automatic identification and display of Governorates and Centers with detailed metadata in map popups.

Performance Optimized: Implements ST_Simplify and ST_Transform for fast spatial data transmission and fluid map rendering.

Modern Tech Stack: Features a high-performance asynchronous backend and a responsive, interactive frontend.

🛠️ Tech Stack

Backend: FastAPI (Python), SQLAlchemy (Async), GeoAlchemy2.

Frontend: React, Leaflet, Tailwind CSS.

Database: PostgreSQL with PostGIS extension.

AI/LLM: Qwen2.5:7B via Ollama / LangChain.

📋 Database Schema

The system is optimized for the following spatial layers in the Makkah Region:

Governorates (Governorate): Administrative boundaries and statistical area data.

Centers (المراكز): Detailed administrative centers linked to their parent governorates.

Educational Services (الخدمات_التعليمية): Comprehensive mapping of schools and facilities.

Health Services (الخدمات_الصحية): Hospitals and primary health centers.

⚙️ Installation & Setup

1. Clone the repository

git clone [https://github.com/ibtesamalmarashi/makkah-geo-ai.git](https://github.com/ibtesamalmarashi/makkah-geo-ai.git)
cd makkah-geo-ai


2. Set up the Backend

cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt


3. Environment Variables

Create a .env file in the backend directory:

DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/makkah_gis
OLLAMA_BASE_URL=http://localhost:11434


4. Run the Application

Backend:

uvicorn app.main:app --reload


Frontend:

cd frontend
npm install
npm start


🤝 Acknowledgments

I would like to express my sincere gratitude to the Makkah Region Development Authority for providing a professional and inspiring environment for my Co-op training.
Special thanks to my supervisor, Ali Alamri , for his invaluable mentorship, technical guidance, and support throughout the development of this project.

👩‍💻 Author

Ibtesam almarashi
Geospatial Data Scientist & Software Developer

Note: This project was developed as part of a Co-op training program and is intended for demonstration purposes.