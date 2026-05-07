from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# التحسين: إضافة إعدادات الـ Pooling لرفع الكفاءة ومنع التهنيج
engine = create_async_engine(
    settings.database_url,
    echo=True,           # مفيد جداً لمراقبة الـ SQL الناتج من الـ AI في الـ Terminal
    future=True,
    pool_size=10,         # عدد الاتصالات التي تبقى مفتوحة وجاهزة للاستخدام
    max_overflow=20,      # عدد الاتصالات الإضافية المسموح بها عند ضغط الأسئلة
    pool_recycle=3600,    # إعادة تدوير الاتصال كل ساعة لتجنب انقطاعه من جهة Postgres
    pool_pre_ping=True    # التحقق من سلامة الاتصال قبل إرسال استعلام الـ SQL إليه
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            # التأكد من إغلاق الجلسة وتحرير الاتصال للـ Pool مرة أخرى
            await session.close()