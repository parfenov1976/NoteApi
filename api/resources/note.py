from api import auth, abort, g, Resource, reqparse
from api.models.note import NoteModel
from api.models.user import UserModel
from api.models.tag import TagModel
from api.schemas.note import note_schema, notes_schema, NoteSchema, NoteCreateSchema, NoteEditSchema, NoteFilterSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields
from sqlalchemy.orm.exc import NoResultFound
import pdb


@doc(security=[{"basicAuth": []}])
@doc(tags=['Notes'])
class NoteResource(MethodResource):
    @auth.login_required
    @doc(description='Returns note by id')
    @doc(summary="Get note by id")
    @doc(responses={200: {"description": "Note by id"}})
    @doc(responses={404: {"description": "Note not found"}})
    @doc(responses={403: {"description": "You are not authorized to get notes of other users"}})
    @marshal_with(NoteSchema, code=200)
    def get(self, note_id):
        author = g.user
        try:
            note = NoteModel.get_all_for_user(author).filter_by(id=note_id).one()
            return note, 200
        except NoResultFound:
            abort(404, error=f"Note with id={note_id} not found")

    @auth.login_required
    @doc(description='Edit note by id')
    @doc(summary="Edit note by id")
    @doc(responses={200: {"description": "Note is edited"}})
    @doc(responses={404: {"description": "Note not found"}})
    @doc(responses={403: {"description": "You are not authorized to edit notes of other users"}})
    @doc(responses={304: {"description": "Not modified"}})
    @use_kwargs(NoteEditSchema, location='json')
    @marshal_with(NoteSchema, code=200)
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
        if kwargs.get("text") is not None:
            note.text = kwargs.get("text")
        if kwargs.get("private") is not None:
            if kwargs.get("private") == note.private:
                return {}, 304
            note.private = kwargs.get("private")
        note.save()
        return note, 200

    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @doc(description='Move note by id to archive')
    @doc(summary="Move note by id to archive")
    @doc(responses={404: {"description": "Note not found"}})
    @doc(responses={403: {"description": "You are not authorized to archive notes of other users"}})
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
    @doc(description='Returns notes list by filters')
    @doc(summary="Get notes list by filters")
    @doc(responses={200: {"description": "Notes list"}})
    @marshal_with(NoteSchema(many=True), code=200)
    @use_kwargs(NoteFilterSchema, location='query')
    def get(self, **kwargs):
        author = g.user
        notes = NoteModel.get_all_for_user(author)
        if kwargs.get('tag') is not None:
            notes = notes.filter(NoteModel.tags.any(name=kwargs['tag']))
        if kwargs.get('private') is not None:
            notes = notes.filter_by(private=kwargs['private'])
        if kwargs.get('username') is not None:
            notes = notes.filter(NoteModel.author.has(username=kwargs['username']))
        return notes, 200

    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    @use_kwargs(NoteCreateSchema, location='json')
    @doc(description='Post new note')
    @doc(summary="Post new note")
    @doc(responses={201: {"description": "Note posted"}})
    @marshal_with(NoteSchema, code=201)
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
class NotesRestoreResource(MethodResource):
    @doc(description='Restore notes from archive')
    @doc(summary="Restore notes from archive")
    @doc(responses={200: {"description": "Note restored"}})
    @doc(responses={304: {"description": "Not modified"}})
    @marshal_with(NoteSchema, code=200)
    def put(self, note_id):
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id={note_id} not found")
        if not note.archive:
            return {}, 304
        note.restore()
        return note, 200


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

# @doc(tags=['NotesFilter'])
# class NoteFilterResource(MethodResource):
#     # GET: /notes/filter?tag=<tag_name> преобразовать к указаному ниже
#     # GET: /notes?tag=<tag_name>
#     @auth.login_required
#     @doc(security=[{"basicAuth": []}])
#     @doc(description="Returns list notes by tag name")
#     @doc(summary="Get list notes by tag name")
#     @doc(responses={200: {"description": "List with notes filtered by tag name"}})
#     @doc(responses={400: {"description": "Tag name missing"}})
#     @use_kwargs({"tag": fields.Str()}, location='query')
#     @marshal_with(NoteSchema(many=True), code=200)
#     def get(self, **kwargs):
#         author = g.user
#         try:
#             notes = NoteModel.query.filter(NoteModel.tags.any(name=kwargs["tag"]), NoteModel.author_id == author.id)
#             return notes, 200
#         except KeyError:
#             abort(400, error="Tag name missing")
#
#
# @doc(tags=['NotesFilter'])
# class NoteFilterByUsernameResource(MethodResource):
#     # GET: /notes/public/filter?username=<un>  преобразовать к указаному ниже
#     # GET: /notes?public=True&username=<un>&tag=<tag_name> по одному из фильтров или по их комбинации
#     # GET: /notes?public=True&tag=<tag_name> - текущая разработка
#     @doc(description="Returns list of user's public notes")
#     @doc(summary="Get list of public notes by username")
#     @doc(responses={200: {"description": "List with public notes filtered by username"}})
#     @doc(responses={400: {"description": "Username missing"}})
#     @doc(responses={404: {"description": "User not found"}})
#     @use_kwargs({"username": fields.Str()}, location='query')
#     @marshal_with(NoteSchema(many=True), code=200)
#     def get(self, **kwargs):
#         try:
#             user = UserModel.query.filter_by(username=kwargs["username"]).all()
#             if not user:
#                 abort(404, error=f'User with username={kwargs["username"]} not found')
#         except KeyError:
#             abort(400, error="Username missing")
#         notes = NoteModel.query.filter(NoteModel.author.has(username=kwargs["username"]), NoteModel.private == False)
#         return notes, 200
#
#
# @doc(tags=['NotesFilter'])
# class NoteFilterPublicResource(MethodResource):
#     @doc(description="Returns list of public notes")
#     @doc(summary="Get list of public notes")
#     @doc(responses={200: {"description": "List with public notes"}})
#     @marshal_with(NoteSchema(many=True), code=200)
#     # GET: /notes/public
#     def get(self):
#         notes = NoteModel.query.filter_by(private=False)
#         return notes, 200
