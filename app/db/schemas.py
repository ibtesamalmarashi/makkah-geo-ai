from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

# ==============================
# 1. Request Models (نماذج استقبال الطلبات)
# ==============================

class QueryRequest(BaseModel):
    """النموذج المسؤول عن استقبال سؤال المستخدم من الواجهة الأمامية"""
    query: str
    session_id: Optional[str] = "session_default"

# ==============================
# 2. Spatial Models (النماذج المكانية)
# ==============================

class SpatialPoint(BaseModel):
    """نموذج لتمثيل نقطة جغرافية واحدة (مثل مدرسة أو مستشفى) ليتم رسمها كـ Marker"""
    id: Optional[int] = None
    name: str
    lat: float
    lng: float
    type: Optional[str] = None # مثلاً: 'school', 'hospital', 'center'
    details: Optional[Dict[str, Any]] = None

# ==============================
# 3. Response Models (نماذج إرسال الردود)
# ==============================

class QuickQueryResponse(BaseModel):
    """النموذج الشامل للرد على استفسارات المستخدم النصية والمكانية"""
    answer: str
    intent: str
    has_geometry: bool = False
    area_km2: Optional[float] = None
    region_id: Optional[int] = None
    layer_type: Optional[str] = None # 'governorate' or 'center'
    # قائمة النقاط التي سيتم تحويلها إلى Markers في الخريطة
    points: Optional[List[SpatialPoint]] = []
    # بيانات إضافية للواجهة الأمامية
    features: Optional[List[Dict[str, Any]]] = None
    count: Optional[int] = 0

class GeometryResponse(BaseModel):
    """النموذج الخاص بإرجاع بيانات الـ GeoJSON لحدود منطقة معينة"""
    region_id: int
    geojson: Dict[str, Any]

from typing import List, Optional, Any, Dict

class QuickQueryResponse(BaseModel):
    answer: str
    intent: str
    has_geometry: bool = False
    points: List[SpatialPoint] = []
    # الحقل الجديد الذي سيحمل المضلعات (المراكز)
    geojson: Optional[Dict[str, Any]] = None 
    count: int = 0    

# ==============================
# 4. Metadata (توثيق قاعدة البيانات للـ AI)
# ==============================

MOCK_SCHEMA = """
Table: Governorate -- بيانات المحافظات
Columns: [id, geom, NAME_AR, POPULATION, calculated_area_km2]

Table: المراكز -- المراكز الإدارية التابعة للمحافظات
Columns: [id, geom, NAME_AR, GOVERNORATE_NAME_AR, calculated_area_km2]

Table: الخدمات_التعليمية -- مواقع المدارس والمنشآت التعليمية
Columns: [id, geom, NAME_AR, GOVERNORATE_NAME]

Table: الخدمات_الصحية -- المستشفيات والمراكز الصحية
Columns: [id, geom, NAME_AR, GOVERNORATE_NAME]
"""