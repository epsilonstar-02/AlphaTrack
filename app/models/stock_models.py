from pydantic import BaseModel, Field, validator
from typing import List

class StockDataPoint(BaseModel):
    date: str
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: int = Field(ge=0)

    @validator('high')
    def high_must_be_highest(cls, v, values):
        if 'low' in values and v < values['low']:
            raise ValueError('High price must be greater than or equal to low price')
        return v

    @validator('low')
    def low_must_be_lowest(cls, v, values):
        if 'high' in values and v > values['high']:
            raise ValueError('Low price must be less than or equal to high price')
        return v

class Stock(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    name: str = Field(min_length=1)
    price: float = Field(gt=0)

    @validator('symbol')
    def symbol_must_be_uppercase(cls, v):
        return v.upper().strip()

class StockData(BaseModel):
    symbol: str
    data: List[StockDataPoint]
    latestClose: float
    fiftyTwoWeekHigh: float
    fiftyTwoWeekLow: float
    averageVolume: float

class Company(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    name: str = Field(min_length=1)

    @validator('symbol')
    def symbol_must_be_uppercase(cls, v):
        return v.upper().strip()
