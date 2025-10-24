from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    username: str
    email: Optional[str] = None
    hashed_password: str

class StockAnalysis(BaseModel):
    news_title: str
    news_content: str
    affected_sectors: List[str]
    recommended_stocks: List[dict]
    analysis_time: str
    impact_level: str