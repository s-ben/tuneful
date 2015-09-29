import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from database import Base, engine, session



# class Post(Base):
#     __tablename__ = "posts"

#     id = Column(Integer, primary_key=True)
#     title = Column(String(128))
#     body = Column(String(1024))
    
#     def as_dictionary(self):
#         post = {
#             "id": self.id,
#             "title": self.title,
#             "body": self.body
#         }
#         return post
        
class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    file = Column(Integer, ForeignKey('files.id'), nullable=False)
    
    def as_dictionary(self):
        song_info = session.query(File).filter_by(id=self.file).first()
        return {
            "id": self.id,
            "file":{
                "id": song_info.id,
                "name": song_info.name
                }
        }


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    name = Column(String(1024))
    song = relationship("Song", backref="songs", uselist=False)
    

    
    def as_dictionary(self):
        file = {
            "id": self.id,
            "filename": self.name,
            "path": url_for("uploaded_file", filename=self.name)
        }
        return file
    
  
    
# Base.metadata.create_all(engine)

