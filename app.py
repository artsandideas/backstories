#!/usr/bin/env python
import os
import sys
from flask import Flask, render_template, request, jsonify
from flask.ext.cors import CORS

from spider import CustomStoryDatabase
from stupeflix import StupeflixApi
from conf import DBS, DEFAULT_AUDIO

app = Flask(__name__)
cors = CORS(app)

@app.route("/")
def home():
    args = {'stories': [], 'errors': [], 'dbs': DBS.keys()}
    if 'db-name' in request.args:
        db_name = request.args['db-name']
        try:
            query_url = DBS[db_name]
        except KeyError:
            errors.append('Invalid db_name, set it in app.py')
        else:
            spider_limit = request.args.get('spider-level', 'all')
            args['stories'] = CustomStoryDatabase(db_name).getSpiderRows(query_url, spider_limit=spider_limit)
            # Sort by publish date, puts the stories without dates at the top
            args['stories'] = filter(lambda s: s.get('headline') and s.get('publish_date') and s.get('path_length') != 0, args['stories'])
            args['stories'] = sorted(args['stories'], key=lambda s: s.get('publish_date'))
    return render_template('index.html', **args)

@app.route("/stupefy.json", methods=["POST"])
def stupefy():
    data = request.get_json(force=True)
    if not data.get('stories'):
        return jsonify({'status': 'failed', 'message': 'No stories in POST data.'})
    audio = data.get('audio') or DEFAULT_AUDIO
    stories = filter(lambda s: s.get('img') is not None and s.get('headline') is not None, data['stories'])
    api = StupeflixApi(audio=audio)
    print 'Creating video...'
    video = api.create_video(stories)
    key = video[0]['key']
    print '\tKey is %s' % key
    return jsonify(video[0])

@app.route("/stupestatus.json", methods=["GET"])
def stupestatus():
    if 'key' in request.args:
        key = request.args.get('key')
        resp = StupeflixApi().status(key)
        return jsonify(resp[0])
    return jsonify({'success': False})

if __name__ == "__main__":
    app.run(debug=True)
