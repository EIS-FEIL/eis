from eis.model.entityhelper import *
log = logging.getLogger(__name__)

class Deletefile(EntityHelper, Base):
    """Viited S3 failidele, mis tuleks kustutada, kuna on salvestatud uus versioon
    """
    __tablename__ = 'deletefile'
    id = Column(Integer, primary_key=True, autoincrement=True)
    object_name = Column(String(60)) # MinIO objekt

    def __init__(self, path):
        self.object_name = path
        Session.add(self)

# client.remove_object(bucket_name, path)
