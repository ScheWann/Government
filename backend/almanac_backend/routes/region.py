from flask import jsonify, request, Blueprint
from flask_login import login_required, current_user
from almanac_backend import db
from almanac_backend.models import Dataset, Index, Region, Table, User

bp_region = Blueprint('region', __name__, url_prefix='/regions')

@bp_region.route('/', methods=['GET'])
@login_required
def get_regions():
    regions = Region.query.all()
    res = [dict(
        create_at=region.create_at.strftime('%F'),
        amount=len(region.tables),
    ) for region in regions if region.name == current_user.regions[0].name]
    return jsonify(res)

@bp_region.route('/for_admin')
@login_required
def get_regions_for_admin():
    regions = Region.query.all()
    res = [dict(
        id=region.id,
        name=region.name,
        create_at=region.create_at.strftime('%F'),
        amount=len(region.tables),
    ) for region in regions if len(region.tables)>0]
    return jsonify(res)

@bp_region.route('/newest_regions')
def get_newest_regions():
    users = User.query.filter_by(level=0).all()
    newest_regions = list()
    for user in users:
        if len(user.regions)>1:
            ori_region = user.regions[0].name
            for region in user.regions[::-1]:
                if region.name == ori_region:
                    newest_regions.append(dict(
                        region_id=region.id,
                        region_name=ori_region
                    ))
                break
    
    return jsonify(newest_regions)

@bp_region.route('/mini', methods=['GET'])
@login_required
def get_mini_regions():
    regions = current_user.regions[1:]
    res = []
    for reg in regions:
        d = {}
        d['region_id'] = reg.id
        d['name'] = reg.name
        d['create_at'] = reg.create_at.strftime('%F')
        d['amount'] = len(reg.tables)
        res.append(d)
    return jsonify(res)

@bp_region.route('/choice/<usage>')
def get_region_for_choice(usage):
    if usage == 'compare':
        regions = current_user.regions
    if usage == 'apply':
        regions = [region for region in Region.query.all() if region not in current_user.regions]
    if usage == 'register':
        print('register')
        regions = [region for region in Region.query.all()]
    res = [dict(
        region_id=region.id,
        choice = region.name+region.create_at.strftime('%F')
    ) for region in regions]

    return jsonify(res)

@bp_region.route('/<int:id>/tables')
@login_required
def get_tables_by_region(id):
    tables = Region.query.get(id).tables
    res = []
    for t in tables:
        d = {}
        d['table_id'] = t.id
        d['name'] = t.name
        res.append(d)
    return jsonify(res)

@bp_region.route('/<int:id>/smr/<type>')
def get_region_sum(id, type):
    tables = Region.query.get(int(id)).bundle[0]
    # 折线图
    if type == 'line':
        line_table = Table.query.get(tables.line)

        return jsonify({'line': {
            'data': [float(d.data) for d in line_table.datas],
            'index': [d.row_index.name for d in line_table.datas]
        }, 'table_name':line_table.name})
    # 饼状图
    if type == 'pie':
        pie_table = Table.query.get(tables.pie)

        return jsonify({'pie': [dict(
            value = float(d.data),
            name = d.row_index.name
        ) for d in pie_table.datas], 'table_name': pie_table.name})
    # 柱状图
    if type == 'column':
        col_table = Table.query.get(tables.column)
        col_list = list()
        col_row_names = list(set([data.row_index.name for data in col_table.datas]))
        col_col_names = list(set([data.col_index.name for data in col_table.datas]))
        for rn in col_row_names:
            d = dict()
            d['product']=rn
            col_row_datas = [data for data in col_table.datas if data.row_index.name == rn]
            for data in col_row_datas:
                d[data.col_index.name]=float(data.data)
            col_list.append(d)
        return jsonify({'column': col_list, 'table_name': col_table.name})
    # 雷达图
    if type == 'radar':
        rad_table = Table.query.get(tables.radar)
        rad_row_idxes, rad_col_idxes = list(), list()
        for d in rad_table.datas:
            if d.row_index.name not in rad_row_idxes:
                rad_row_idxes.append(d.row_index.name)
            if d.col_index.name not in rad_col_idxes:
                rad_col_idxes.append(d.col_index.name)
        rad_datas = {
            'data': [{
                'name': cx,
                'value':[0 for _ in rad_row_idxes]
            } for cx in rad_col_idxes],
            'indicator': list()
        }
        for d in rad_table.datas:
            for di in rad_datas['data']:
                if d.col_index.name == di['name']:
                    di['value'][rad_row_idxes.index(d.row_index.name)] = float(d.data)
        for rx in rad_row_idxes:
            ds = list()
            for di in rad_datas['data']:
                ds.append(di['value'][rad_row_idxes.index(rx)])
            rad_datas['indicator'].append({
                'name': rx,
                'max': round(max(ds))+1
            })
        return jsonify({'radar': rad_datas, 'table_name': rad_table.name})

    return jsonify({'msg': '非法类型'})