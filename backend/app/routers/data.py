from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date
from io import BytesIO
import pandas as pd
from app.database import get_db
from app.models import DataRecord, User
from app.schemas import DataRecordResponse, DataRecordCreate, DataRecordUpdate
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[DataRecordResponse])
async def get_data(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DataRecord)
    if category:
        query = query.filter(DataRecord.category == category)
    if start_date:
        query = query.filter(DataRecord.date >= start_date)
    if end_date:
        query = query.filter(DataRecord.date <= end_date)
    records = query.offset(skip).limit(limit).all()
    return records

@router.get("/{record_id}", response_model=DataRecordResponse)
async def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(DataRecord).filter(DataRecord.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.post("/", response_model=DataRecordResponse)
async def create_record(
    record: DataRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_record = DataRecord(
        category=record.category,
        title=record.title,
        value=record.value,
        unit=record.unit,
        date=record.date,
        remark=record.remark,
        created_by=current_user.id
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@router.put("/{record_id}", response_model=DataRecordResponse)
async def update_record(
    record_id: int,
    record: DataRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_record = db.query(DataRecord).filter(DataRecord.id == record_id).first()
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    db_record.category = record.category
    db_record.title = record.title
    db_record.value = record.value
    db_record.unit = record.unit
    db_record.date = record.date
    db_record.remark = record.remark
    db.commit()
    db.refresh(db_record)
    return db_record

@router.delete("/{record_id}")
async def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(DataRecord).filter(DataRecord.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"message": "Record deleted successfully"}

@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Only CSV and Excel files are allowed."
        )
    
    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(contents))
        else:
            df = pd.read_excel(BytesIO(contents))
        
        required_columns = ['category', 'title', 'value', 'date']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns. Required: {required_columns}"
            )
        
        records_created = 0
        for _, row in df.iterrows():
            new_record = DataRecord(
                category=str(row['category']),
                title=str(row['title']),
                value=float(row['value']),
                unit=str(row.get('unit', '')),
                date=pd.to_datetime(row['date']).date(),
                remark=str(row.get('remark', '')),
                created_by=current_user.id
            )
            db.add(new_record)
            records_created += 1
        
        db.commit()
        return {"message": f"Successfully imported {records_created} records"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing data: {str(e)}"
        )

@router.get("/export")
async def export_data(
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DataRecord)
    if category:
        query = query.filter(DataRecord.category == category)
    if start_date:
        query = query.filter(DataRecord.date >= start_date)
    if end_date:
        query = query.filter(DataRecord.date <= end_date)
    
    records = query.all()
    data = [{
        'id': r.id,
        'category': r.category,
        'title': r.title,
        'value': float(r.value),
        'unit': r.unit,
        'date': r.date.isoformat(),
        'remark': r.remark,
        'created_at': r.created_at.isoformat() if r.created_at else None
    } for r in records]
    
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    output.seek(0)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=data_export.xlsx"}
    )

@router.get("/categories")
async def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    categories = db.query(DataRecord.category).distinct().all()
    return [cat[0] for cat in categories]

@router.get("/summary")
async def get_summary(
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DataRecord)
    if category:
        query = query.filter(DataRecord.category == category)
    if start_date:
        query = query.filter(DataRecord.date >= start_date)
    if end_date:
        query = query.filter(DataRecord.date <= end_date)
    
    records = query.all()
    total_count = len(records)
    total_value = sum(float(r.value) for r in records)
    avg_value = total_value / total_count if total_count > 0 else 0
    
    return {
        "total_count": total_count,
        "total_value": round(total_value, 2),
        "avg_value": round(avg_value, 2),
        "category": category
    }
