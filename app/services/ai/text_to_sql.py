import asyncio
import re
from openai import AsyncOpenAI
from typing import Tuple

# ==============================
# Client Setup
# ==============================
# ملاحظة: تأكد من أن Ollama يعمل محلياً على هذا المنفذ
client = AsyncOpenAI(
    api_key="ollama",
    base_url="http://127.0.0.1:11434/v1"
)

# ============================================================
# 🚀 Makkah Geo-AI: Optimized SQL Prompt Template (V4.1)
# ============================================================
# تم تحديث الـ Prompt لضمان استرجاع البيانات الإدارية (المحافظة) في كافة الاستعلامات
SQL_PROMPT_TEMPLATE = """
Target: PostGIS Expert. Output: ONLY SYNTAX-PERFECT SQL for Makkah GIS.

RULES:
1. Format: SELECT only. No backticks, no explanations. 
2. Naming: Double quote ALL tables/columns ("table"."column").
3. Geospatial: Use (ST_AsGeoJSON(ST_Simplify(ST_Transform("geom", 4326), 0.0005)) as geometry).
4. Logic: 
   - ALWAYS include "GOVERNORATE_NAME_AR" in SELECT for "المراكز", "الخدمات_التعليمية", and "الخدمات_الصحية" to ensure it appears on map popups.
   - 'How Many' (كم عدد): SELECT "NAME_AR", "GOVERNORATE_NAME_AR", and geometry. NEVER use COUNT/GROUP BY.
   - 'Area' (مساحة): SELECT "NAME_AR", "calculated_area_km2", and geometry.
5. Filtering: Use LIKE '%value%' for Arabic names. Use "GOVERNORATE_NAME_AR" when filtering by governorate.

SCHEMA:
- "Governorate": [id, geom, NAME_AR, calculated_area_km2]
- "المراكز", "الخدمات_التعليمية", "الخدمات_الصحية": [id, geom, NAME_AR, GOVERNORATE_NAME_AR]

EXAMPLES:
- User: كم مدارس بحرة؟
  SQL: SELECT "NAME_AR", "GOVERNORATE_NAME_AR", ST_AsGeoJSON(ST_Simplify(ST_Transform("geom", 4326), 0.0005)) as geometry FROM "الخدمات_التعليمية" WHERE "GOVERNORATE_NAME_AR" LIKE '%بحرة%' ;

- User: مراكز الكامل؟
  SQL: SELECT "NAME_AR", "GOVERNORATE_NAME_AR", ST_AsGeoJSON(ST_Simplify(ST_Transform("geom", 4326), 0.0005)) as geometry FROM "المراكز" WHERE "GOVERNORATE_NAME_AR" LIKE '%الكامل%' ;

- User: مساحة جدة؟
  SQL: SELECT "NAME_AR", "calculated_area_km2", ST_AsGeoJSON(ST_Simplify(ST_Transform("geom", 4326), 0.0005)) as geometry FROM "Governorate" WHERE "NAME_AR" LIKE '%جدة%' LIMIT 1;
"""
async def generate_sql_raw(user_query: str) -> str:
    """توليد وتنظيف استعلام SQL من الموديل"""
    try:
        response = await client.chat.completions.create(
            model="qwen2.5:7b",
            messages=[
                {"role": "system", "content": SQL_PROMPT_TEMPLATE},
                {"role": "user", "content": user_query}
            ],
            temperature=0,
            max_tokens=100
        )

        content = response.choices[0].message.content.strip()

        # 1. إزالة أي علامات Markdown قد يضيفها الموديل رغم المنع
        content = re.sub(r'```sql|```', '', content).strip()

        # 2. استخراج جزء الـ SELECT فقط (تجاهل أي كلام شرح قبله)
        match = re.search(r"(SELECT[\s\S]+)", content, re.IGNORECASE)
        if match:
            content = match.group(1)

        # 3. تنظيف الفواصل المنقوطة الزائدة
        return content.split(";")[0].strip()
    
    except Exception as e:
        print(f"❌ Error in generate_sql_raw: {e}")
        return ""

def validate_sql(sql: str) -> Tuple[bool, str]:
    """التأكد من أمان الاستعلام وصحته الأساسية"""
    if not sql or not sql.upper().startswith("SELECT"):
        return False, "Invalid SQL Start"
    
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER"]
    for word in forbidden:
        if word in sql.upper():
            return False, f"Forbidden keyword detected: {word}"
            
    return True, ""

async def generate_valid_sql(user_query: str) -> str:
    """الأنبوب النهائي (Pipeline) لاستخراج SQL جاهز للتنفيذ"""
    try:
        sql = await generate_sql_raw(user_query)
        
        # تصحيح يدوي سريع لأخطاء شائعة (Safety Net)
        if "GOVERNORATE_NAME" in sql and "GOVERNORATE_NAME_AR" not in sql:
            sql = sql.replace('"GOVERNORATE_NAME"', '"GOVERNORATE_NAME_AR"')

        valid, error = validate_sql(sql)
        if not valid:
            print(f"⚠️ SQL Validation Failed: {error}")
            # استعلام افتراضي آمن لتجنب تعليق الـ Backend مع التبسيط الجديد
            return 'SELECT "NAME_AR", ST_AsGeoJSON(ST_Simplify(ST_Transform("geom", 4326), 0.0005)) as geometry FROM "Governorate" LIMIT 1'
            
        return sql

    except Exception as e:
        print(f"🔥 SQL Pipeline Error: {e}")
        return 'SELECT "id" FROM "Governorate" LIMIT 1'