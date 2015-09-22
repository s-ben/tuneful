import unittest
import os
import shutil
import json
from urlparse import urlparse
from StringIO import StringIO

import sys; print sys.modules.keys()
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())

    def test_get_songs(self):
        """ Filtering posts by body and title"""
        file_A = models.File(filename="File A")
        file_B = models.File(filename="File B")
   
        session.add_all([file_A, file_B])
        session.commit()     
        # song_A.file = file_A
        # file_A.song = song_A
        
        song_A = models.Song(file_id=file_A.id)
        song_B = models.Song(file_id=file_B.id)
        
        session.add_all([song_A, song_B])
        session.commit()  
    
    
        response = self.client.get("/api/songs",
            headers=[("Accept", "application/json")]
        )

        
        data = json.loads(response.data)
        # print response.data['id']
        # print data[0]['file']['name']
        
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        # song_filename = data[0]['file']['name']
        # self.assertEqual(song_filename, "File A")
        
        song_test_A = data[0]
        self.assertEqual(song_test_A["id"], 1)
        self.assertEqual(song_test_A["file"]["name"], "File A")
        
        song_test_B = data[1]
        self.assertEqual(song_test_B["id"], 2)
        self.assertEqual(song_test_B["file"]["name"], "File B")
        # posts = json.loads(response.data)
        # self.assertEqual(len(posts), 1)

        # post = posts[0]
        # self.assertEqual(post["title"], "Post with whistles")
        # self.assertEqual(post["body"], "Still a test")
    def test_post_songs(self):
        """ Filtering posts by body and title"""
        file_A = models.File(filename="File A")
        # file_B = models.File(filename="File B")
        session.add(file_A)
        session.commit()    
        
        song_data = {
                    "file": 
                        {
                        "id": file_A.id
                        }
                    }
                    
        response = self.client.post("/api/songs",
            data = json.dumps(song_data),
            content_type="application/json",
            headers=[("Accept", "application/json")],
        )  
        return_data = json.loads(response.data)
        print return_data
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        
        song_filename= return_data["file"]["name"]
        self.assertEqual(song_filename, "File A")
        self.assertEqual(return_data["id"], 1)

        # print response.data
    def test_post_songs_edit(self):
        """ Filtering posts by body and title"""
        file_A = models.File(filename="File A")
        file_B = models.File(filename="File B")
        session.add_all([file_A, file_B])
        session.commit()    
        
        song_A = models.Song(file_id=file_A.id)
        # song_B = models.Song(file_id=file_B.id)
        
        session.add(song_A)
        session.commit()  
        
        song_data_edited = {
                    "file": 
                        {
                        "id": file_B.id
                        }
                    }
                    
        response = self.client.put("/api/songs/{}".format(song_A.id),
            data = json.dumps(song_data_edited),
            content_type="application/json",
            headers=[("Accept", "application/json")],
        )  
        return_data = json.loads(response.data)
        print return_data
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        
        # song_filename= return_data["file"]["id"]
        # self.assertEqual(song_filename, "File A")
        self.assertEqual(return_data["file"]["id"], file_B.id)
        
        
    def test_songs_delete(self):
        """ Delete song by song id"""
        file_A = models.File(filename="File A")
        session.add(file_A)
        session.commit()    
        
        song_A = models.Song(file_id=file_A.id)
        session.add(song_A)
        session.commit()  
        
                    
        response = self.client.delete("/api/songs/{}".format(song_A.id),
            headers=[("Accept", "application/json")],
        )  
        return_data = json.loads(response.data)
        print return_data
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        
        songs = session.query(models.Song).all()
        # song_filename= return_data["file"]["id"]
        # self.assertEqual(song_filename, "File A")
        self.assertEqual(len(songs), 0)       
        
    def test_get_uploaded_file(self):
        path =  upload_path("test.txt")
        with open(path, "w") as f:
            f.write("File contents")

        response = self.client.get("/uploads/test.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/plain")
        self.assertEqual(response.data, "File contents")
        
    def test_file_upload(self):
        data = {
            "file": (StringIO("File contents"), "test.txt")
        }

        response = self.client.post("/api/files",
            data=data,
            content_type="multipart/form-data",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(urlparse(data["path"]).path, "/uploads/test.txt")

        path = upload_path("test.txt")
        self.assertTrue(os.path.isfile(path))
        with open(path) as f:
            contents = f.read()
        self.assertEqual(contents, "File contents")
        