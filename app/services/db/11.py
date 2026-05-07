import asyncio
from app.services.ai.text_to_sql import generate_sql

async def test_key():
    try:
        print("جاري اختبار الـ API Key...")
        # نرسل سؤالاً بسيطاً جداً لنرى هل سيرد الموديل بـ SQL أم لا
        sample_sql = await generate_sql("كم عدد المناطق؟")
        print(f"✅ تم الاتصال بنجاح! الـ SQL المولد هو: {sample_sql}")
    except Exception as e:
        print(f"❌ فشل الاتصال. الخطأ: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_key())