from flask import Flask, render_template, request
from search import Search
import time, sys

s = Search()
docid_dict = s.getDocidUrl()

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
        s.search(query)
        doc_ids = s.getResults()
        for id in doc_ids:
            result.append(docid_dict[str(id)])
        end_time = time.time()
        print(f"--- {end_time - start_time} seconds ---", file=sys.stderr)
    return render_template('search.html', query=query, result=result, docid_dict=docid_dict)


if __name__ == '__main__':
    app.run(debug=True)
