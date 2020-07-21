from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine, MetaData, and_
from sqlalchemy.schema import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import traceback
from collections import defaultdict
from uuid import uuid4

BASE = declarative_base()

#############################################################
# Has the DB strucutre of Agent, Agent-Queue, User, User-Queue
##############################################################
'''
Steps present in the file
- Created DB for Agent
    1. Permfored the operations such as adding, updating and selecting
- Created a DB for User
- Created queue for agent
-Cretaed queue for user

'''
class Agent(BASE):
    __tablename__ = 'agenttable'
    name = Column(String,nullable=False)
    agent_id = Column(String,primary_key=True)
    avail = Column(String,nullable=False)
    time_stamp = Column(DateTime)
    password = Column(String, nullable=False)
    email = Column(String,nullable=False)
    company = Column(String, nullable=False)

    def __init__(self,name,agent_id,avail,password,email, company):
        self.name = name
        self.agent_id = agent_id
        self.avail = avail
        self.time_stamp = datetime.datetime.now()+datetime.timedelta(hours=5,minutes=30)
        self.password = password
        self.email = email
        self.company = company
    
    def check_agent(agent_id,session):
        '''
        Since agent-ids are given randomnly should 
        be checked with the bd so that the user id isnt 
        already present
        '''
        agent = BASE.metadata.tables['agenttable']
        try:
            query_result = session.execute(agent.select())
        except:
            print(traceback.print_exc())
            print('Could not fetch Agent-id')
            return False

        data = [list(row) for row in query_result]
        for row in data:
            if agent_id == row[1]:
                return False
        return True
    
    def check_agent_email(email,session):
        '''
        Check if a agent of particuar email id is already present
        '''
        agent = BASE.metadata.tables['agenttable']
        try:
            query_result = session.execute(agent.select())
        except:
            print(traceback.print_exc())
            print('Could not fetch Agent-id')
            return False

        data = [list(row) for row in query_result]
        for row in data:
            if email == row[5]:
                return False
        return True
    
    def insert_agent(session,name, agent_id, password, email, company, avail='F'):
        '''
        Adding a agent into the DB
        '''
        if Agent.check_agent(agent_id = agent_id, session=session):
            a1 = Agent(name,agent_id,avail,password,email, company=company)
            session.add(a1)
        else:
            print('Agent Id is already present')
            return False
        return True
    
    def change_avail(session, agent_id, avail):
        '''
        Changing the alvalibilty of the agent
        '''
        agent = BASE.metadata.tables['agenttable']
        if session.query(agent).filter(agent.c.agent_id == agent_id).update({'avail': avail},synchronize_session=False):
            return True
        else:
            print('Could not change availabilty')
            return False
    
    def remove_agent_from_db(session, agent_id):
        agent = BASE.metadata.tables['agenttable']
        if session.query(agent).filter(agent.c.agent_id == agent_id).delete(synchronize_session=False):
            return True
        else:
            print('Could not remove agent from DB')
            return False

    def check_all_away(session, company):
        agent = BASE.metadata.tables['agenttable']
        if len(session.query(agent).filter(agent.c.company==company).all()) == len(session.query(agent).filter(and_(agent.c.avail=='A', agent.c.company==company)).all()):
            return True
        else:
            return False
    
    def check_avilability(session, agent_id, avail):
        agent = BASE.metadata.tables['agenttable']
        if session.query(agent).filter(agent.c.agent_id==agent_id).first().avail == avail:
            return True
        else:
            return False
    
    def get_password(session, agent_id):
        agent = BASE.metadata.tables['agenttable']
        data = session.query(agent.c.password).filter(agent.c.agent_id==agent_id).first()
        if data:
            data = data[0] 
        return data
    
    def get_agentid(session,email):
        agent = BASE.metadata.tables['agenttable']
        agent_id = session.query(agent.c.agent_id).filter(agent.c.email==email).first()
        if agent_id:
            agent_id = agent_id[0]
        return agent_id

    def check_status(session,agent_id,status):
        agent = BASE.metadata.tables['agenttable']
        if session.query(agent).filter(agent.c.agent_id==agent_id).first().avail == status:
            return True
        else:
            return False
    
    def get_company(session, agent_id):
        agent = BASE.metadata.tables['agenttable']
        company = session.query(agent.c.company).filter(agent.c.agent_id==agent_id).first()
        if company:
            company = company[0]
        return company
    
    def check_email(session, email_id):
        agent = BASE.metadata.tables['agenttable']
        query_result = session.query(agent).filter(agent.c.email==email_id).all()
        if query_result:
            return True
        else:
            return False
class User(BASE):
    __tablename__ = 'usertable'
    user_id = Column(String,primary_key=True)
    phone_number = Column(String,nullable=False)
    email = Column(String,nullable=False)
    name = Column(String,nullable=False)
    agent_id = Column(String, ForeignKey('agenttable.agent_id'))
    status = Column(String)
    time_stamp = Column(DateTime)
    uid = Column(String)
    geo = Column(String)
    liveliness = Column(String)
    validation = Column(String)
    face = Column(String)
    zipfolder_link = Column(String)
    company = Column(String)

    def __init__(self,user_id,phone,email,name, company, status='W',id1=None,uid=None,geo=None,liveness=None,validation=None,face=None):
        self.user_id = user_id
        self.phone_number = phone
        self.email = email
        self.name = name
        self.agent_id = id1
        self.status = status
        self.company = company
        self.time_stamp = datetime.datetime.now() + datetime.timedelta(hours=5,minutes=30)
        self.uid = uid
        self.geo = geo
        self.liveliness = liveness
        self.validation = validation
        self.face = face
    
    def check_user_id(user_id, session):
        user = BASE.metadata.tables['usertable']
        try:
            query_result = session.execute(user.select())
        except:
            print(traceback.print_exc())
            print('Could not fetch phone number')
            return False
        data = [list(row) for row in query_result]
        for row in data:
            if user_id == row[0]:
                return False
        return True

    def insert_user_db(session, phone, email, name, company, status='W',id1=None,uid=None):
        flag = True
        while(flag):
            user_id = str(uuid4())
            flag = not(User.check_user_id(user_id,session))
        u1 = User(user_id=user_id, phone=phone, email=email, name=name, company=company)
        session.add(u1)
        return True, user_id
    
    def change_status_db(session,user_id,status='F'):
        user = BASE.metadata.tables['usertable']
        if session.query(user).filter(user.c.user_id==user_id).update({'status':status},synchronize_session=False):
            return True
        else:
            print('Could not make a change')
            return False
    
    def change_both_db(session,user_id,agent_id,status='OP'):
        user = BASE.metadata.tables['usertable']
        try:
            session.query(user).filter(user.c.user_id==user_id).update({'status':status, 'agent_id': agent_id},synchronize_session=False)
            return True
        except:
            print(traceback.print_exc())
            print('Can not add agent id')
            return False

    def reomve_user_db(session,user_id):
        user = BASE.metadata.tables['usertable']
        if session.query(user).filter(user.c.user_id==user_id).delete(synchronize_session=False):
            return True
        else:
            print('Could not remove user from db')
            return False
    
    def remove_user_db_agent_avail(session, agent_id, status='OP'):
        user = BASE.metadata.tables['usertable']
        if session.query(user).filter(and_(user.c.agent_id==agent_id, user.c.status==status)).delete(synchronize_session=False):
            return True
        else:
            print('Could not remove user from db since he is in a unfinished call')
            return False

    def change_state_db_email(session,user_id,uid,geo,liveness,validation,face,status='F'):
        user = BASE.metadata.tables['usertable']
        if session.query(user).filter(user.c.user_id==user_id).update({'status':status, 'uid': uid, 'geo': geo, 'liveliness': liveness, 'validation': validation, 'face': face},synchronize_session=False):
            return True
        else:
            print('Cannot change status using email')
            return False

    def check_status(session,user_id,status):
        user = BASE.metadata.tables['usertable']
        if session.query(user).filter(user.c.user_id==user_id).first().status == status:
            return True
        else:
            return False
    
    def fetch_by_agentid(session,agent_id, company):
        user = BASE.metadata.tables['usertable']
        data = session.query(user.c.name, user.c.phone_number, user.c.uid, user.c.geo, user.c.liveliness, user.c.validation, user.c.face, user.c.time_stamp, user.c.zipfolder_link, user.c.email).filter(and_(user.c.agent_id==agent_id, user.c.company==company)).all()
        if data:
            return_data = defaultdict(list)
            failed = []
            passed = []
            null = []
            for record in data:
                record = list(record)
                record[7] = record[7].strftime('%d-%m-%Y %H:%M:%S')
                if None in record:
                    null.append(record)
                elif 'false' in record:
                    failed.append(record)
                else:
                    passed.append(record)
            return_data = {'pass': passed, 'failed': failed, 'null': null}
            return return_data
        else:
            data = {'pass': [], 'failed': [], 'null': []}
            return data
    
    def search(session, company, agent_id, id_text, srhtext, end_date=False):
        user = BASE.metadata.tables['usertable']
        mapper = {
            'name': user.c.name,
            'phone': user.c.phone_number,
            'email': user.c.email,
            'agent': user.c.agent_id,
            'status': user.c.status,
            'time': user.c.time_stamp
        }
        if id_text != 'time':
            search_text = '%'+srhtext+'%'
            data = session.query(user.c.name, user.c.phone_number, user.c.uid, user.c.geo, user.c.liveliness, user.c.validation, user.c.face, user.c.time_stamp, user.c.zipfolder_link, user.c.email).filter(and_(user.c.agent_id==agent_id, mapper[id_text].ilike(search_text), user.c.company==company)).all()
            if data:
                return_data = defaultdict(list)
                failed = []
                passed = []
                null = []
                for record in data:
                    record = list(record)
                    record[7] = record[7].strftime('%d-%m-%Y %H:%M:%S')

                    if None in record:
                        null.append(record)
                    elif 'false' in record:
                        failed.append(record)
                    else:
                        passed.append(record)
                return_data = {'pass': passed, 'failed': failed, 'null': null}
                return return_data
            else:
                data = {'pass': [], 'failed': [], 'null': []}
                return data
        else:
            if end_date:
                start_date = datetime.datetime.strptime(srhtext, '%Y-%m-%d')
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
                data = session.query(user.c.name, user.c.phone_number, user.c.uid, user.c.geo, user.c.liveliness, user.c.validation, user.c.face, user.c.time_stamp, user.c.zipfolder_link, user.c.email).filter(and_(user.c.agent_id==agent_id,user.c.time_stamp.between(start_date,end_date), user.c.company==company)).all()
            else:
                start_date = datetime.datetime.strptime(srhtext, '%Y-%m-%d')
                end_date = datetime.datetime.strptime(srhtext,'%Y-%m-%d')+datetime.timedelta(days=1)
                data = session.query(user.c.name, user.c.phone_number, user.c.uid, user.c.geo, user.c.liveliness, user.c.validation, user.c.face, user.c.time_stamp, user.c.zipfolder_link, user.c.email).filter(and_(user.c.agent_id==agent_id,user.c.time_stamp.between(start_date,end_date), user.c.company==company)).all()
            if data:
                return_data = defaultdict(list)
                failed = []
                passed = []
                null = []
                for record in data:
                    record = list(record)
                    record[7] = record[7].strftime('%d-%m-%Y %H:%M:%S')

                    if None in record:
                        null.append(record)
                    elif 'false' in record:
                        failed.append(record)
                    else:
                        passed.append(record)
                return_data = {'pass': passed, 'failed': failed, 'null': null}
                return return_data
            else:
                data = {'pass': [], 'failed': [], 'null': []}
                return data

    def precheck_finish(session, agent_id, user_id):
        user = BASE.metadata.tables['usertable']
        agent_id_db = session.query(user.c.agent_id).filter(user.c.user_id==user_id).first()
        if agent_id_db:
            agent_id_db = agent_id_db[0]
        if agent_id == agent_id_db:
            return True
        else:
            return False
    
    def update_link(session, user_id, link):
        user = BASE.metadata.tables['usertable']
        if session.query(user).filter(user.c.user_id==user_id).update({'zipfolder_link':link},synchronize_session=False):
            return True
        else:
            return False
    


class AgentQueue(BASE):
    __tablename__ = 'agentqueue'
    agent_id = Column(String, primary_key=True)
    company = Column(String)

    def __init__(self,agent_id, company):
        self.agent_id = agent_id
        self.company = company
    
    def check_agent_queue(session, agent_id):
        agentqueue = BASE.metadata.tables['agentqueue']
        try:
            query_result = session.execute(agentqueue.select())
        except:
            print(traceback.print_exc())
            print('Could not fetch Agent-id from queue')
            return False
        data = [list(row) for row in query_result]
        for row in data:
            if agent_id == row[0]:
                return False
        return True

    def add_agent_in_queue(session,agent_id, company):
        if AgentQueue.check_agent_queue(session,agent_id):
            aq = AgentQueue(agent_id, company=company)
            session.add(aq)
        else:
            print('Id is present in queue')
            return False
        return True
    
    def pop_agent_from_queue(session, company):
        agentqueue = BASE.metadata.tables['agentqueue']
        agent_id_query = session.query(agentqueue).filter(agentqueue.c.company==company).first()
        if agent_id_query:
            agent_id = agent_id_query.agent_id
            session.query(agentqueue).filter(agentqueue.c.agent_id==agent_id).delete(synchronize_session=False)
        else:
            print('Could not pop because it was null')
            return False
        return agent_id
    
    def check_null_agent(session, company):
        agentqueue = BASE.metadata.tables['agentqueue']
        agent_id_query = session.query(agentqueue).filter(agentqueue.c.company==company).first()
        if agent_id_query:
            return False
        else:
            return True
    
    def remove_agent_from_queue(session, agent_id):
        agentqueue = BASE.metadata.tables['agentqueue']
        if session.query(agentqueue).filter(agentqueue.c.agent_id==agent_id).delete(synchronize_session=False):
            return True
        else:
            print('Could not delete the agent')
            return False


class UserQueue(BASE):
    __tablename__ = 'userqueue'
    user_id = Column(String, primary_key=True)
    email = Column(String)
    company = Column(String)
    
    def __init__(self,user_id,email, company):
        self.user_id = user_id
        self.email = email
        self.company = company
    
    def check_userq_phone(session,user_id, email):
        userqueue = BASE.metadata.tables['userqueue']
        try:
            query_result = session.execute(userqueue.select())
        except:
            print(traceback.print_exc())
            print('Could not fetch Userid from queue')
            return False
        try:
            email_there = session.query(userqueue).filter(userqueue.c.email==email).all()
        except:
            print(traceback.print_exc())
            print('Could not fetch Email')
            return False
        data = [list(row) for row in query_result]
        for row in data:
            if user_id == row[0] or email_there:
                return False
        return True

    def add_user_in_queue(session, user_id, email, company):
        if UserQueue.check_userq_phone(session,user_id,email):
            uq = UserQueue(user_id=user_id, email=email, company=company)
            session.add(uq)
        else:
            print('user Id is present already') 
            return False
        return True

    def pop_user_from_queue(session,company):
        userqueue = BASE.metadata.tables['userqueue']
        phone_query = session.query(userqueue).filter(userqueue.c.company==company).first()
        if phone_query:
            user_id1 = phone_query.user_id
            email = phone_query.email
            session.query(userqueue).filter(userqueue.c.user_id==user_id1).delete(synchronize_session=False)
        else:
            print('Could not pop because null')
            return False, ''
        return user_id1,email
    
    def check_null_user(session, company):
        userqueue = BASE.metadata.tables['userqueue']
        phone_query = session.query(userqueue).filter(userqueue.c.company==company).first()
        if phone_query:
            return False
        else:
            return True

    def remove_user_from_queue(session,user_id):
        userqueue = BASE.metadata.tables['userqueue']
        if session.query(userqueue).filter(userqueue.c.user_id==user_id).delete(synchronize_session=False):
            return True
        else:
            print('Could not delete the user')
            return False
