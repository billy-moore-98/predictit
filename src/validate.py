from pydantic import BaseModel
from typing import List, Optional


class Contract(BaseModel):
    id: int
    dateEnd: str
    image: str
    name: str
    shortName: str
    status: str
    lastTradePrice: Optional[float]
    bestBuyYesCost: Optional[float]
    bestBuyNoCost: Optional[float]
    bestSellYesCost: Optional[float]
    bestSellNoCost: Optional[float]
    lastClosePrice: Optional[float]
    displayOrder: Optional[float]


class Market(BaseModel):
    id: int
    name: str
    image: str
    url: str
    contracts: List[Contract]
    timeStamp: str
    status: str


class PredictitResponse(BaseModel):
    markets: List[Market]
