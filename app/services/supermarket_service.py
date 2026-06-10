from fastapi import HTTPException, status

from app.schemas.supermarket_schema import SupermarketCreate


class SupermarketService:
    def __init__(self, repository):
        self.repository = repository

    def create_market(self, data: SupermarketCreate):
        payload = data.model_dump()
        return self.repository.create(payload)

    def list_markets(self):
        return self.repository.get_all()

    def get_market(self, market_id: int):
        market = self.repository.get_by_id(market_id)
        if market is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supermarket not found",
            )
        return market

    def delete_market_by_name(self, name: str) -> None:
        market = self.repository.get_by_name(name.strip())
        if market is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supermarket not found",
            )
        self.repository.delete(market)
