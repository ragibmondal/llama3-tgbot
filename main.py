
from flask import Flask, render_template
from telegram_bot import run_telegram_bot

app = Flask(__name__, static_folder='templates', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    run_telegram_bot()
    app.run(host='0.0.0.0', port=8080)
