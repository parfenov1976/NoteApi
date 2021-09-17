import os
from config import Config, ma_plugin
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from marshmallow import fields
from api import api, abort, logging
from api.models.image import ImageModel


@ma_plugin.map_to_openapi_type('file', None)
class FileField(fields.Raw):
    pass


@doc(tags=['Files'])
@api.resource('/upload')  # альтернативный вариант прописывния урла
class UploadPictureResource(MethodResource):
    @doc(description='Upload image')
    @doc(summary="Upload image")
    @doc(responses={200: {"description": "Image uploaded"}})
    @use_kwargs({"image": FileField(required=True)}, location="files")
    def put(self, **kwargs):
        uploaded_file = kwargs["image"]
        target = os.path.join(Config.UPLOAD_FOLDER, uploaded_file.filename)
        image = ImageModel(image_url=target)
        image.save()
        if not image.id:
            abort(400, error=f"Image with name:{uploaded_file.filename} is already exist")
        uploaded_file.save(target)
        logging.info(f"Image uploaded {target}")
        return {"msg": "uploaded image successfully",
                "url": os.path.join(Config.UPLOAD_FOLDER_NAME, uploaded_file.filename),
                "id": image.id}, 200
