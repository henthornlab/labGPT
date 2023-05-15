from flask import Flask, request, render_template_string
import logging
import re
import stanza
import openai
import pandas as pd

app = Flask(__name__)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', datefmt='%Y/%m/%d %H:%M:%S', level=logging.INFO)

app = Flask(__name__)

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def process_question(question):

    df = pd.read_csv('UOLabData.csv')
    doc = nlp(question)
    logging.info("*** Running nlp on query. doc is broken down into")
    for sent in doc.sentences:
        for word in sent.words:
            logging.info("%s %s %s", word.text, word.upos, word.xpos)

    conceptual = True
    early_dash = False
    area = 0
    letter = ''
    instrument_type = ''
    intent = []
    for sent in doc.sentences:
        for word in sent.words:
            match word.upos:
                case 'PUNCT':
                    early_dash = True
                case 'PRON':
                    if word.text.lower() == 'what':
                        conceptual = False
                case 'NOUN':
                    if '-' in word.text:
                        instrument_type = word.text[0:3].upper()
                        area = word.text[4:7]
                        letter = word.text[7:8].upper()
                        continue
                    if has_numbers(word.text):
                        area = re.sub(r'[^0-9]', '', word.text)
                    if word.text.lower() == 'accuracy':
                        intent.append('Accuracy')
                    elif word.text.lower() == 'error':
                        intent.append('Accuracy')
                    elif word.text.lower() == 'range':
                        intent.append('Range')
                    elif word.text.lower() == 'type':
                        intent.append('Description')
                    elif 'fit' in word.text.lower():
                        instrument_type = 'FIT'
                    elif 'dpit' in word.text.lower():
                        intrument_type = 'DPIT'
                    elif 'pit' in word.text.lower():
                        instrument_type = 'PIT'
                    elif 'sit' in word.text.lower():
                        instrument_type = 'SIT'
                    elif 'te' in word.text.lower():
                        instrument_type = 'TE'
                    elif 'cit' in word.text.lower():
                        instrument_type = 'CIT'
                    elif 'p' in word.text.lower():
                        instrument_type = 'P'
                case 'PROPN':
                    if has_numbers(word.text):
                        area = re.sub(r'[^0-9]', '', word.text)
                    if 'fit' in word.text.lower():
                        instrument_type = 'FIT'
                    elif 'dpit' in word.text.lower():
                        instrument_type = 'DPIT'
                    elif 'pit' in word.text.lower():
                        instrument_type = 'PIT'
                    elif 'sit' in word.text.lower():
                        instrument_type = 'SIT'
                    elif 'te' in word.text.lower():
                        instrument_type = 'TE'
                    elif 'cit' in word.text.lower():
                        instrument_type = 'CIT'
                    elif 'p' in word.text.lower():
                        instrument_type = 'P'
                case 'ADJ':
                    if has_numbers(word.text):
                        area = re.sub(r'[^0-9]', '', word.text.lower())
                    if 'fit' in word.text.lower():
                        instrument_type = 'FIT'
                    elif 'dpit' in word.text.lower():
                        intrument_type = 'DPIT'
                    elif 'pit' in word.text.lower():
                        instrument_type = 'PIT'
                    elif 'sit' in word.text.lower():
                        instrument_type = 'SIT'
                    elif 'te' in word.text.lower():
                        instrument_type = 'TE'
                    elif 'cit' in word.text.lower():
                        instrument_type = 'CIT'
                    elif 'p' in word.text.lower():
                        instrument_type = 'P'
                case 'VERB':
                    if word.text.lower() == 'tell':
                        conceptual = False
                case 'NUM':
                    string = ''
                    for character in word.text:
                        if character.isnumeric():
                            string += character
                        else:
                            if character != '-':
                                if has_numbers(string):
                                    letter += character.upper()
                                else:
                                    instrument_type += character
                            else:
                                area = string
                                string = '-'
                    if area == 0:
                        area = int(string)
                    else:
                        letter = string
                case 'SYM':
                    strings = word.text.split("-")
                    for string in strings:
                        if string == '':
                            continue
                        elif area == 0:
                            area = int(string)
                        else:
                            letter = string.upper()
    if area == 0 or letter == '' or intent == []:
        if area != 0 and letter != '' and conceptual == False:
            intent = ['Description', 'Range', 'Accuracy']
        else:
            conceptual = True
    logging.info("Conceptual is: %s", str(conceptual))
    logging.info("Instrument type is: %s", instrument_type)
    logging.info("Area code is: %s", str(area))
    logging.info('Instrument letter is: %s',  letter)
    logging.info('Intents are: %s',  str(intent))

    gpt_answer = ''
    answer = ''
    if not conceptual:
        if early_dash:
            tag = instrument_type + '-' + str(area) + letter
        else:
            tag = instrument_type + str(area) + '-' + letter
        temp = df.query("Instrument == '" + tag + "'")
        intent.insert(0, 'Instrument')
        answer = temp[intent]
        intent = intent.remove('Instrument')
    else:
        openai.api_key = "your_key_here"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": question}
            ]
        )

        gpt_answer = response.choices[0].message.content

    logging.info("*** ANSWERS ***")
    if not conceptual:
        logging.info("answer is %s", answer)
        return answer.to_html()
    else:
        logging.info("gpt_answer is %s", gpt_answer)
        type(answer)
        return gpt_answer


def create_response():
    return '''
        <!DOCTYPE html>
        <html>
          <head><title>LabGPT</title></head>
          <body>
            <br><img src="static/rhit-logo-wide.png" RHIT Logo">
            <h1>Welcome to LabGPT</h1>
            <h3>Enter your query below</h3>
            <h3> Try something like: What is the accuracy of FIT-400A? </h3>
            <form action="/query" method="post">
        
            <label for="query">Query:</label>
            <input type="text" id="query" size="60" name="query"><br><br>
            <input type="submit" value="Query"></input>
            </form> 

            <br><br>     
          </body>
        </html>'''

@app.route('/', methods=["GET"])
def home():

    logging.info("New request for / from %s", request.remote_addr)

    template = create_response()
    return render_template_string(template)

@app.route('/query', methods=["POST"])
def query():
    query = request.form['query']
    logging.info("Post on / from %s with query: %s", request.remote_addr, query)
    if len(query) == 0:
        return '''<!DOCTYPE html><html>
          <body>
            <h3>Empty request</h3> 
          </body>
        </html>'''
    else:
        answer = process_question(query)

        return '''<!DOCTYPE html>
            <html>
                <head><title>LabGPT</title></head>
                <body>
                <br><img src="static/rhit-logo-wide.png" RHIT Logo">
                <h1>LabGPT</h1>''' + answer + '''
                <br><br>
                <a href="/">New query</a>     
                </body>
            </html>'''


if __name__ == '__main__':
    logging.info("Starting")
    logging.info("Downloading English model for stanza")
    stanza.download('en')  # download English model
    nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos');  # initialize English neural pipeline

    app.run(host="0.0.0.0", port=3000)


