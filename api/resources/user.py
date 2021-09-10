from api import Resource, abort, reqparse, auth
from api.models.user import UserModel
from api.schemas.user import user_schema, users_schema, UserSchema, UserRequestSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields


@doc(tags=['Users'])
class UserResource(MethodResource):
    @doc(
        summary="Get user by id",
        description="Returns user",
        produces=[
            'application/json'
        ],
        params={'user_id': {'description': 'user id'}},
        responses={
            "200": {

                "description": "Return user",
                "content":
                    {"application/json": []}

            },
            "404": {
                "description": "User not found"
            }
        }
    )
    @marshal_with(UserSchema, code="User")
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, error=f"User with id={user_id} not found")
        return user, 200

    @auth.login_required(role="admin")
    @doc(security=[{"basicAuth": []}])
    @doc(description='Edit user by id')
    @marshal_with(UserSchema)
    @use_kwargs({"username": fields.Str()})
    def put(self, user_id, **kwargs):
        # parser = reqparse.RequestParser()
        # parser.add_argument("username", required=True)
        # user_data = parser.parse_args()
        user = UserModel.query.get(user_id)
        user.username = kwargs["username"]
        user.save()
        return user, 200

    @auth.login_required(role="admin")
    @doc(security=[{"basicAuth": []}])
    @doc(description='Delete user by id')
    @marshal_with(UserSchema)
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, error=f"User with id={user_id} not found")
        user.delete()
        return user, 201


@doc(tags=['Users'])
class UsersListResource(MethodResource):
    @doc(description='Get user list')
    @marshal_with(UserSchema(many=True))
    def get(self):
        users = UserModel.query.all()
        return users, 200

    @auth.login_required(role="admin")
    @doc(security=[{"basicAuth": []}])
    @use_kwargs(UserRequestSchema, location='json')
    @doc(description='Post new user')
    @marshal_with(UserSchema)
    def post(self, **kwargs):
        # parser = reqparse.RequestParser()
        # parser.add_argument("username", required=True)
        # parser.add_argument("password", required=True)
        # user_data = parser.parse_args()
        user = UserModel(**kwargs)
        user.save()
        if not user.id:
            abort(400, error=f"User with username:{user.username} already exist")
        return user, 201
