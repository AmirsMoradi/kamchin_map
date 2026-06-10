from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.supermarket_repository import SupermarketRepository
from app.schemas.supermarket_schema import SupermarketCreate, SupermarketResponse
from app.services.supermarket_service import SupermarketService

router = APIRouter(prefix="/markets", tags=["markets"])


def get_supermarket_service(db: Session = Depends(get_db)) -> SupermarketService:
    repository = SupermarketRepository(db)
    return SupermarketService(repository)


@router.get("", response_model=list[SupermarketResponse])
def get_markets(
    service: SupermarketService = Depends(get_supermarket_service),
):
    return service.list_markets()


@router.post(
    "",
    response_model=SupermarketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_market(
    data: SupermarketCreate,
    service: SupermarketService = Depends(get_supermarket_service),
):
    return service.create_market(data)


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_market(
    name: str,
    service: SupermarketService = Depends(get_supermarket_service),
):
    service.delete_market_by_name(name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
