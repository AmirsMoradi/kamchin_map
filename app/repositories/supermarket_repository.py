from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.supermarket_model import Supermarket


class SupermarketRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Supermarket).all()

    def get_by_id(self, market_id: int):
        return self.db.query(Supermarket).filter(Supermarket.id == market_id).first()

    def get_by_name(self, name: str):
        return self.db.query(Supermarket).filter(Supermarket.name == name).first()

    def create(self, data: dict):
        try:
            market = Supermarket(**data)
            self.db.add(market)
            self.db.commit()
            self.db.refresh(market)
            return market
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def update(self, market: Supermarket, update_data: dict):
        try:
            for key, value in update_data.items():
                if value is not None:
                    setattr(market, key, value)
            self.db.commit()
            self.db.refresh(market)
            return market
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def delete(self, market: Supermarket):
        try:
            self.db.delete(market)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def find_by_id(self, market_id: int):
        return self.db.query(Supermarket).filter(Supermarket.id == market_id).first()

    def find_by_name(self, name: str):
        return self.db.query(Supermarket).filter(Supermarket.name == name).first()

    def find_all(self):
        return self.db.query(Supermarket).all()

    def find_by(self, **kwargs):
        return self.db.query(Supermarket).filter_by(**kwargs).all()
