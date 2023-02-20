import os
import shutil

from fastapi import UploadFile

MEDIA_ROOT = "storage"


class Storage:
    def upload(self, file):
        raise NotImplementedError


class LocalStorage(Storage):
    def __init__(self, root=MEDIA_ROOT):
        self.root = root

    def upload(self, file: UploadFile) -> str:
        path = os.path.join(self.root, file.filename)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return path
