import shutil, os, zipfile, time
from flask import request, jsonify, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from almanac_backend import bc, db, lm
from almanac_backend.models import Bundle, Dataset, Index, Region, Table, User
from excel_crawler import ExcelCrawler
from datetime import datetime
import random

bp_user = Blueprint('user', __name__, url_prefix='/user')

@lm.request_loader
def load_user_from_request(request):
    user_id = request.headers.get('Authorization')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return user
    return None

@bp_user.route('/', methods=['GET'])
@login_required
def user_profile():
    rname = current_user.regions[0].name
    uni_cnt, size, f_cnt, upl_cnt = 0, 0, 0, 0
    for r, d, f in os.walk('.\\统计年鉴\\'+rname):
        size += sum([os.path.getsize(os.path.join(r, name)) for name in f])
        f_cnt += len(f)
    while size/1024 > 1:
        size /= 1024
        uni_cnt += 1
    upl_cnt = len([reg for reg in current_user.regions if reg.name == rname])
    return jsonify(dict(
        uni_cnt=uni_cnt,
        size=size,
        f_cnt=f_cnt,
        upl_cnt=upl_cnt-1
    ))

@bp_user.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        json = request.get_json()
        user = User.query.filter(User.username==json['account']).one_or_none()
        if user is None:
            return jsonify({'msg':'服务器找不到用户，因为我是个泡泡茶壶'})
        elif bc.check_password_hash(user.password, json['pass']):
            login_user(user)
            return jsonify({'user_id':user.id,'level': user.level})
        else:
            return jsonify({'msg':'你密码不对，因为你是个泡泡茶壶'}), 401

@bp_user.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'msg':'再见，你个泡泡茶壶'})

@bp_user.route('/upload', methods=['POST'])
@login_required
def data_upload():
    f = request.files.get('file')
    oregion = current_user.regions[0]
    rname = oregion.name
    new_region = Region(name=rname)
    current_user.regions.append(new_region)
    db.session.add(new_region)
    db.session.commit()
    rpath = '.\\统计年鉴\\' + rname + '\\' + new_region.create_at.strftime('%F %H%M%S')
    zip_file = '.\\统计年鉴\\' + f.filename
    f.save(zip_file)
    with zipfile.ZipFile(zip_file) as zp:
        zp.extractall(rpath)
    os.remove(zip_file)
    excel_files = list()
    for r, d, f in os.walk(rpath):
        for file in f:
            if '.xls' in file:
                excel_files.append(os.path.join(r, file))
    res = list()
    node = dict(id=int(), label=str())
    for file in excel_files:
        try:
            ec = ExcelCrawler(loc=file)
        except Exception as e:
            print(e)
            os.remove(file)
        else:
            htap = file[::-1].split('\\', 1)
            htap[0] = ('\\'+ec.table_name+'.xls')[::-1]
            path = ''.join(htap)[::-1]
            os.rename(file, path)
            table = Table(name=ec.table_name)
            new_region.tables.append(table)
            db.session.commit()
            # res[table.name] = dict(
            #     列=dict([(cx[0], ec.colnames[cx[0]]) for cx in list(ec.colnames)]),
            #     行=dict([(rx, ec.rownames[rx]) for rx in list(ec.rownames)])
            # )
            res.append(dict(
                id=table.id,
                label=table.name,
                loc=path,
                children=[
                    dict(
                        id=f'%d-0' % table.id,
                        label='列',
                        children=[dict(
                            id=f'%d-0-%d' % (table.id, ck[0]),
                            label=cv,
                            cx=ck[0]
                        ) for ck,cv in ec.colnames.items()]
                    ),
                    dict(
                        id=f'%d-1' % table.id,
                        label='行',
                        children=[dict(
                            id=f'%d-1-%d' % (table.id, rk),
                            label=rv,
                            rx=rk
                        ) for rk,rv in ec.rownames.items()]
                    )
                ]
            ))
    return jsonify({'data': res, 'region_id': new_region.id})

@bp_user.route('/inject', methods=['POST'])
@login_required
def user_prefered_diagram():
    diagrams = request.get_json()
    bundle = Bundle(
        column = diagrams['column'],
        line = diagrams['line'],
        radar = diagrams['radar'],
        pie = diagrams['pie'],
        region = Table.query.get(int(diagrams['line'])).region
    )
    db.session.add(bundle)
    db.session.commit()

    return jsonify({'msg': 'success'})

@bp_user.route('/register', methods=['POST'])
@login_required
def user_register():
    user_info = request.get_json()
    user = User(
        username=user_info['username'],
        password=bc.generate_password_hash(user_info['password'])
    )
    user.regions.append(Region.query.get(int(user_info['region_id'])))
    db.session.add(user)
    db.session.commit()

    return jsonify({'msg': 'success'})
    

# @bp_user.route('/task_status/<id>')
# @login_required
# def task_status(id):
#     task = task_data_inject.AsyncResult(id)
#     if task.state == 'PENDING':
#         response = {
#             'current': 0,
#             'total': 1,
#             'status': 'Pending...'
#         }
#     elif task.state != 'FAILURE':
#         response = {
#             'current': task.info.get('current', 0),
#             'total': task.info.get('total', 1),
#             'status': task.info.get('status', '')
#         }
#     else:
#         response = {
#             'state': task.state,
#             'current': 1,
#             'total': 1,
#             'status': str(task.info),
#         }
#         task.get()
#     return jsonify(response)
