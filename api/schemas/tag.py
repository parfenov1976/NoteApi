from api import ma
from api.models.tag import TagModel


#       schema        flask-restful
# object ------>  dict ----------> json


# Сериализация ответа(response)
class TagSchema(ma.SQLAlchemySchema):
    class Meta:
        model = TagModel

    id = ma.auto_field()
    name = ma.auto_field()

    _links = ma.Hyperlinks({
        'self': ma.URLFor('tagsresource', values=dict(tag_id="<id>")),
        'collection': ma.URLFor('tagslistresource')
    })

# Десериализация запроса(request)
# class UserRequestSchema(ma.SQLAlchemySchema):
#     class Meta:
#         model = UserModel
#
#     username = ma.Str()
#     password = ma.Str()
#
#
# user_schema = UserSchema()
# users_schema = UserSchema(many=True)