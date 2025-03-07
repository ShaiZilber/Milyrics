import json

from flask import Flask, render_template, request, redirect, jsonify, url_for
import csv
app = Flask(__name__)
words = []
song_name = ""
correct = []
singer_name = ""

@app.route("/<name>/<singer>", methods=['GET', 'POST'])
def with_artist(name, singer):
    global words, correct, song_name, singer_name
    if request.method == 'POST':
        print("post!")
        changed = "false"
        data = request.json
        input_value = data.get('input_value', '')
        if input_value in words:
            for i, word in enumerate(words):
                if word == input_value and not correct[i]:
                    correct[i] = True
                    changed = "true"
        print(changed)
        return render_template("words-part.html", song=words, correct=correct, line_length=20, singer=singer_name, song_name=song_name, changed=changed)
    else:
        singer_name = singer
        song_name = name.replace("-", " ")
        print(singer)
        with open("lyrics.csv", "r", encoding="utf8") as f:
            csvdata = csv.DictReader(f, fieldnames=['artist', 'songs', 'song', 'artist_key', 'url', 'words count',
                                                    'unique words count'])
            next(csvdata)
            for row in csvdata:
                if row['song'] == name and (singer == '!' or singer == row['artist']):
                    words = row['songs'][1:-1].replace("\'", "").replace(" ", "").split(",")
                    singer_name = row['artist']
                    break

        if correct == []:
            correct = [False] * len(words)
    return render_template("guess-page.html", song=words, correct=correct, line_length=20, singer=singer_name, changed="false", song_name=song_name, giveup=False)


@app.route("/<name>", methods=['GET'])
def index(name, singer=""):
    return redirect(f"/{name}/!")

@app.route("/give-up/", methods=['POST'])
def give():
    global words, correct

    return render_template("guess-page.html", song=words, correct=correct, line_length=20, singer=singer_name, song_name=song_name,
                           changed="false", giveup=True)
@app.route("/reset/", methods=['POST'])
def reset():
    global words, correct, song_name, singer_name
    song_name_before = song_name
    singer_name_before = singer_name
    words = []
    song_name = ""
    correct = []
    singer_name = ""
    return redirect(f"/{song_name_before}/{singer_name_before}")

@app.route("/", methods=['GET', 'POST'])
def find():
    global words, correct, song_name, singer_name
    words = []
    song_name = ""
    correct = []
    singer_name = ""
    songs = []
    singers = []
    if request.method == 'POST':
        data = request.form['query']

        with open("lyrics.csv", "r", encoding="utf8") as f:
            csvdata = csv.DictReader(f, fieldnames=['artist', 'songs', 'song', 'artist_key', 'url', 'words count',
                                                    'unique words count'])
            next(csvdata)
            for row in csvdata:
                if data in row['song']:
                    songs.append(row['song'])
                    singers.append(row['artist'])
            return render_template("index.html", songs=songs, artists=singers)
    else:
        with open("lyrics.csv", "r", encoding="utf8") as f:
            csvdata = csv.DictReader(f, fieldnames=['artist', 'songs', 'song', 'artist_key', 'url', 'words count',
                                                    'unique words count'])
            next(csvdata)
            for row in csvdata:
                songs.append(row['song'])
                singers.append(row['artist'])

        return render_template("index.html", songs=songs, artists=singers)

def main():
    s = "["
    with open("lyrics.csv", "r", encoding="utf8") as f:
        csvdata = csv.DictReader(f, fieldnames=['artist', 'songs', 'song', 'artist_key', 'url', 'words count',
                                                'unique words count'])
        next(csvdata)
        for row in csvdata:
            s += f"{json.dumps(row,ensure_ascii=False)},"
    s += "]"
    with open("lyrics.json", "w",  encoding="utf8") as f:
        f.write(s)

    print(s)
    #app.run()



if __name__ == '__main__':
    main()
