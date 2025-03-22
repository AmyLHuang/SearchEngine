from flask import Flask, render_template, request
from main import Query
import time, sys

q = Query()
docid_dict = q.getDocidUrl()

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    result = []
    if query:
        start_time = time.time()
        doc_ids = q.querySearch(query)
        for id in doc_ids:
            result.append(docid_dict[id])
        end_time = time.time()
        print(f"--- {end_time - start_time} seconds ---", file=sys.stderr)
    return render_template('search.html', query=query, result=result, docid_dict=docid_dict)


if __name__ == '__main__':
    app.run(debug=True)
