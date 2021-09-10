from api import auth, abort, g, Resource, reqparse
from api.models.note import NoteModel
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

    # TODO: Check return >kwargs.get("private") OR kwargs["private"]
    @auth.login_required
    @doc(description='Edit note by id')
    @marshal_with(NoteSchema)
    # TODO: Check kwargs
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

    # TODO: Check return > возможна потеря автора
    @auth.login_required
    @doc(description='Delete note by id')
    @marshal_with(NoteSchema)
    def delete(self, note_id):
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id:{note_id} not found")
        # note_dict = note
        note.delete()
        return note, 200


@doc(security=[{"basicAuth": []}])
@doc(tags=['Notes'])
class NotesListResource(MethodResource):
    @auth.login_required
    @doc(description='Get notes list')
    @marshal_with(NoteSchema(many=True))
    # TODO: check
    def get(self):
        author = g.user
        notes = NoteModel.query.filter_by(author_id=author.id)
        return notes, 200

    @auth.login_required
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
    @doc(summary="Set tags to Note")
    @use_kwargs({"tags": fields.List(fields.Int())}, location='json')
    @marshal_with(NoteSchema)
    def put(self, note_id, **kwargs):
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"note {note_id} not found")
        print("note kwargs = ", kwargs)
        ...
        ...
        return note, 200
