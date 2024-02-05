from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import re
import nltk
import heapq

app = Flask(__name__, static_folder='static')



nltk.download('stopwords')
nltk.download('punkt')

@app.route('/')
def index():
    return render_template('index.html', summary=None)

@app.route('/summarize', methods=['POST'])
def summarize():
    article_link = request.form['articleLink']
    article_text = get_article_content(article_link)

    if article_text:
        clean_text = re.sub('[^a-zA-Z]', ' ', article_text.lower())
        clean_text = re.sub('\s+', ' ', clean_text)
        sentence_list = nltk.sent_tokenize(article_text)

        stopwords = nltk.corpus.stopwords.words('english')
        word_frequencies = {}
        for word in nltk.word_tokenize(clean_text):
            if word not in stopwords:
                if word not in word_frequencies:
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1

        maximum_frequency = max(word_frequencies.values())
        for word in word_frequencies:
            word_frequencies[word] = word_frequencies[word] / maximum_frequency

        sentence_scores = {}
        for sentence in sentence_list:
            for word in nltk.word_tokenize(sentence):
                if word in word_frequencies and len(sentence.split(' ')) < 30:
                    if sentence not in sentence_scores:
                        sentence_scores[sentence] = word_frequencies[word]
                    else:
                        sentence_scores[sentence] += word_frequencies[word]

        summary = heapq.nlargest(5, sentence_scores, key=sentence_scores.get)
        summary_text = " ".join(summary)
        return render_template('index.html', summary=summary_text)

    return render_template('index.html', summary=None)

def get_article_content(article_link):
    try:
        response = requests.get(article_link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            article_content = soup.get_text()
            return article_content
        else:
            print(f"Error: Unable to fetch content. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)
