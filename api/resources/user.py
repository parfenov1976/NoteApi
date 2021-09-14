from api import Resource, abort, reqparse, auth, logging
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
        responses={
            "200": {
                "description": "User"
            },
            "404": {
                "description": "User not found"
            }
        },
    )
    @marshal_with(UserSchema, code=200)
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, error=f"User with id={user_id} not found")
        return user, 200

    @auth.login_required(role="admin")
    @doc(security=[{"basicAuth": []}])
    @doc(description='Edit user by id')
    @doc(summary="Edit user by id")
    @doc(responses={200: {"description": "User edited"}})
    @doc(responses={403: {"description": "You are not authorized to edit users"}})
    @doc(responses={404: {"description": "User not found"}})
    @marshal_with(UserSchema, code=200)
    @use_kwargs({"username": fields.Str()})
    def put(self, user_id, **kwargs):
        # parser = reqparse.RequestParser()
        # parser.add_argument("username", required=True)
        # user_data = parser.parse_args()
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, error=f"User with id={user_id} not found")
        user.username = kwargs["username"]
        user.save()
        return user, 200

    @auth.login_required(role="admin")
    @doc(security=[{"basicAuth": []}])
    @doc(description='Delete user by id')
    @doc(summary="Delete user by id")
    @doc(responses={200: {"description": "User deleted"}})
    @doc(responses={403: {"description": "You are not authorized to delete users"}})
    @doc(responses={404: {"description": "User not found"}})
    @marshal_with(UserSchema, code=201)
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, error=f"User with id={user_id} not found")
        user.delete()
        return user, 201


@doc(tags=['Users'])
class UsersListResource(MethodResource):
    @doc(description='Get users list')
    @doc(summary="Get users list")
    @doc(responses={200: {"description": "Users list"}})
    @doc(responses={400: {"description": "User with same username is already exist"}})
    @marshal_with(UserSchema(many=True), code=200)
    def get(self):
        users = UserModel.query.all()
        return users, 200

    @use_kwargs(UserRequestSchema, location='json')
    @doc(description='Post new user')
    @doc(summary="Post new user")
    @doc(responses={200: {"description": "User posted"}})
    @marshal_with(UserSchema, code=201)
    def post(self, **kwargs):
        # parser = reqparse.RequestParser()
        # parser.add_argument("username", required=True)
        # parser.add_argument("password", required=True)
        # user_data = parser.parse_args()
        user = UserModel(**kwargs)
        user.save()
        if not user.id:
            abort(400, error=f"User with username:{user.username} is already exist")
        logging.info("User create")
        return user, 201
