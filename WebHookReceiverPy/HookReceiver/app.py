import sys
from flask import Flask, request, abort

app = Flask(__name__)

@app.route('/', methods=['POST'])
def welcome():
    return 'A simple webhook listener!'

@app.route('/webhook', methods=['POST'])
def webhook():
    print("\n\nReceived WebHook Notification from Orchestrator:")
    sys.stdout.flush()
    if request.method == 'POST':
        print(request.json)
        return '',200
    else:
        abort(400)
if __name__ == '__main__':
    app.run(debug=True)