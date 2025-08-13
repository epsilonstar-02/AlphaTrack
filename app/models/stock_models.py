from pydantic import BaseModel

class Stock(BaseModel):
    symbol: str
    name: str
    price: float
