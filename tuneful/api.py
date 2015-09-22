import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

import models
import decorators
from tuneful import app
from database import session
from utils import upload_path





@app.route("/api/songs", methods=["GET"])
# @decorators.accept("application/json")
def songs_get():
    """ Get songs endpoint """
    # Get the post from the database
    songs = session.query(models.Song).all()
    # songs = songs.order_by(models.Song.id)
    
    # create list of dictionaries containing song info
    song_dictionaries = []
    for song in songs:
        song_dictionaries.append(song.as_dictionary())

    data = json.dumps(song_dictionaries)
    # print type(songs)
    # data = json.dumps(song

    # Check whether the post exists
    # If not return a 404 with a helpful message
    # if not post:
    #     message = "Could not find post with id {}".format(id)
    #     data = json.dumps({"message": message})
    #     return Response(data, 404, mimetype="application/json")

    # # Return the post as JSON
    # data = json.dumps(post.as_dictionary())
    
    return Response(data, 200, mimetype="application/json")
    
@app.route("/api/songs", methods=["POST"])
# @decorators.accept("application/json")
def songs_add():
    """ Add songs endpoint """
    # Get the post from the database
    data = request.json
    
    # Create song object
    song = models.Song(file=data["file"]["id"])
    # Add song to database
    session.add(song)
    session.commit()  
    
    return_data = json.dumps(song.as_dictionary())
    return Response(return_data, 201,  mimetype="application/json")
    
@app.route("/api/songs/<int:id>", methods=["PUT"])
# @decorators.accept("application/json")
def songs_edit(id):
    """ Edit songs endpoint """
    # Get the song from the database
    song = session.query(models.Song).get(id)
    
    # Check to make sure the post exists
    if not song:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")
    
    # Extract the JSON data to a dictionary
    data = request.json
    # Update file of song object
    song.file = data["file"]["id"]
    # Commit change to database
    session.commit()    
    
    return_data = json.dumps(song.as_dictionary())
    return Response(return_data, 200,  mimetype="application/json")
    
@app.route("/api/songs/<int:id>", methods=["DELETE"])
# @decorators.accept("application/json")
def songs_delete(id):
    """ Delete songs endpoint """
    # Get the song from the database
    song = session.query(models.Song).get(id)
    # Check to make sure the post exists
    if not song:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    # Return the post as JSON
    data = json.dumps(song.as_dictionary())
    session.delete(song)
    return Response(data, 200, mimetype="application/json")

@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)
    
@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
    file = request.files.get("file")
    if not file:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")

    filename = secure_filename(file.filename)
    db_file = models.File(name=filename)
    session.add(db_file)
    session.commit()
    file.save(upload_path(filename))

    data = db_file.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")