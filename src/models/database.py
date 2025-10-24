from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class StockAnalysis(Base):
    __tablename__ = "stock_analysis"

    id = Column(Integer, primary_key=True, index=True)
    news_title = Column(String)
    news_content = Column(Text)
    affected_sectors = Column(JSON)
    recommended_stocks = Column(JSON)
    analysis_time = Column(DateTime, default=datetime.utcnow)
    impact_level = Column(String)