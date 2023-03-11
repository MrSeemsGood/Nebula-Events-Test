from flask import Flask, redirect, url_for, request, render_template
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from nebula3.common import *
import json

ip = '127.0.0.1'
port = 9669

config = Config()
connection_pool = ConnectionPool()

class MyApp(Flask):
   def __init__(self, name):
      super().__init__(name)
      self.surname : str = ""
      self.out = None 
      self.response = dict()

app = MyApp(__name__)

@app.route('/')
def login():
   return render_template('index.html')

@app.route('/nebula_request', methods=['POST', 'GET'])
def insertValues():
   if request.method == 'POST':
      result = dict(request.form)
   else:
      result = dict(request.args)

   result = list(result.values())
   surname = result[0]
   app.surname = surname

   if surname == '':
      print('Ошибка: ФИО не было указано.')
      return render_template('index.html')
   
   # в форме есть ФИО, подключиться к БД чтобы получить информацию
   assert connection_pool.init([(ip, port)], config)
   client = connection_pool.get_session('root', 'nebula')
   assert client is not None

   client.execute(
      'USE events;'
   )

   resp = client.execute_json(
      'MATCH (s)-[e]->() WHERE id(s) == "{}" RETURN e;'.format(app.surname)
   )

   app.response : dict = json.loads(resp)

   with open("resp.json", 'w+', encoding='utf-8') as j:
      json.dump(app.response, j, ensure_ascii=False)
      events = [d['meta'][0]['id']['dst'] for d in app.response["results"][0]["data"]]

   #connection_pool.close()
   return render_template('nebula_request.html', display=app.response, events=events)

if __name__ == '__main__':
   app.run(debug = True)