from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from io import BytesIO
import pandas as pd
import json
from app.database import get_db
from app.models import DataRecord, ReportTemplate, User
from app.schemas import ReportTemplateResponse, ReportTemplateCreate, ReportRequest
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.get("/templates", response_model=List[ReportTemplateResponse])
async def get_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    templates = db.query(ReportTemplate).all()
    return templates

@router.get("/templates/{template_id}", response_model=ReportTemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/templates", response_model=ReportTemplateResponse)
async def create_template(
    template: ReportTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        json.loads(template.config)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON config"
        )
    
    new_template = ReportTemplate(
        name=template.name,
        config=template.config
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template

@router.put("/templates/{template_id}", response_model=ReportTemplateResponse)
async def update_template(
    template_id: int,
    template: ReportTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    try:
        json.loads(template.config)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON config"
        )
    
    db_template.name = template.name
    db_template.config = template.config
    db.commit()
    db.refresh(db_template)
    return db_template

@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"}

@router.post("/generate")
async def generate_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DataRecord)
    
    if request.category:
        query = query.filter(DataRecord.category == request.category)
    if request.start_date:
        query = query.filter(DataRecord.date >= request.start_date)
    if request.end_date:
        query = query.filter(DataRecord.date <= request.end_date)
    
    records = query.all()
    
    if request.template_id:
        template = db.query(ReportTemplate).filter(ReportTemplate.id == request.template_id).first()
        if template:
            config = json.loads(template.config)
        else:
            config = {}
    else:
        config = {}
    
    category_summary = {}
    for record in records:
        cat = record.category
        if cat not in category_summary:
            category_summary[cat] = {"count": 0, "total": 0, "items": []}
        category_summary[cat]["count"] += 1
        category_summary[cat]["total"] += float(record.value)
        category_summary[cat]["items"].append({
            "title": record.title,
            "value": float(record.value),
            "unit": record.unit,
            "date": record.date.isoformat(),
            "remark": record.remark
        })
    
    chart_data = {
        "categories": list(category_summary.keys()),
        "values": [round(s["total"], 2) for s in category_summary.values()]
    }
    
    return {
        "summary": category_summary,
        "chart_data": chart_data,
        "total_records": len(records),
        "report_config": config,
        "generated_at": pd.Timestamp.now().isoformat()
    }

@router.post("/export")
async def export_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DataRecord)
    
    if request.category:
        query = query.filter(DataRecord.category == request.category)
    if request.start_date:
        query = query.filter(DataRecord.date >= request.start_date)
    if request.end_date:
        query = query.filter(DataRecord.date <= request.end_date)
    
    records = query.all()
    
    data = [{
        '日期': r.date.strftime('%Y-%m-%d'),
        '分类': r.category,
        '标题': r.title,
        '数值': float(r.value),
        '单位': r.unit,
        '备注': r.remark
    } for r in records]
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='报表数据')
        
        summary_df = df.groupby('分类')['数值'].agg(['sum', 'count', 'mean']).reset_index()
        summary_df.columns = ['分类', '合计', '数量', '平均值']
        summary_df.to_excel(writer, index=False, sheet_name='统计汇总')
    
    output.seek(0)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=report.xlsx"}
    )
