class BaseRepository:

    def __init__(self, db, model):
        self.db = db
        self.model = model

    def save(self, entity):
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity):
        self.db.merge(entity)
        self.db.commit()
        return entity

    def delete(self, entity):
        self.db.delete(entity)
        self.db.commit()

    def find_all(self):
        return self.db.query(self.model).all()

    def find_by_id(self, entity_id):
        return self.db.get(self.model, entity_id)

    def find_by(self, *filters):
        return self.db.query(self.model).filter(*filters).all()
