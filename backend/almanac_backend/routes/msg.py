from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from almanac_backend import db
from almanac_backend.models import Msg, Region, User
from datetime import datetime

bp_msg = Blueprint('msg', __name__, url_prefix='/msg')

@bp_msg.route('/<int:id>/approve')
@login_required
def msg_dealing(id):
    msg = Msg.query.get(id)
    if current_user.level == 1:
        user = User.query.get(msg.user_id)
        region = Region.query.get(msg.region_id)
        user.regions.append(region)
        msg.state = 1
        db.session.commit()
    else:
        return jsonify({'msg': 'failed'}), 400
    
    return jsonify({'msg':'success'})

@bp_msg.route('/')
@login_required
def get_all_msg():
    if current_user.level == 1:
        msgs = Msg.query.filter_by(state=0).all()
        res = [dict(
            id=msg.id,
            ori_rgn = User.query.get(msg.user_id).regions[0].name,
            tgt_rgn = Region.query.get(msg.region_id).name,
            create_at = msg.create_at.strftime('%F'),
            message = msg.msg,
        ) for msg in msgs]
    else:
        msgs = Msg.query.filter_by(user_id = current_user.id).all()
        res = [dict(
            tgt_rgn = Region.query.get(msg.region_id).name,
            create_at = msg.create_at.strftime('%F'),
            message = msg.msg,
            state = msg.state
        ) for msg in msgs]
    
    return jsonify(res)

@bp_msg.route('/apply', methods=['POST'])
@login_required
def msg_apply():
    apl = request.get_json()
    msg = Msg(
        rid=apl['region_id'],
        uid=current_user.id,
        msg=apl['msg']
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({'msg': 'success'})