from api import db
from sqlalchemy.exc import IntegrityError


class ImageModel(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), unique=True, nullable=False)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"Image id={self.id}, path={self.name}"
