from api import api, app, docs
from api.resources.note import NoteResource, NotesListResource, NoteSetTagsResource, NotesRestoreResource
from api.resources.user import UserResource, UsersListResource
from api.resources.auth import TokenResource
from api.resources.tag import TagsResource, TagsListResource
from config import Config
from api import Message, mail

# CRUD

# Create --> POST
# Read --> GET
# Update --> PUT
# Delete --> DELETE
api.add_resource(UsersListResource,
                 '/users',
                 )  # GET, POST
api.add_resource(UserResource,
                 '/users/<int:user_id>',
                 )  # GET, PUT, DELETE

api.add_resource(TokenResource,
                 '/auth/token',
                 )  # GET
api.add_resource(TagsResource,
                 '/tags/<int:tag_id>',
                 )
api.add_resource(TagsListResource,
                 '/tags',
                 )
api.add_resource(NotesListResource,
                 '/notes',  # GET, POST
                 )
api.add_resource(NoteResource,
                 '/notes/<int:note_id>',  # GET, PUT, DELETE
                 )
api.add_resource(NotesRestoreResource,
                 '/notes/<int:note_id>/restore',
                 )
api.add_resource(NoteSetTagsResource,
                 '/notes/<int:note_id>/tags',
                 )
# api.add_resource(NoteFilterResource,
#                  '/notes/filter',
#                  )
# api.add_resource(NoteFilterByUsernameResource,
#                  '/notes/public/filter',  # GET
#                  )
# api.add_resource(NoteFilterPublicResource,
#                  '/notes/public'
#                  )

docs.register(UserResource)
docs.register(UsersListResource)
docs.register(TagsResource)
docs.register(TagsListResource)
docs.register(NoteResource)
docs.register(NotesListResource)
docs.register(NotesRestoreResource)
docs.register(NoteSetTagsResource)
# docs.register(NoteFilterResource)
# docs.register(NoteFilterByUsernameResource)
# docs.register(NoteFilterPublicResource)

msg = Message('test subject', sender=Config.ADMINS[0], recipients=Config.ADMINS)
msg.body = 'Server started'
msg.html = 'Server started'


if __name__ == '__main__':
    # with app.app_context(): # для отправки почтовых сообщения снять комент
    #     mail.send(msg)
    app.run(debug=Config.DEBUG, port=Config.PORT)
