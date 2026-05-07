import re
import asyncio
import json
from sqlalchemy import text
from decimal import Decimal
from typing import Dict, Any, List
from app.db.session import SessionLocal
from app.services.ai.text_to_sql import generate_valid_sql

# ==========================
# 1. JSON Safe Converter
# ==========================
def professional_serializer(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (bytes, bytearray)):
        return str(obj)
    return str(obj)

# ==========================
# 2. Protected Names Fix
# ==========================
def protect_sql_names(sql: str) -> str:
    protected_names = [
        "MakkahRegion", "Governorate", "المراكز", "الخدمات_التعليمية", "الخدمات_الصحية",
        "NAME_AR", "NAME_EN", "POPULATION", "calculated_area_km2", "area_km2",
        "REGION_ID", "OBJECTID", "geom", "id", "GOVERNORATE_NAME_AR"
    ]

    for name in protected_names:
        sql = re.sub(rf'(?<!")\b{name}\b(?!")', f'"{name}"', sql)
    
    sql = sql.replace('الخدمات التعليمية', '"الخدمات_التعليمية"')
    sql = sql.replace('الخدمات الصحية', '"الخدمات_الصحية"')
    
    return sql

# ==========================
# 3. SQL Executor with Healing
# ==========================
async def execute_query_with_healing(user_query: str, db_session=None, max_retries: int = 3) -> Dict[str, Any]:
    error = None
    sql_query = ""
    
    session_factory = db_session if db_session else SessionLocal()

    for attempt in range(max_retries):
        try:
            # 1. توليد الـ SQL
            sql_query = await generate_valid_sql(user_query)
            if not sql_query:
                continue

            # 🚀 إضافة: فحص النطاق (Out of Scope)
            if "out_of_scope" in sql_query.lower():
                return {
                    "success": False,
                    "error": "خارج النطاق",
                    "sql": sql_query,
                    "data": []
                }

            # 2. تحسين الـ SQL ليدعم الخريطة مع التبسيط الجديد 0.0005
            if "geom" in sql_query and "ST_AsGeoJSON" not in sql_query:
                sql_query = re.sub(
                     r'\bgeom\b', 
                     'ST_AsGeoJSON(ST_Simplify(ST_Transform(geom, 4326), 0.0005)) as geometry', 
                     sql_query, 
                     flags=re.IGNORECASE
                )

            # 3. حماية الأسماء
            sql_query = protect_sql_names(sql_query)

            # 4. التنفيذ
            async with session_factory as session:
                await session.execute(text("SET TRANSACTION READ ONLY;"))
                
                result = await session.execute(text(sql_query))
                rows = result.fetchall()
                data = [dict(row._mapping) for row in rows]

                return {
                    "success": True,
                    "sql": sql_query,
                    "data": data,
                    "count": len(data),
                    "attempts": attempt + 1
                }

        except Exception as e:
            error = str(e)
            print(f"⚠️ محاولة {attempt + 1} فشلت بسبب: {error}")
            
            # منع التكرار اللانهائي إذا كان الخطأ خارج النطاق أساساً
            if "out_of_scope" in str(error): break
            
            user_query = f"{user_query} (خطأ SQL: {error} - يرجى تصحيح الاستعلام)"
            await asyncio.sleep(0.5) # تقليل التأخير لزيادة السرعة

    return {
        "success": False,
        "error": f"تعذر التنفيذ. الخطأ الأخير: {error}",
        "sql": sql_query,
        "data": []
    }