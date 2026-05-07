from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# تأكد من أن هذا الاستيراد يطابق هيكل مجلداتك الجديد
from app.api.endpoints import router as api_router

app = FastAPI(
    title="Intelligent Spatial Middleware",
    description="Arabic Natural Language to Spatial SQL API",
    version="1.0.0"
)

# إعدادات CORS مهمة جداً لربط React مع FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في الإنتاج استبدلها برابط الـ Frontend الخاص بك
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ربط الـ Router مع البادئة الموحدة
# لاحظ: أي مسار داخل api_router سيبدأ بـ /api/v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Welcome to Intelligent Spatial Middleware API",
        "documentation": "/docs",
        "endpoints": {
            "all_stats": "/api/v1/governorates/all-stats",
            "query": "/api/v1/query"
        }
    }

# تشغيل التطبيق (في حال رغبت بتشغيله من داخل الملف مباشرة)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)