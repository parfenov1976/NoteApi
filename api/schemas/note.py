from api import ma
from api.models.note import NoteModel
from api.schemas.user import UserSchema
from api.schemas.tag import TagSchema


#       schema        flask-restful
# object ------>  dict ----------> json

class NoteSchema(ma.SQLAlchemySchema):
    class Meta:
        model = NoteModel

    id = ma.auto_field()
    text = ma.auto_field()
    private = ma.auto_field()
    author = ma.Nested(UserSchema())
    tags = ma.Nested(TagSchema(many=True))
    archive = ma.auto_field()

    _links = ma.Hyperlinks({
        'self': ma.URLFor('noteresource', values=dict(note_id="<id>")),
        'collection': ma.URLFor('noteslistresource')
    })


note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)


# Десериализация запроса(request)
class NoteCreateSchema(ma.SQLAlchemySchema):
    class Meta:
        model = NoteModel

    text = ma.Str()
    private = ma.Bool()


class NoteEditSchema(ma.SQLAlchemySchema):
    class Meta:
        model = NoteModel

    text = ma.Str(required=False)
    private = ma.Bool(required=False)


class NoteFilterSchema(ma.SQLAlchemySchema):  # class Meta не указан т.к. данная схема не взаимодействует
    # с моделью, она взаимодествует с запросом и извлекает указанные поля из него
    private = ma.Bool(required=False)
    tag = ma.Str(required=False)
    username = ma.Str(required=False)
    # archive = ma.Bool(required=False)
