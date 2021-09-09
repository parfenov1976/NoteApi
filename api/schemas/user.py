from api import ma
from api.models.user import UserModel


#       schema        flask-restful
# object ------>  dict ----------> json


# Сериализация ответа(response)
class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = UserModel
        # fields = ('id', 'username')

    id = ma.auto_field()
    username = ma.auto_field()
    is_staff = ma.auto_field()
    role = ma.auto_field()


user_schema = UserSchema()
users_schema = UserSchema(many=True)