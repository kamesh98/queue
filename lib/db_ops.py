from sqlalchemy.orm import sessionmaker
import traceback
from sqlalchemy import create_engine, MetaData
from models.cous_exc import Agent, AgentQueue, User, UserQueue
from uuid import uuid4
import json
import requests

agentid_token_mapper = {}

def indone_registration(email, password, name, last_name, phone):
    header = {'Content-Type': 'application/json'}
    url = 'https://one.in-d.ai/api/users/direct/'
    data = {
        'email': email,
        'password': password,
        'first_name': name,
        'last_name': last_name,
        'phone': phone
    }
    response = requests.post(url,data=json.dumps(data),headers=header)
    print(response.content, response.status_code)
    if response.status_code == 201:
        return True, True, 'User Added in In-d one'
    else:
        response_json = response.json()
        response_json_email = response_json.get('email', 'None')
        response_json_phone = response_json.get('phone', 'None')
        if "exists" in response_json_email[0]:
            return False, True, 'Email has been registerd already in in-d one'
        elif "exists" in response_json_phone[0]:
            return False, False,'Phone number is already present please use a diifrent phone number'
        return False, False, 'Failed'

def indone_agent_token_generation(email, password, agent_id, channel='WB'):
    global agentid_token_mapper
    print(agent_id)
    header = {'Content-Type': 'application/json'}
    url =  'https://one.in-d.ai/api/users/token/'
    data = {
        'email': email,
        'password': password,
        'channel': "WEB"
    }
    response = requests.post(url, data=json.dumps(data), headers=header).json()
    token = response.get('access', False)
    print(token)
    if token:
        agentid_token_mapper[agent_id] = token
        print(agentid_token_mapper)
        return token
    else:
        return False

def indone_api_key_creation(agent_id, name, expiry=0.02):
    global agentid_token_mapper
    #print(agentid_token_mapper)
    print(agent_id)
    token = agentid_token_mapper[agent_id]
    token = 'Bearer ' + token
    header = {'Content-Type': 'application/json', 'Authorization': token}
    data = {
        'name' : 'Videokyc',
        'expiry': expiry
    }
    url = 'https://one.in-d.ai/api/applications/'
    response = requests.post(url, data=json.dumps(data), headers=header)
    print(response.content, response.status_code)
    response = requests.post(url, data=json.dumps(data), headers=header).json()
    key = response.get('key', False)
    if key:
        return key
    else:
        return False

def add_agent(name, agent_id, password, email, company, phone, availabilty='A'):
    try:
        Session = sessionmaker(bind = engine)
        session = Session()
        
        if not Agent.check_agent(agent_id,session):
            ret, ret1 = fail(session, 'Agent-ID already present please refresh again')
            return ret, ret1

        flag = True
        flag, flag1, response = indone_registration(email=email, password=password, name=name, last_name= name[0], phone=phone)
        if flag1:
            if Agent.check_agent_email(email,session):
                if not Agent.insert_agent(session, name=name, agent_id=agent_id, password=password, email=email, company=company, avail='A'):
                    session.rollback()
                    print('Could not add agent')
                    return False, 'Could not add agent some error occured'
        print(response)
        session.commit()
    except:
        print(traceback.print_exc())
        session.rollback()
        session.close()
        print('Could not add agent')
        return False, 'Could not add agent'        
    finally:
        session.close()
    return flag, response

def fail(session,message):
    session.rollback()
    session.close()
    print(message)
    return False, message

def force_exit(agent_id,user_id):
    try:
        Session = sessionmaker(bind = engine)
        session = Session()
        
        company = Agent.get_company(session, agent_id)
        if not company:
            ret, ret1 = fail(session, 'Could not fetch company name')
            return ret, ret1
        
        if not User.precheck_finish(session,agent_id,user_id):
            ret, ret1 = fail(session, 'User is not assigned to the agent')
            return ret, ret1

        if not User.check_status(session, user_id, 'OP'):
            ret, ret1 = fail(session, 'User is diffrent status')
            return ret, ret1

        if not Agent.check_status(session, agent_id, 'O'):
            ret, ret1 = fail(session, 'Agent is diffrent status')
            return ret, ret1

        user = User.reomve_user_db(session,user_id)
        if not user:
            session.rollback()
            session.close()
            print('Could not remove user with user_id')
            return False, 'Could not remove user with user_id'

        avail_agent = Agent.change_avail(session,agent_id,'F')
        if not avail_agent:
            session.rollback()
            session.close()
            print('Could not change availabilty')
            return False, 'Could not change availabilty of agent'
        
        if not AgentQueue.check_null_agent(session, company):    
            
            adag = AgentQueue.add_agent_in_queue(session,agent_id, company)
            if not adag:
                ret, ret1 = fail(session,'cannot add agent in queue')
                return ret,ret1
            session.commit()
            session.close()
            return True, 'Done'
        
        else:

            if UserQueue.check_null_user(session, company):

                adagq = AgentQueue.add_agent_in_queue(session, agent_id, company)
                if not adagq:
                    ret, ret1 = fail(session,'cannot add agent in queue')
                    return ret, ret1
                session.commit()
                session.close()
                return True, 'Done'
            
            else:

                user_id, email1 = UserQueue.pop_user_from_queue(session, company)
                if not user_id:
                    ret, ret1 = fail(session,'Cannot pop user from queue')
                    return ret, ret1
                
                usrbth = User.change_both_db(session,user_id,agent_id,'OP')
                if not usrbth:
                    ret, ret1 = fail(session,'Cannot change both')
                    return ret, ret1

                agtav = Agent.change_avail(session,agent_id,'O')
                if not agtav:
                    ret, ret1 = fail(session,'Cannot change avalability')
                    return ret, ret1
        key = indone_api_key_creation(agent_id, str(uuid4()), expiry=0.02)
        if not key:
            ret, ret1 = fail(session, 'Could not generate ind-one key')
            return ret, ret1

        session.commit()
    except:
        print(traceback.print_exc())
        session.rollback()
        session.close()
        print('Could not force exit')
        return False, 'Could not force exit'
    finally:
        session.close()
    data = {'email': email1, 'agent_id': agent_id, 'user_id': user_id, 'company': company, 'key': key}
    return True, data


def agent_login(agent_id):
    try:
        Session = sessionmaker(bind = engine)
        session = Session()

        company = Agent.get_company(session, agent_id)
        if not company:
            ret, ret1 = fail(session, 'Could not fetch company name')
            return ret, ret1

        if Agent.check_status(session, agent_id, 'O'):
            if not User.remove_user_db_agent_avail(session, agent_id):
                ret, ret1 = fail(session, 'Could not remove user from db since he is in a unfinished call')
                return ret, ret1

        if Agent.check_status(session, agent_id, 'F'):
            if not AgentQueue.remove_agent_from_queue(session,agent_id):
                ret, ret1 = fail(session, 'Could not remove Agent from queue since he is in a unfinished logout')
                return ret, ret1

        
        if not Agent.change_avail(session,agent_id,avail='F'):
            session.rollback()
            session.close()
            print('Could not login')
            return False, 'Could not login'

        if not AgentQueue.check_null_agent(session, company):    
            
            adag = AgentQueue.add_agent_in_queue(session,agent_id, company)
            if not adag:
                ret, ret1 = fail(session,'cannot add agent in queue')
                return ret,ret1
            session.commit()
            session.close()
            return True, 'Done'
        
        else:

            if UserQueue.check_null_user(session, company):

                adagq = AgentQueue.add_agent_in_queue(session,agent_id, company)
                if not adagq:
                    ret, ret1 = fail(session,'cannot add agent in queue')
                    return ret, ret1
                session.commit()
                session.close()
                return True, 'Done'
            
            else:

                user_id, email1 = UserQueue.pop_user_from_queue(session, company)
                if not user_id:
                    ret, ret1 = fail(session,'Cannot pop user from queue')
                    return ret, ret1
                
                usrbth = User.change_both_db(session,user_id,agent_id,'OP')
                if not usrbth:
                    ret, ret1 = fail(session,'Cannot change both')
                    return ret, ret1

                agtav = Agent.change_avail(session,agent_id,'O')
                if not agtav:
                    ret, ret1 = fail(session,'Cannot change avalability')
                    return ret, ret1
        key = indone_api_key_creation(agent_id, str(uuid4()), expiry=0.02)
        if not key:
            ret, ret1 = fail(session, 'Could not generate ind-one key')
            return ret, ret1

        session.commit()        
    except:
        print(traceback.print_exc())
        session.rollback()
        session.close()
        print('Could not login')
        return False, 'Could not login'
    
    finally:
        session.close()
    data = {'email': email1, 'agent_id': agent_id, 'user_id': user_id, 'company': company, 'key': key}
    return True, data

def agent_logout(agent_id):
    try:
        Session = sessionmaker(bind = engine)
        session = Session()

        if not Agent.check_status(session, agent_id, 'F'):
            ret, ret1 = fail(session, 'Agent is diffrent status')
            return ret, ret1
        
        que_rem = AgentQueue.remove_agent_from_queue(session,agent_id)
        if not que_rem:
            session.rollback()
            session.close()
            print('Could not remove from Queue')
            return False, 'Could not remove from Queue'       

        avail = Agent.change_avail(session,agent_id,'A')
        if not avail:
            session.rollback()
            session.close()
            print('Could not change to occupied')
            return False, 'Could not change to occupied'
        session.commit()
    except:
        print(traceback.print_exc())
        session.rollback()
        session.close()
        print('Could not logout')
        return False, 'Could not logout'
    finally:
        session.close()
    return True, 'Done'


def add_user(phone, email, name, company, status='W',id1=None):
    try:
        Session = sessionmaker(bind = engine)
        session = Session()
        
        if Agent.check_all_away(session, company):
            ret,ret1 = fail(session,'All agents are away')
            return ret,ret1

        usdb, user_id = User.insert_user_db(session, phone=phone, email=email, name=name, company=company, status='W')
        if not usdb:
            ret,ret1 = fail(session,'Could not add user in DB')
            return ret,ret1
        
        if not UserQueue.check_null_user(session, company):
            
            usq = UserQueue.add_user_in_queue(session, user_id, email, company)
            if not usq:
                ret,ret1 = fail(session,'You have been added in the queue already a email will be sent to you shortly')
                return ret,ret1
            print('ADDED in 1')
            session.commit()
            session.close()
            return True, 'Done'
        
        else:

            if AgentQueue.check_null_agent(session, company):
                usq = UserQueue.add_user_in_queue(session, user_id, email, company)
                if not usq:
                    ret,ret1 = fail(session,'You have been added in the queue already a email will be sent to you shortly')
                    return ret,ret1
                print('ADDED in 2')
                session.commit()
                session.close()
                return True, 'Done'
            
            else:
                agent_id = AgentQueue.pop_agent_from_queue(session, company)
                if not agent_id:
                    ret,ret1 = fail(session,'Cannot pop agent')
                    return ret,ret1
                
                agent_avl = Agent.change_avail(session,agent_id,'O')
                if not agent_avl:
                    ret,ret1 = fail(session, 'Could not change availability')
                    return ret,ret1
                
                user_both = User.change_both_db(session, user_id, agent_id,'OP')
                if not user_both:
                    ret,ret1 = fail(session, 'Could not change 2 changes')
                    return ret,ret1
        key = indone_api_key_creation(agent_id, str(uuid4()), expiry=0.02)
        if not key:
            ret, ret1 = fail(session, 'Could not generate ind-one key')
            return ret, ret1

        session.commit()
    
    except:
        print(traceback.print_exc())
        ret,ret1 = fail(session,'Could not add user')
        return ret,ret1
    
    finally:
        session.close()
    
    data = {'email': email, 'agent_id': agent_id, 'user_id': user_id, 'company': company, 'key': key}
    return True, data

def finish(agent_id, user_id,uid, geo, liveness, validation, face):
    try:
        Session = sessionmaker(bind = engine)
        session = Session()
        
        company = Agent.get_company(session, agent_id)
        if not company:
            ret, ret1 = fail(session, 'Could not fetch company name')
            return ret, ret1

        if not User.precheck_finish(session,agent_id,user_id):
            ret, ret1 = fail(session, 'User is not assigned to the agent')
            return ret, ret1
        
        if not User.check_status(session, user_id, 'OP'):
            ret, ret1 = fail(session, 'User is diffrent status')
            return ret, ret1

        if not Agent.check_status(session, agent_id, 'O'):
            ret, ret1 = fail(session, 'Agent is diffrent status')
            return ret, ret1

        usrstat = User.change_state_db_email(session, user_id, uid, geo, liveness, validation, face, 'F')
        if not usrstat:
            ret, ret1 = fail(session,'Cannot change to finish')
            return ret, ret1
        
        agentavai = Agent.change_avail(session,agent_id,'F')
        if not agentavai:
            ret, ret1 = fail(session,'Cannot change to free')
            return ret,ret1
        
        if not AgentQueue.check_null_agent(session, company=company):
            
            adag = AgentQueue.add_agent_in_queue(session,agent_id, company)
            if not adag:
                ret, ret1 = fail(session,'cannot add agent in queue')
                return ret,ret1
            session.commit()
            session.close()
            return True, 'Done'
        else:

            if UserQueue.check_null_user(session, company):

                adagq = AgentQueue.add_agent_in_queue(session,agent_id, company)
                if not adagq:
                    ret, ret1 = fail(session,'cannot add agent in queue')
                    return ret, ret1
                session.commit()
                session.close()
                return True, 'Done'
            
            else:

                user_id, email1 = UserQueue.pop_user_from_queue(session, company)
                if not user_id:
                    ret, ret1 = fail(session,'Cannot pop user from queue')
                    return ret, ret1
                
                usrbth = User.change_both_db(session,user_id,agent_id,'OP')
                if not usrbth:
                    ret, ret1 = fail(session,'Cannot change both')
                    return ret, ret1

                agtav = Agent.change_avail(session,agent_id,'O')
                if not agtav:
                    ret, ret1 = fail(session,'Cannot change avalability')
                    return ret, ret1
        key = indone_api_key_creation(agent_id, str(uuid4()), expiry=0.02)
        if not key:
            ret, ret1 = fail(session, 'Could not generate ind-one key')
            return ret, ret1
        session.commit()
    except:
        print(traceback.print_exc())
        session.rollback()
        session.close()
        print('Could finish the Close process')
        return False, 'Could finish the process'
    finally:
        session.close()
    data = {'email': email1, 'agent_id': agent_id, 'user_id': user_id, 'company': company, 'key': key}
    return True, data

def finish_exit(agent_id, user_id, uid, geo, liveness, validation, face):
    try:
        Session = sessionmaker(bind = engine)
        session = Session()
        
        company = Agent.get_company(session, agent_id)
        if not company:
            ret, ret1 = fail(session, 'Could not fetch company name')
            return ret, ret1

        if not User.precheck_finish(session,agent_id,user_id):
            ret, ret1 = fail(session, 'User is not assigned to the agent')
            return ret, ret1
        
        if not User.check_status(session, user_id, 'OP'):
            ret, ret1 = fail(session, 'User is diffrent status')
            return ret, ret1

        if not Agent.check_status(session, agent_id, 'O'):
            ret, ret1 = fail(session, 'Agent is diffrent status')
            return ret, ret1

        usrstat = User.change_state_db_email(session, user_id, uid, geo, liveness, validation, face, 'F')
        if not usrstat:
            ret, ret1 = fail(session,'Cannot change to finish')
            return ret, ret1
        
        agentavai = Agent.change_avail(session,agent_id,'A')
        if not agentavai:
            ret, ret1 = fail(session,'Cannot change to Away')
            return ret,ret1
        session.commit()
    except:
        print(traceback.print_exc())
        session.rollback()
        session.close()
        print('could not finish and logout')
        return False, 'could not finish and logout'
    finally:
        session.close()
    return True, 'Done'

def extract_user_data(agent_id):
    try:
        Session = sessionmaker(bind = engine)
        session = Session()
        
        company = Agent.get_company(session, agent_id)
        if not company:
            ret, ret1 = fail(session, 'Could not fetch company name')
            data = []
            return data

        data = User.fetch_by_agentid(session,agent_id, company)
        session.commit()
    except:
        print(traceback.print_exc())
        data = []
        session.rollback()
        session.close()
        return data
    finally:
        session.close()
    return data

def login_password(agent_id, password, email):
    try:
        Session = sessionmaker(bind = engine)
        session = Session()

    #     password_db = Agent.get_password(session,agent_id)
    #     if password_db == password:
    #         flag = True
    #     else:
    #         flag =  False
        if not Agent.check_email(session, email):
            print('Email id is not present in video-Kyc')
            return False, 'Email id is not present in video-Kyc'

        token = indone_agent_token_generation(email, password, agent_id, channel='WB')
        if not token:
            print('Ind Token generation is not complete')
            return False, 'Ind Token generation is not complete'
        flag = True
    except:
        print(traceback.print_exc())
        print('Cannot compare password')
        return False, 'Cannot generate token'
    return flag, token

def get_id_byemail(email):
    try:
        Session = sessionmaker(bind = engine)
        session = Session()

        agent_id = Agent.get_agentid(session, email)
        if not agent_id:
            ret, ret1 = fail(session, 'Could not fetch agentID')
            return ret, ret1
        session.commit()
    except:
        print(traceback.print_exc())
        ret, ret1 = fail(session, 'Error while fetching agentId')
        return ret, ret1
    finally:
        session.close()
        return True, agent_id

def insert_link(user_id,link):
    try:
        Session = sessionmaker(bind = engine)
        session = Session() 

        if not User.update_link(session,user_id,link):
            ret, ret1 = fail(session,'Could not update the link')
            return ret, ret1
        
        session.commit()
    except:
        print(traceback.print_exc())
        ret, ret1 = fail(session, 'Error while updating')
    finally:
        session.close()
    return True, 'Done'

def search(agent_id, search_id, search_text, end_date=False):
    try:
        Session = sessionmaker(bind = engine)
        session = Session()
        
        company = Agent.get_company(session, agent_id)
        if not company:
            ret, ret1 = fail(session, 'Could not fetch company name')
            data = []
            return data

        data = User.search(session, company ,agent_id, search_id, search_text, end_date)
        session.commit()
    except:
        print(traceback.print_exc())
        data = []
        session.rollback()
        session.close()
        return data
    finally:
        session.close()
    return data

def drop_call(agent_id):
    try:
        Session = sessionmaker(bind = engine)
        session = Session()
        
        company = Agent.get_company(session, agent_id)
        if not company:
            ret, ret1 = fail(session, 'Could not fetch company name')
            return ret, ret1
        
        if Agent.check_status(session, agent_id, 'O'):
            print('IN1')
            if not User.remove_user_db_agent_avail(session, agent_id):
                ret, ret1 = fail(session, 'Could not remove user from db since the user record is missing')
                return ret, ret1

        if Agent.check_status(session, agent_id, 'F'):
            print('IN2')
            if not AgentQueue.remove_agent_from_queue(session,agent_id):
                ret, ret1 = fail(session, 'Could not remove Agent from queue since he is not present')
                return ret, ret1

        print(agent_id)
        if not Agent.change_avail(session,agent_id,avail='A'):
            session.rollback()
            session.close()
            print('Could not login')
            return False, 'Could not login'
        session.commit()
    except:
        print(traceback.print_exc())
        session.rollback()
        session.close()
        return False, 'Error while hanging-up'
    finally:
        session.close()
    return True, 'Done'