from flask import Flask, render_template, request
from search import Search

app = Flask(__name__)

s = Search()
doc_id_to_url = s.getDocIdToUrl()

@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    result = []
    if query:
        s.search(query)
        doc_ids = s.getResults()
        for id in doc_ids:
            result.append(doc_id_to_url[str(id)])
    return render_template('search.html', query=query, result=result)

if __name__ == '__main__':
    app.run(debug=True)
