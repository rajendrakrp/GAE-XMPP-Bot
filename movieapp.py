import urllib, re, json
from flask import Flask, make_response, request
from google.appengine.api import urlfetch, xmpp

IMDB = "http://www.omdbapi.com/"

app = Flask(__name__)

def parse_movie(movie):

    movie = re.sub(r'[^a-zA-Z0-9\']+', ' ', movie)
    movie = urllib.urlencode({"t" : movie})
    return movie
    
def get_imdb_results(movie):

    full_url = IMDB + "?" + movie
    imdb_result = urlfetch.fetch(full_url)
    json_data = json.loads(imdb_result.content)
    if isinstance(json_data, dict) and json_data.has_key('error'):
        return None, json_data.get('Error')
    return "success", json_data
    
@app.route('/_ah/xmpp/message/chat/', methods=['GET', 'POST'])
def send_results():

    message = xmpp.Message(request.form)
    movie = message.body.strip()
    movie = parse_movie(movie)
    status, results = get_imdb_results(movie)
    if not status:
        message.reply(str(results))
    else:
        rating = results.get('imdbRating', "Ratings not found")
        plot = results.get('Plot', "Plot not found")
        final_msg = "IMDB Rating: " + str(rating) + "\n" + \
                    "Plot: " + str(plot) + "\n"
        message.reply(str(final_msg))

    return make_response()

