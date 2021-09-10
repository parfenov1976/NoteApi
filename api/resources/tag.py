from api import auth, abort, g, Resource, reqparse
from api.models.tag import TagModel
from api.schemas.tag import TagSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields


@doc(tags=['Tags'])
class TagsResource(MethodResource):
    @doc(
        summary="Get tag by id",
        description="Returns tag",
        produces=[
            'application/json'
        ],
        params={'tag_id': {'description': 'tag id'}},
        responses={
            "200": {

                "description": "Return tag",
                "content":
                    {"application/json": []}

            },
            "404": {
                "description": "Tag not found"
            }
        }
    )
    @marshal_with(TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get(tag_id)
        if not tag:
            abort(404, error=f"Tag with id={tag_id} not found")
        return tag, 200


@doc(tags=['Tags'])
class TagsListResource(MethodResource):
    @doc(
        summary="Get all tags",
        description="Returns all tags",
        produces=[
            'application/json'
        ],
        responses={
            "200": {

                "description": "Return all tags",
                "content":
                    {"application/json": []}

            }
        }
    )
    @marshal_with(TagSchema(many=True))
    def get(self):
        tags = TagModel.query.all()
        return tags, 200

    @doc(
        summary="Create new tag",
        description="Returns created tag",
        produces=[
            'application/json'
        ],
        responses={
            "201": {

                "description": "Returns created tag",
                "content":
                    {"application/json": []}

            }
        }
    )
    @use_kwargs({"name": fields.Str()})
    @marshal_with(TagSchema)
    def post(self, **kwargs):
        tag = TagModel(**kwargs)
        tag.save()
        return tag, 201
