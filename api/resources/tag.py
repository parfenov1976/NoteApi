from api import auth, abort, g, Resource, reqparse
from api.models.tag import TagModel
from api.schemas.tag import TagSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields


@doc(tags=['Tags'])
class TagsResource(MethodResource):
    @doc(description="Returns tag")
    @doc(summary="Get tag by id")
    @doc(responses={200: {"description": "Tag by id"}})
    @doc(responses={404: {"description": "Tag not found"}})
    @marshal_with(TagSchema, code=200)
    def get(self, tag_id):
        tag = TagModel.query.get(tag_id)
        if not tag:
            abort(404, error=f"Tag with id={tag_id} not found")
        return tag, 200

    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @doc(description="Returns changed tag")
    @doc(summary="Change tag name")
    @doc(responses={201: {"description": "Tag name changed"}})
    @doc(responses={404: {"description": "Tag not found"}})
    @use_kwargs({"name": fields.Str()})
    @marshal_with(TagSchema, code=201)
    def put(self, tag_id, **kwargs):
        tag = TagModel.query.get(tag_id)
        if not tag:
            abort(404, error=f"Tag with id={tag_id} not found")
        tag.name = kwargs["name"]
        tag.save()
        return tag, 201

    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @doc(description="Deletes tag")
    @doc(summary="Deletes tag by id")
    @doc(responses={201: {"description": "Tag deleted"}})
    @doc(responses={404: {"description": "Tag not found"}})
    @marshal_with(TagSchema, code=201)
    def delete(self, tag_id):
        tag = TagModel.query.get(tag_id)
        if not tag:
            abort(404, error=f"Tag with id={tag_id} not found")
        tag.delete()
        return tag, 201


@doc(tags=['Tags'])
class TagsListResource(MethodResource):
    @doc(description="Returns all tags")
    @doc(summary="Get all tags")
    @doc(responses={200: {"description": "List of all tags"}})
    @marshal_with(TagSchema(many=True), code=200)
    def get(self):
        tags = TagModel.query.all()
        return tags, 200

    @doc(description="Returns created tag")
    @doc(summary="Create new tag")
    @doc(responses={201: {"description": "Created tag"}})
    @use_kwargs({"name": fields.Str()})
    @marshal_with(TagSchema, code=201)
    def post(self, **kwargs):
        tag = TagModel(**kwargs)
        tag.save()
        return tag, 201
