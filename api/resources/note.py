from api import auth, abort, g, Resource, reqparse
from api.models.note import NoteModel
from api.models.user import UserModel
from api.models.tag import TagModel
from api.schemas.note import note_schema, notes_schema, NoteSchema, NoteRequestSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields


@doc(security=[{"basicAuth": []}])
@doc(tags=['Notes'])
class NoteResource(MethodResource):
    @auth.login_required
    @doc(description='Get note by id')
    @marshal_with(NoteSchema)
    def get(self, note_id):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id={note_id} not found")
        if note.author != author:
            abort(403, error=f"Forbidden")
        return note, 200

    @auth.login_required
    @doc(description='Edit note by id')
    @marshal_with(NoteSchema)
    @use_kwargs(NoteRequestSchema, location='json')
    def put(self, note_id, **kwargs):
        author = g.user
        # parser = reqparse.RequestParser()
        # parser.add_argument("text", required=True)
        # parser.add_argument("private", type=bool)
        # note_data = parser.parse_args()
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"note {note_id} not found")
        if note.author != author:
            abort(403, error=f"Forbidden")
        note.text = kwargs["text"]
        note.private = kwargs["private"] or note.private
        note.save()
        return note, 200

    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @doc(description='Delete note by id')
    @doc(responses={404: {"description": "Note not found"}})
    @doc(responses={403: {"description": "You are not authorized to delete notes of other users"}})
    @marshal_with(NoteSchema, code=200)
    def delete(self, note_id):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id:{note_id} not found")
        if note.author != author:
            abort(403, error=f"Forbidden")
        note.delete()
        return note, 200


@doc(security=[{"basicAuth": []}])
@doc(tags=['Notes'])
class NotesListResource(MethodResource):
    @auth.login_required
    @doc(description='Get notes list')
    @marshal_with(NoteSchema(many=True))
    def get(self):
        author = g.user
        notes = NoteModel.query.filter_by(author_id=author.id)
        return notes, 200

    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @use_kwargs(NoteRequestSchema, location='json')
    @doc(description='Post new note')
    @marshal_with(NoteSchema)
    def post(self, **kwargs):
        author = g.user
        # parser = reqparse.RequestParser()
        # parser.add_argument("text", required=True)
        # parser.add_argument("private", type=bool)
        # note_data = parser.parse_args()
        note = NoteModel(author_id=author.id, **kwargs)
        note.save()
        return note, 201


@doc(tags=['Notes'])
class NoteSetTagsResource(MethodResource):
    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @doc(description="Return note after setting tags")
    @doc(summary="Set tags to Note")
    @doc(responses={200: {"description": "Tags were set"}})
    @doc(responses={404: {"description": "Note not found"}})
    @doc(responses={403: {"description": "You are not authorized to tags notes of other users"}})
    @use_kwargs({"tags": fields.List(fields.Int())}, location='json')
    @marshal_with(NoteSchema, code=200)
    def put(self, note_id, **kwargs):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id={note_id} not found")
        if note.author != author:
            abort(403, error=f"Forbidden")
        for tag_id in kwargs["tags"]:
            tag = TagModel.query.get(tag_id)
            note.tags.append(tag)
        note.save()
        return note, 200

    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @doc(description="Returns note after deleting tags")
    @doc(summary="Delete tags from note by tags id")
    @doc(responses={200: {"description": "Tags was delete"}})
    @doc(responses={400: {"description": "List of tag ids not match to note tags"}})
    @doc(responses={404: {"description": "Note not found"}})
    @doc(responses={403: {"description": "You are not authorized to untags notes of other users"}})
    @use_kwargs({"tags": fields.List(fields.Int())}, location='json')
    @marshal_with(NoteSchema, code=200)
    def delete(self, note_id, **kwargs):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id={note_id} not found")
        if not set(kwargs['tags']) <= set([el.id for el in note.tags]):
            abort(400, error=f"List of tag ids not match to note tags")
        if note.author != author:
            abort(403, error=f"Forbidden")
        for tag_id in kwargs["tags"]:
            tag = TagModel.query.get(tag_id)
            note.tags.remove(tag)
        note.save()
        return note, 200


@doc(tags=['NotesFilter'])
class NoteFilterResource(MethodResource):
    # GET: /notes/filter?tag=<tag_name>
    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @doc(description="Returns list notes by tag name")
    @doc(summary="Get list notes by tag name")
    @doc(responses={200: {"description": "List with notes filtered by tag name"}})
    @doc(responses={400: {"description": "Tag name missing"}})
    @use_kwargs({"tag": fields.Str()}, location='query')
    @marshal_with(NoteSchema(many=True), code=200)
    def get(self, **kwargs):
        author = g.user
        try:
            notes = NoteModel.query.filter(NoteModel.tags.any(name=kwargs["tag"]), NoteModel.author_id == author.id)
            return notes, 200
        except KeyError:
            abort(400, error="Tag name missing")


@doc(tags=['NotesFilter'])
class NoteFilterByUsernameResource(MethodResource):
    # GET: /notes/public/filter?username=<un>
    # TODO доделать - список публичных заметок по имени пользователя
    @use_kwargs({"username": fields.Str()}, location='query')
    @marshal_with(NoteSchema(many=True), code=200)
    def get(self, **kwargs):
        notes = NoteModel.query.filter(NoteModel.author.has(username=kwargs["username"]))
        return notes, 200

# TODO доделать - список публичных заметок
