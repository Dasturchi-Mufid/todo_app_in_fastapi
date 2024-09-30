import logging

from typing import Any,Union

from .models import Todo

from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

object_type_hint = Todo
objects_type_hints = list[Todo] | list


class ORMBase:

    def __init__(self, model):
        self.model = model

    def get(self,db:Session,id:int):
        return db.query(self.model).filter(self.model.id == id).first()

    def create(self, db: Session, **object_data: dict):
        try:
            object_data = self.model(**object_data)
            db.add(object_data)
            db.commit()
            db.refresh(object_data)
            return object_data
        except IntegrityError:
            logging.info("Already added to the database")
        except Exception as e:
            logging.error(f"An error accured: {e}")
        return db.query(self.model).filter(self.model)

    def update(self,db:Session,id:int,**updated_data) -> object_type_hint:

        try:
            object = db.query(self.model).get(id)
            if object:
                for key, value in updated_data.items():
                    setattr(object, key, value)
                db.commit()
                return object
            else:
                logging.info(f"Object with {id} not found")
        except Exception as e:
            logging.error(f"An error accured: {e}")
            raise
    
    def delete(self, db: Session, id: int) -> Any:
        try:
            object = db.query(self.model).get(id)
            if object:
                db.delete(object)
                db.commit()
                return True
            else:
                logging.info(f"Object with {id} not found")
        except Exception as e:
            logging.error(f"An error accured: {e}")
            return False

    def all(self,db:Session) -> objects_type_hints:
        return db.query(self.model).all()
    
    def filter(self, db: Session, **filters) -> objects_type_hints:
        try:
            query = db.query(self.model)
            conditions = []
            
            for key, value in filters.items():
                if hasattr(self.model,key):
                    conditions.append(getattr(self.model, key) == value)
            if 'logic' in filters and filters['logic'].lower() == 'or':
                query = query.filter(or_(*conditions))
            else:
                query = query.filter(and_(*conditions))
            
            return query.all()
        except Exception as e:
            logging.error(f"An error accured: {e}")
            raise
    
    def count(self, db: Session) -> int:
        return db.query(self.model).count()
    
    def get_or_create(self, db: Session, **data) -> object_type_hint:
        get =self.get(db,data['id'])
        if get is not None:
            return self.create(db,**data)
        else:return get
        

TodoDB = ORMBase(model=Todo)