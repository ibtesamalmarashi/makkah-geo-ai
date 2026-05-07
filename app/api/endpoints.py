from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional, Any
import json
import time

# =========================
# 1. الاستيرادات المحدثة والمنقحة
# =========================
from app.db.session import get_db
from app.db.schemas import QuickQueryResponse, SpatialPoint, QueryRequest
from app.services.ai.synthesizer import synthesize_spatial_response
# تم الاعتماد على execute_query_with_healing الذي يستدعي generate_valid_sql داخلياً
from app.services.db.executor import execute_query_with_healing

router = APIRouter(tags=["Spatial Data"])

# =========================
# 2. الدوال المساعدة (محسنة للأداء ودعم البيانات الإدارية)
# =========================
def parse_geometry_to_features(rows) -> List[Any]:
    """
    تحويل نتائج قاعدة البيانات إلى GeoJSON Features مباشرة.
    تدعم النقاط (Points) والمضلعات (Polygons/MultiPolygons) مع دعم المحافظة والمركز.
    """
    processed_features = []
    for row in rows:
        row_dict = dict(row) if hasattr(row, '_mapping') else row
        
        # البحث عن البيانات الجغرافية في الحقول المحتملة
        geom_raw = row_dict.get("geometry") or row_dict.get("geojson_simple") or row_dict.get("geom")
        
        if geom_raw:
            try:
                geom = json.loads(geom_raw) if isinstance(geom_raw, str) else geom_raw
                # منطق تحديد الاسم (الأولوية لـ NAME_AR)
                name = row_dict.get("NAME_AR") or row_dict.get("name_ar") or row_dict.get("SCHOOL_NAME") or "معلم مكاني"
                
                # تمييز النوع للتنسيق البصري على الخريطة
                is_polygon = geom.get("type") in ["Polygon", "MultiPolygon"]
                
                processed_features.append({
                    "type": "Feature",
                    "geometry": geom,
                    "properties": {
                        "name": name,
                        "label": name,
                        "color": "#E67E51" if is_polygon else "#003B38",
                        "fillOpacity": 0.25 if is_polygon else 0.8,
                        "layer_type": "center" if is_polygon else "point",
                        "category": row_dict.get("category") or "General",
                        "calculated_area_km2": row_dict.get("calculated_area_km2"),
                        # التعديل: تمرير المحافظة والمركز ليتم عرضها في Popups الخريطة
                        "GOVERNORATE_NAME_AR": row_dict.get("GOVERNORATE_NAME_AR") or row_dict.get("governorate"),
                        "CENTER_NAME": row_dict.get("CENTER_NAME") or row_dict.get("center")
                    }
                })
            except Exception:
                continue
    return processed_features

# =========================
# 3. المسارات الرئيسية (Endpoints)
# =========================

@router.post("/query", response_model=QuickQueryResponse)
async def handle_natural_language_query(req: QueryRequest, db: AsyncSession = Depends(get_db)):
    start_all = time.time()
    
    try:
        # الخطوة 1: التنفيذ المباشر (تم إلغاء تصنيف النية Router لزيادة السرعة)
        execution_result = await execute_query_with_healing(req.query, db_session=db)
        
        # فحص ما إذا كان السؤال خارج النطاق (اعتذار المودل)
        if execution_result.get("error") == "خارج النطاق" or "out_of_scope" in str(execution_result.get("sql", "")):
            return QuickQueryResponse(
                answer="أعتذر، أنا متخصص في بيانات منطقة مكة المكرمة فقط (المحافظات، المراكز، الخدمات الصحية والتعليمية). لا يمكنني الإجابة على استفسارات خارج هذا النطاق.",
                intent="out_of_scope"
            )
        
        if not execution_result.get("success"):
            return QuickQueryResponse(
                answer="عذراً، لم أتمكن من العثور على البيانات المطلوبة حالياً في جداول منطقة مكة.", 
                intent="error"
            )

        results = execution_result.get("data", [])
        count = execution_result.get("count", 0)

        # الخطوة 2: معالجة البيانات الجغرافية
        geo_features = parse_geometry_to_features(results)

        # الخطوة 3: صياغة الرد النصي
        if count == 0:
            answer_text = "لم يتم العثور على نتائج تطابق بحثك في قاعدة بيانات مكة المكرمة."
        
        elif count > 15:
            answer_text = f"تم العثور على {count} نتيجة في منطقة مكة. قمت بعرض كافة المواقع على الخريطة لتسهيل تصفحها."
        
        else:
            ai_data_slim = []
            for row in results:
                row_dict = dict(row) if hasattr(row, '_mapping') else row
                clean_row = {k: v for k, v in row_dict.items() if k not in ['geometry', 'geom', 'geojson_simple', 'ST_AsGeoJSON']}
                ai_data_slim.append(clean_row)
            
            final_answer_obj = await synthesize_spatial_response(req.query, ai_data_slim)
            answer_text = final_answer_obj.get("answer") if isinstance(final_answer_obj, dict) else final_answer_obj

        # التعديل: استخراج النقاط مع دعم بيانات المحافظة والمركز لـ React
        extracted_points = []
        for f in geo_features:
            if f["geometry"]["type"] == "Point":
                coords = f["geometry"]["coordinates"]
                extracted_points.append(SpatialPoint(
                    name=f["properties"]["name"],
                    lat=coords[1],
                    lng=coords[0],
                    # تمرير البيانات الإدارية
                    governorate=f["properties"].get("GOVERNORATE_NAME_AR"),
                    center=f["properties"].get("CENTER_NAME")
                ))

        print(f"✅ Total Response Time: {time.time() - start_all:.2f}s | Count: {count}")

        return QuickQueryResponse(
            answer=answer_text,
            intent="spatial",
            has_geometry=len(geo_features) > 0,
            points=extracted_points,
            geojson={"type": "FeatureCollection", "features": geo_features}, 
            count=count
        )

    except Exception as e:
        print(f"❌ Error in Endpoint: {str(e)}")
        return QuickQueryResponse(answer="حدث خطأ غير متوقع أثناء معالجة الطلب.", intent="error")

@router.get("/governorates/all-stats")
async def get_all_governorates_stats(db: AsyncSession = Depends(get_db)):
    """جلب كافة حدود المحافظات (للعرض الأولي للخريطة)"""
    try:
        query = text('SELECT id, "NAME_AR", ST_AsGeoJSON(ST_Simplify(ST_Transform(geom, 4326), 0.0005)) as geometry FROM "Governorate"')
        result = await db.execute(query)
        features = [{
            "type": "Feature",
            "properties": {"id": r.id, "name": r.NAME_AR},
            "geometry": json.loads(r.geometry)
        } for r in result.fetchall()]
        return {"type": "FeatureCollection", "features": features}
    except Exception as e:
        print(f"Error fetching all stats: {e}")
        return {"type": "FeatureCollection", "features": []}

@router.get("/geometry/governorate/{gov_id}")
async def get_governorate_geometry(gov_id: int, db: AsyncSession = Depends(get_db)):
    """جلب حدود محافظة معينة بالـ ID مع تبسيط الجيومتري لتحسين الأداء"""
    try:
        query = text('''
            SELECT ST_AsGeoJSON(ST_Simplify(ST_Transform(geom, 4326), 0.0005)) 
            FROM "Governorate" 
            WHERE id = :id
        ''')
        result = await db.execute(query, {"id": gov_id})
        row = result.fetchone()
        
        if row and row[0]: 
            return json.loads(row[0])
            
        raise HTTPException(status_code=404, detail="المحافظة غير موجودة")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))