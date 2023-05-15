from flask import Flask, request, render_template_string
import logging

app = Flask(__name__)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', datefmt='%Y/%m/%d %H:%M:%S', level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def home():

    logging.info("New request for / from %s", request.remote_addr)

    template = create_response()
    return render_template_string(template)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)

def create_response():
    return '''
        <!DOCTYPE html>
        <html>
          <head><title>LabGPT</title></head>
          <body>
            <br><img src="static/rhit-logo-wide.png" RHIT Logo">
            <h1>Welcome to LabGPT</h1>
            <h3>Enter your question below</h3 

            <br><br>     
          </body>
        </html>'''
