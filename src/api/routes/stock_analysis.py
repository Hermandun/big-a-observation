from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.schemas import StockAnalysis
from services.news_monitor import NewsMonitor

router = APIRouter()
news_monitor = NewsMonitor()

@router.get("/latest")
async def get_latest_analysis():
    """获取最新的分析结果"""
    # TODO: 实现从数据库获取最新分析结果
    return {"message": "Coming soon"}

@router.get("/stock/{stock_code}")
async def get_stock_data(stock_code: str):
    """获取单个股票的实时数据"""
    data = await news_monitor.get_stock_data(stock_code)
    if not data:
        raise HTTPException(status_code=404, detail="Stock not found")
    return data