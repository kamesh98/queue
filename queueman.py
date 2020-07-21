from flask import Flask, request, jsonify
import traceback
from flask_cors import CORS
import smtplib
from hashlib import sha256
from geopy.geocoders import Nominatim
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from lib import db_ops
app = Flask(__name__)
CORS(app)

def get_email_content(link):
    return f'''
        <div style="background-color:#fff;margin:0 auto 0 auto;padding:30px 0 30px 0;color:#4f565d;font-size:13px;line-height:20px;font-family:'Helvetica Neue',Arial,sans-serif;text-align:left">
            <center>
            <table style="width:550px;text-align:center">
                <tbody><tr>
                    <td style="padding:0 0 20px 0;border-bottom:1px solid #e9edee; text-align:left; ">
                        <h2 style="font-family: trebuchet ms,sans-serif;">
                            Greetings! 
                        </h2>
                        <div style="font-size: larger;">
                            Thank you for your Interest to Open an Account with us.                
                        </div>
                        <br>
                        <div style="margin-block-end: 0; font-size: larger;">
                            Please read the instructions carefully before you start your application.    
                        </div>
                    </td>
                </tr>
                <tr>
                    <td colspan="2" style="padding-bottom:10px; border-bottom:1px solid #e9edee; ">               
                        </span>
                            <p style="margin:20 10px 10px 10px;padding:0">
                                <span style="font-family: trebuchet ms,sans-serif; color: #4f565d; font-size: 15px; line-height: 20px;">
                                    Below is the link to start your Video KYC
                                </span>
                            </p>
                        <span>
                            <p>
                                <a style="display:inline-block;text-decoration:none;padding:15px 20px;background-color:#048c88;border:1px solid #048c88;border-radius:3px;color:#fff;font-weight:bold; font-size: medium" href="{link}" target="_blank" >
                                    Start Video KYC
                                </a>
                            </p>
                        </span>
                        
                    </td>
                </tr>
                <tr>
                    <td style="padding-bottom: 20px; text-align:left;">
                        <h3 style="margin-block-end: 0px;">Important Instructions</h3>
                        <div style="display: flex; justify-content: center; font-size: 15px;">
                            <ol style="text-align: left; color: #575757;">
                                <li style="padding: 0px 0px 3px 5px;">
                                    Please keep your Aadhaar XML and Pan Card Ready.
                                </li> 
                                <li style="padding: 0px 0px 3px 5px;">
                                    Please be in a well lit room/area. 
                                </li> 
                                <li style="padding: 0px 0px 3px 5px;">
                                    Please be in a place with less/no noise.
                                </li> 
                                <li style="padding: 0px 0px 3px 5px;">
                                    Follow the instructions of Customer Executive Carefully
                                </li>
                            </ol>
                        </div>
                        <p style="margin-block-start: 0px; font-size: larger;">
                            Thank you for your time. Have a nice day! 
                        </p>

                    </td>
                </tr>
                <tr>
                    <td colspan="2" style="padding:30px 0 0 0;border-top:1px solid #e9edee;color:#9b9fa5">
                        If you have any questions you can get in touch at <a style="color:#666d74;text-decoration:none" href="mailto:explore@in-d.ai" target="_blank">explore@in-d.ai</a>
                    </td>
                </tr>
            </tbody></table>
            </center>
        </div></div>'''

def mailing(agent_id, email, token, user_id):
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.ehlo()
    s.starttls() 
    s.ehlo()
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Thank you for your interest in VideoKYC'
    msg['From'] = "aitest@intainft.com"
    msg['To'] = email
    body = "https://video.kyc.in-d.ai/user/?room-id={agent_id1}&token={token}&user_id={user}".format(agent_id1=agent_id, token=token, user=user_id)
    body = get_email_content(body)
    body = MIMEText(body,'html')
    msg.attach(body) 
    s.sendmail("aitest@intainft.com", email, msg.as_string()) 
    s.quit() 

def check_null(*args):
    for i in args:
        if not i:
            return False
    return True

def find_address(loaction):
    flag = False
    geolocator = Nominatim(user_agent="VideoKyc")
    address = geolocator.reverse(loaction).address
    if 'INDIA' in address.upper():
        flag = True
    return address, flag

@app.route('/queue/addagent',methods=['POST'])
def addagent():
    try:
        agent_id = request.form['agent_id']
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        company = request.form['company']
        phone = request.form['phone']
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207
    
    try:
        check = check_null(agent_id, name, password, email, company, phone)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'One of the input were null'
            }), 207 
        #password = sha256(password.encode('utf-8')).hexdigest()
        flag, text = db_ops.add_agent(name, agent_id, password, email, company=company, phone=phone, availabilty='A')
        if flag:
            return jsonify({
                    'status': 'success',
                    'flag': 'A',
                    'desc': text
                }), 201
        else:
            return jsonify({
                    'status': 'fail',
                    'flag': 'F',
                    'desc': text
                }), 207
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207

@app.route('/queue/loginpass',methods=['POST'])
def loginpass():

    try:
        email = request.form['email']
        password = request.form['password']
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207
    
    try:
        check = check_null(email,password)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'One of the input were null'
            }), 207 
        #password = sha256(password.encode('utf-8')).hexdigest()
        flg, agent_id = db_ops.get_id_byemail(email)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Colud not fetch agent_id by email'
            }), 207 
        flag, token = db_ops.login_password(agent_id, password, email)
        if flag:
            return jsonify({
                'status': 'success',
                'flag': 'A',
                'desc': flag,
                'token': token,
                'agent_id': agent_id
                }), 200
        else:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': token           
            }),403
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207  

@app.route('/queue/forceexit',methods=['POST'])
def force_exit():
    try:
        agent_id = request.form['agent_id']
        user_id = request.form['user_id']
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207
    
    try:
        check = check_null(agent_id,user_id)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'One of the input were null'
            }), 207 
        
        flag, data = db_ops.force_exit(agent_id,user_id)
        if flag:
            if isinstance(data,dict):
                
                mailflag = True
                try:
                    mailing(data['agent_id'], data['email'], data['key'], data['user_id'])
                    data.pop('key')
                except:
                    print(traceback.print_exc())
                    mailflag = False
                
                return jsonify({
                    'status': 'success',
                    'flag': 'C',
                    'desc': data,
                    'mail': mailflag
                }), 200
            else:
                return jsonify({
                    'status': 'success',
                    'flag': 'A',
                    'desc': data
                }), 201
        
        else:
            return jsonify({
                    'status': 'fail',
                    'flag': 'F',
                    'desc': data
                }), 207

    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207

@app.route('/queue/agentlogin', methods=['POST'])
def agent_login():
    
    try:
        agent_id = request.form['agent_id']
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207
    
    try:
        check = check_null(agent_id)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'One of the input were null'
            }), 207 

        flag, data = db_ops.agent_login(agent_id)
        if flag:
            if isinstance(data,dict):
                
                mailflag = True
                try:
                    mailing(data['agent_id'], data['email'], data['key'], data['user_id'])
                    data.pop('key')
                except:
                    print(traceback.print_exc())
                    mailflag = False

                return jsonify({
                    'status': 'success',
                    'flag': 'C',
                    'desc': data,
                    'mail': mailflag
                }), 200
            else:
                return jsonify({
                    'status': 'success',
                    'flag': 'A',
                    'desc': data
                }), 201
        
        else:
            return jsonify({
                    'status': 'fail',
                    'flag': 'F',
                    'desc': data
                }), 207

    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207        

@app.route('/queue/agentlogout', methods=['POST'])
def agent_logout():

    try:
        agent_id = request.form['agent_id']
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207

    try:
        check = check_null(agent_id)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'One of the input were null'
            }), 207 
        flag, text = db_ops.agent_logout(agent_id)
        if flag:
            return jsonify({
                    'status': 'success',
                    'flag': 'A',
                    'desc': text
                }), 200
        else:
            return jsonify({
                    'status': 'fail',
                    'flag': 'F',
                    'desc': text
                }), 207
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207

@app.route('/queue/adduser', methods=['POST'])     
def adduser():
    try:
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        company = request.form['company']
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207
    
    try:
        check = check_null(name, email, phone, company)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'One of the input were null'
            }), 207 
        print('Data:', name,email,phone)
        flag, data = db_ops.add_user(phone, email, name, company=company)
        if flag:
            if isinstance(data,dict):
                mailflag = True
                try:
                    mailing(data['agent_id'], data['email'], data['key'], data['user_id'])
                    data.pop('key')
                except:
                    print(traceback.print_exc())
                    mailflag = False

                return jsonify({
                    'status': 'success',
                    'flag': 'C',
                    'desc': data,
                    'mail': mailflag
                }), 200
            else:
                return jsonify({
                    'status': 'success',
                    'flag': 'A',
                    'desc': data
                }), 201
        
        else:
            return jsonify({
                    'status': 'fail',
                    'flag': 'F',
                    'desc': data
                }), 207

    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207        

@app.route('/queue/finish', methods=['POST'])
def finish():
    try:
        agent_id = request.form['agent_id']
        user_id = request.form['user_id']
        uid = request.form['uid']
        geo = request.form['geo']
        liveness = request.form['liveness']
        validation = request.form['validation']
        face = request.form['face']
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207
    
    try:
        check = check_null(agent_id,user_id)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'One of the input were null'
            }), 207 
        flag, data = db_ops.finish(agent_id,user_id, uid, geo, liveness, validation, face)
        if flag:
            if isinstance(data,dict):
                mailflag = True
                try:
                    mailing(data['agent_id'], data['email'], data['key'], data['user_id'])
                    data.pop('key')
                except:
                    print(traceback.print_exc())
                    mailflag = False

                return jsonify({
                    'status': 'success',
                    'flag': 'C',
                    'desc': data,
                    'mail': mailflag
                }), 200
            else:
                return jsonify({
                    'status': 'success',
                    'flag': 'A',
                    'desc': data
                }), 201
        
        else:
            return jsonify({
                    'status': 'fail',
                    'flag': 'F',
                    'desc': data
                }), 207

    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207

@app.route('/queue/finishlogout', methods=['POST'])
def finish_exit():
    try:
        agent_id = request.form['agent_id']
        user_id = request.form['user_id']
        uid = request.form['uid']
        geo = request.form['geo']
        liveness = request.form['liveness']
        validation = request.form['validation']
        face = request.form['face']
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207
    
    try:
        check = check_null(agent_id,user_id)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'One of the input were null'
            }), 207 
        
        flag, text = db_ops.finish_exit(agent_id,user_id, uid, geo, liveness, validation, face)
        if flag:
            return jsonify({
                    'status': 'success',
                    'flag': 'A',
                    'desc': text
                }), 200
        else:
            return jsonify({
                    'status': 'fail',
                    'flag': 'F',
                    'desc': text
                }), 207
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207

@app.route('/queue/getuserbatch', methods=['POST'])
def fetch_user_agentid():
    try:
        agent_id = request.form['agent_id']
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207
    
    try:
        check = check_null(agent_id)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'One of the input were null'
            }), 207 

        data = db_ops.extract_user_data(agent_id)
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207

    return jsonify({
            'status': 'success',
            'flag': 'A',
            'desc': data
    }), 200

@app.route('/queue/updatelink', methods=['POST'])
def updatelink():
    try:
        user_id = request.form['user_id']
        link = request.form['link']
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207

    try:
        check = check_null(user_id,link)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'One of the input were null'
            }), 207 

        flag, text = db_ops.insert_link(user_id,link)
        if flag:
            return jsonify({
                    'status': 'success',
                    'flag': 'A',
                    'desc': text
                }), 201
        else:
            return jsonify({
                    'status': 'fail',
                    'flag': 'F',
                    'desc': text
                }), 207
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207         

@app.route('/queue/search', methods=['POST'])
def search():
    try:
        agent_id = request.form['agent_id']
        search_id = request.form['search_id']
        search_text = request.form['search_text']
        end_date = request.form.get('end_date', False)
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207
    
    try:
        check = check_null(search_id, search_text)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'One of the input were null'
            }), 207 

        data = db_ops.search(agent_id, search_id, search_text, end_date)
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207

    return jsonify({
            'status': 'success',
            'flag': 'A',
            'desc': data
    }), 200

@app.route('/queue/loaction', methods=['POST'])
def loaction():
    try:
        loaction = request.form['loaction']
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Could not fetch loaction'
            }), 207
    
    try:
        check = check_null(loaction)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'One of the input were null'
            }), 207 
        try:
            address, flag = find_address(loaction)
        except:
            print(traceback.print_exc())
            address = None
            flag = False
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207

    return jsonify({
            'status': 'success',
            'flag': flag,
            'result': address
    }),200    

@app.route('/queue/dropcall',methods=['POST'])
def dropcall():
    try:
        agent_id = request.form['agent_id']
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207
    
    try:
        check = check_null(agent_id)
        if not check:
            return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'One of the input were null'
            }), 207 
        flag, text = db_ops.drop_call(agent_id)
        if flag:
            return jsonify({
                    'status': 'success',
                    'flag': 'A',
                    'desc': text
                }), 200
        else:
            return jsonify({
                    'status': 'fail',
                    'flag': 'F',
                    'desc': text
                }), 207
    except:
        print(traceback.print_exc())
        return jsonify({
                'status': 'fail',
                'flag': 'F',
                'desc': 'Failed'
            }), 207
