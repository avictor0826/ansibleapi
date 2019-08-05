from flask import (
    Flask,
    render_template,
    request,
    make_response,
    jsonify

)
from ansible_runner.runner import AnsibleRunner

from functools import wraps
import pprint,datetime
import json
#import jwt

app = Flask(__name__, template_folder="templates")
app.config['KEY'] = 'hastlavistababy'

'''
def jwt_token(f):
    @wraps(f)
    def check_authorization(*args, **kwargs):
        key = request.headers.get('X-Auth-Ansibleapi')
        if key is None:
            return make_response(jsonify({ "status": "error","message":"Auth failed"}), 401)
        try:
            d = jwt.decode(key, app.config['KEY'], algorithms=['HS256'])
            #print("d=",d.get('user').encode('ascii'))
            if d.get('user').encode('ascii') == 'ansiblekongapi':
                return f()
            else:
                return make_response(jsonify({ "status": "error","message":"Auth failed"}), 401)
        except Exception as e:
            print(e)
            return make_response(jsonify({ "status": "error","message":"Auth failed"}), 401)
    return check_authorization

'''
@app.route('/play/', methods=['POST'])
def playbook_execute():
    res = {}
    #print(request.is_json)
    if not request.is_json:
        return make_response(jsonify({ "status": "error","message":"not a json input"}), 400)

    try:
        inp = request.get_json()
        playbook=inp.get('playbook')
        extra_vars=inp.get('extra_vars')
        hostlist=inp.get('hostlist')
        inventory=inp.get('inventory')
        #req = Request(rc)
        '''
        print("Playbook : "+ playbook)
        print("Hostlist:",hostlist)
        print("Inventory: ",inventory)
        '''
        print("extra_args: ",type(json.loads(extra_vars)))
        ar = AnsibleRunner(playbook,hostnames=hostlist,inventory=inventory,extra_vars=json.loads(extra_vars))
        #print("Runner initialized ")
        suc = ar.run()
        print("Runner completed ")
        outp=ar.output()
        if suc and len(outp) > 0:
            res['status']= "success"
            res['output'] = outp
            return make_response(jsonify(res), 200)
        else:
            res['status']= "failed"
            res['output'] = outp
            if len(outp) == 0:
                res['output'] = {"message":"No hosts found or not a proper inventory file"}
            return make_response(jsonify(res), 400)
    except Exception as e:
        print(e)
        res['status'] = 'error'
        res['message'] = str(e)
        return make_response(jsonify(res), 500)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port='7000')
