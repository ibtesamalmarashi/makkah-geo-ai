import asyncio
import json
import re
from openai import AsyncOpenAI

# ==========================
# Ollama Client
# ==========================
client = AsyncOpenAI(
    api_key="ollama",
    base_url="http://127.0.0.1:11434/v1"
)

# ==========================
# Prompt (محسن لدعم استخلاص البيانات)
# ==========================
SYNTHESIZER_PROMPT = """
Role: Makkah Geo-AI Assistant. Task: Summarize GIS data in Arabic.

RULES:
1. Data Integrity: Use 'area_km2' and 'total_count' exactly as provided. NO jargon.
2. Naming: 
   - Centers (count <= 10): List ALL names.
   - Others/Large count: List first 3 names only.
3. Format: Max 3 lines. Professional tone.
4. Call to Action: Always end by referencing the Map.

EXAMPLES:
- "تم العثور على 5 مراكز منها: الشميسي، عسفان... موضحّة الآن على الخريطة."
- "مساحة المنطقة 4682.46 كم²، وتم تحديد حدودها على الخريطة."
- "يوجد 50 مدرسة، منها: الفتح والنور. تفضل بمشاهدة التوزيع على الخريطة."
"""
# ==========================
# دالة استخراج النقاط (Smart Extraction)
# ==========================
def extract_spatial_points(raw_data_str: str):
    """
    تحويل البيانات الخام القادمة من SQL إلى مصفوفة نقاط يفهمها الماركر في الخريطة
    """
    points = []
    try:
        # محاولة تحويل النص إلى JSON إذا كان مصفوفة صفوف
        data = json.loads(raw_data_str)
        if isinstance(data, list):
            for row in data:
                # البحث عن حقل الجيومتري (الذي طلبه AI في الخطوة السابقة)
                if "geometry" in row and row["geometry"]:
                    geo = json.loads(row["geometry"])
                    if geo["type"] == "Point":
                        points.append({
                            "name": row.get("NAME_AR") or row.get("SCHOOL_NAME") or "منشأة",
                            "lat": geo["coordinates"][1],
                            "lng": geo["coordinates"][0],
                            "type": row.get("category") or "General"
                        })
    except Exception as e:
        print(f"⚠️ Point Extraction Error: {e}")
    
    return points

# ==========================
# Main Synthesizer Function
# ==========================
import json

async def synthesize_spatial_response(user_query: str, raw_data: any):
    """
    تحويل نتائج قاعدة البيانات إلى رد نصي دقيق واحترافي.
    """
    try:
        # 1. تطهير البيانات الواردة
        if isinstance(raw_data, str):
            try:
                processed_data = json.loads(raw_data)
            except json.JSONDecodeError:
                processed_data = []
        else:
            processed_data = raw_data if isinstance(raw_data, list) else []

        # 2. استخراج المؤشرات الجغرافية والرقمية بدقة
        count = len(processed_data)
        exact_area = None
        sample_names = []

        if count > 0:
            first_row = processed_data[0]
            if isinstance(first_row, dict):
                # جلب المساحة الدقيقة من العمود المخصص الذي أضفناه في الـ SQL
                exact_area = first_row.get("calculated_area_km2")
                # تجميع عينة من الأسماء للرد النصي
                sample_names = [
                    item.get("NAME_AR") for item in processed_data[:3] 
                    if isinstance(item, dict) and item.get("NAME_AR")
                ]

        # 3. بناء ملخص البيانات الموجه للموديل
        data_summary = {
            "total_count": count,
            "samples": sample_names,
            "area_km2": exact_area,  # القيمة الحقيقية من قاعدة البيانات
            "status": "success" if count > 0 else "no_results"
        }

        # 4. توليد الرد باستخدام معايير دقة عالية (Temperature = 0)
        response = await client.chat.completions.create(
            model="qwen2.5:7b",
            messages=[
                {"role": "system", "content": SYNTHESIZER_PROMPT},
                {"role": "user", "content": f"Query: {user_query}\nData: {json.dumps(data_summary, ensure_ascii=False)}"}
            ],
            temperature=0.0,  # لضمان الالتزام بالأرقام الممرة وعدم الهلوسة
            max_tokens=100
        )
        
        return {
            "answer": response.choices[0].message.content.strip(),
            "count": count,
            "has_geometry": count > 0
        }

    except Exception as e:
        print(f"❌ Professional Synth Error: {str(e)}")
        return {
            "answer": "تم استخراج البيانات المطلوبة وتحديث الخريطة بنجاح.",
            "count": 0,
            "has_geometry": True
        }
# دالة الـ Fallback للحالات الطارئة
def fallback_response(data: str) -> str:
    return "تم جلب البيانات المطلوبة وتحديث الخريطة."