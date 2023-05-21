import json
from flask import Flask, request, render_template, session
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config

IP = '127.0.0.1'
PORT = 9669

config = Config()
connection_pool = ConnectionPool()

app = Flask(__name__)

@app.route('/')
def login():
    session.clear()
    return render_template('index.html')

@app.route('/nebula_request', methods=['POST', 'GET'])
def insert_values():
    if request.method == 'POST':
        result = dict(request.form)
    else:
        result = dict(request.args)

    session['surname'] = list(result.values())[0]

    if session['surname'] == '':
        print('Ошибка: ФИО не было указано.')
        return render_template('index.html')

    assert connection_pool.init([(IP, PORT)], config)
    client = connection_pool.get_session('root', 'nebula')
    assert client is not None

    client.execute(
        'USE events;'
    )

    resp = client.execute_json(
        'MATCH (s)-[e]->() WHERE id(s) == "{}" RETURN e;'.format(session['surname'])
    )

    session['response']:dict = json.loads(resp)

    with open("resp.json", 'w+', encoding='utf-8') as j:
        json.dump(session['response'], j, ensure_ascii=False)
        events = [d['meta'][0]['id']['dst'] for d in session['response']["results"][0]["data"]]

    return render_template('nebula_request.html', display=session['response'], events=events)

if __name__ == '__main__':
    app.run(debug = True)
