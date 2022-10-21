import pymysql
pymysql.install_as_MySQLdb()
from eventlet import monkey_patch
monkey_patch()
from flask import Flask, g
from flask.sessions import SecureCookieSessionInterface
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager, user_loaded_from_request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from threading import Lock

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI = 'mysql://root:3Zsqlpas5*@localhost/opengovf',
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
    JSON_AS_ASCII=False
)
CORS(app)
bc = Bcrypt(app)
db = SQLAlchemy(app)
lm = LoginManager(app)
io = SocketIO(app, async_mode='eventlet', cors_allowed_origins='*')
thread = None
thread_lock = Lock()

class CustomSessionInterface(SecureCookieSessionInterface):
    """Prevent creating session from API requests."""
    def save_session(self, *args, **kwargs):
        if g.get('login_via_request'):
            return
        return super(CustomSessionInterface, self).save_session(*args, **kwargs)
app.session_interface = CustomSessionInterface()
@user_loaded_from_request.connect
def user_loaded_from_request(self, user=None):
    g.login_via_request = True

from almanac_backend.routes.region import bp_region
app.register_blueprint(bp_region)

from almanac_backend.routes.user import bp_user
app.register_blueprint(bp_user)

from almanac_backend.routes.msg import bp_msg
app.register_blueprint(bp_msg)

@app.route('/test')
def test_route():
    return '''<h1>This is a test route.</h1>'''

from flask import request
from almanac_backend.models import Dataset, Index, Table
from excel_crawler import ExcelCrawler
def data_inject(tables):
    # tables = request.get_json()
    # print(tables)
    for t in tables:
        table = Table.query.get(int(t['id']))
        io.emit('inj_state', f'开始处理 %s' % table.name, namespace='/inject')
        # io.sleep(.1)
        # io.emit('inj_state', f'开始处理 %s' % t['label'], namespace='/inject')
        ec = ExcelCrawler(loc=t['loc'])
        for idxs in t['children']:
            if idxs['label'] == '列':
                c_idxs = idxs['children']
            else:
                r_idxs = idxs['children']
        io.sleep(1)
        io.emit('inj_state', '已读取所需注入指标', namespace='/inject')
        for c in c_idxs:
            for r in r_idxs:
                if ec.tb.cell_type(r['rx'], c['cx']) == 2:
                    ds = Dataset(ec.tb.cell_value(r['rx'],c['cx']))
                    db_c = Index.query.filter_by(name = c['label']).one_or_none()
                    db_r = Index.query.filter_by(name = r['label']).one_or_none()
                    ds.col_index = db_c if db_c else Index(name=c['label'])
                    io.emit('inj_state', f'已注入指标 %s' % c['label'], namespace='/inject')
                    ds.row_index = db_r if db_r else Index(name=r['label'])
                    io.emit('inj_state', f'已注入指标 %s' % r['label'], namespace='/inject')
                    ds.table = table
    db.session.commit()
    io.sleep(1)
    io.emit('inj_state', '已保存修改至数据库', namespace='/inject')
    io.emit('inj_complete', 'success', namespace='/inject')

@io.on('inject', namespace='/inject')
def hdl_inject_proc(json):
    global thread
    with thread_lock:
        if thread is None:
            thread = io.start_background_task(data_inject, json)
            thread.join()
            thread = None

@io.on('client_request', namespace='/socket_test')
def hdl_socket_test(json):
    print(json)
    print('asdfasdfadsfasdfasdfasdfasdfasdf')
    emit('server_response', {'data': 'success'})
    return 'success'