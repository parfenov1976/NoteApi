from api import db
from sqlalchemy.exc import IntegrityError
from api.models.user import UserModel


class TagModel(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    # author_id = db.Column(db.Integer, db.ForeignKey(UserModel.id))

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
        return f"Tag {self.name}"
