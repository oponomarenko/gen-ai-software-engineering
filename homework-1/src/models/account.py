from pydantic import BaseModel


class BalanceResponse(BaseModel):
    accountId: str
    balance: float
    currency: str
