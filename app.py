from flask import Flask, jsonify, request, make_response
import jwt
from _datetime import datetime
from datetime import timedelta
from functools import wraps
from pymongo import MongoClient
import hashlib
from firebase import firebase
from firebase_admin import db, credentials

# from Objects import ProjectWorker

app = Flask(__name__)

# host = "localhost"
# port = 27017
host = "mongodb://raza:FUckoff92@ds119370.mlab.com:19370/fyp"
port = 19370
client = MongoClient(host=host, port=port)
# connection = client["FYP"]
connection = client["fyp"]
app.config['SECRET_KEY'] = 'thisisthesecretkey'
location = ""
budget = 0
database = 'shopreality-57d63'
collection = 'testing'
data = {
    'Name': 'Saba',
    'class': 'FYP'
}


def connecttofirebase(database):
    firebaseObject = firebase.FirebaseApplication('https://' + database + '.firebaseio.com/', None)
    return firebaseObject


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('key')  # http://127.0.0.1:5000/route?token=alshfjfjdklsfj89549834ur

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated


def getRating(worker):
    length = len(worker['Ratings'])
    ratings = 0
    for a in range(0, length, 1):
        ratings = ratings + worker['Ratings'][a]['Rating']
    return ratings / length


@app.route('/unprotected')
def unprotected():
    return jsonify({'message': 'Anyone can view this!'})


@app.route('/', methods=['GET'])
def start():
    # return "Welcome to the construction recommendation system"
    if connection:
        return "connected"
    else:
        return "not connected"


@app.route('/Dummy', methods=['POST'])
def dummy():
    request_data = request.get_json()
    date = datetime.strptime(request_data['Date'], '%b/%d/%Y')
    date = date + timedelta(days=2)
    date = datetime.strftime(date, '%d-%b-%Y')
    return date

    # firebase = connecttofirebase(database)
    # result = firebase.post('/' + collection + '/', data)
    # return "Ho gya"


# return hashlib.md5("1234567891011".encode()).hexdigest()


@app.route('/acceptBid', methods=['Post'])
def acceptbid():
    request_data = request.get_json()
    Bid = connection["Bids"]
    bid = Bid.find_one({"ID": request_data['ID']})
    Need = connection['Needs']
    need = Need.find_one({"ID": bid['ID']})
    AcceptBid = connection['AcceptBid']
    AcceptBid.insert_one({"Need": need['ID'], "Bid": bid['ID']})
    return "Acccepted the Bid"


@app.route('/AddClient', methods=['Post'])
# @token_required
def AddClient():
    # connection.authenticate("raza2", "FUckoff92")
    Client = connection["Client"]
    request_data = request.get_json()
    new_client = Client.find_one({'NIC': request_data['CNIC']})
    Login = connection["Login"]
    new_login = Login.find_one(request_data["CNIC"])
    if new_client is None and new_login is None:
        Client.insert({'Name': request_data['Name'], 'Contact': request_data['Phone'], 'Email': request_data[
            'Email'], 'Address': request_data['Address'], 'NIC': request_data['CNIC']})
        Client = connection["Login"]
        Client.insert(
            {'NIC': request_data["CNIC"], 'password': hashlib.md5(request_data['Password'].encode()).hexdigest()})
        return 'Client is inserted'
    return 'Client already registered'


@app.route('/addVendor', methods=['POST'])
def addVendor():
    id = 1
    request_data = request.get_json()
    Vendor = connection['Vendor']
    lastvendor = Vendor.find().sort([("ID", -1)])
    try:
        id = lastvendor[0]['ID']
    except:
        id = 1
    Vendor.insert_one({"Name": request_data['name'], "Contact": request_data['phone'],
                       "Category": request_data['category'], "Address": request_data['address'], "ID": id})
    return "Vendor is added"


@app.route('/Addworker', methods=['Post'])
# @token_required
def AddWorker():
    Worker = connection["Worker"]
    request_data = request.get_json()
    new_worker = Worker.find_one({'NIC': request_data['CNIC']})
    Login = connection["Login"]
    new_login = Login.find_one({'NIC': request_data['CNIC']})
    if new_worker is None and new_login is None:
        Worker.insert({'Name': request_data['Name'], 'Contact': request_data['Phone'], 'Email': request_data[
            'Email'], 'Address': request_data['Address'], 'Category': request_data['Type'], 'NIC': request_data[
            'CNIC']})
        Worker = connection["Login"]
        Worker.insert(
            {'NIC': request_data["CNIC"], 'password': hashlib.md5(request_data['Password'].encode()).hexdigest()})
        return 'Worker is inserted'
    return 'Worker already registered'


@app.route('/algoArchitect', methods=['POST'])
@token_required
def Algoarchitect():
    Worker = connection["Worker"]
    workers = []
    allworker = Worker.find({'Category': 'Architect'},
                            {'_id': 0})
    x = 0
    count = 0
    while True:
        try:
            if allworker[x]['Price'] == {"$lt": (budget / 100) * 30}:
                count = count + 1
            if allworker[x]['Address'] == location:
                count = count + 1
            similarity = count / 2
            if similarity > 0.5:
                workers.append(allworker[x])
            x = x + 1
            count = 0
        except:
            break
    return jsonify({"workers": workers})


@app.route('/algoContractor', methods=['POST'])
@token_required
def Algocontractor():
    Worker = connection["Worker"]
    workers = []
    allworker = Worker.find({'Category': 'Contractor'},
                            {'_id': 0})
    x = 0
    count = 0
    while True:
        try:
            if allworker[x]['Price'] == {"$lt": (budget / 100) * 30}:
                count = count + 1
            if allworker[x]['Address'] == location:
                count = count + 1
            similarity = count / 2
            if similarity > 0.5:
                workers.append(allworker[x])
            x = x + 1
            count = 0
        except:
            break
    return jsonify({"workers": workers})


@app.route('/algoCarpenters', methods=['POST'])
@token_required
def Algocarpenter():
    Worker = connection["Worker"]
    workers = []
    allworker = Worker.find({'Category': 'Carpenter'},
                            {'_id': 0})
    x = 0
    count = 0
    while True:
        try:
            if allworker[x]['Price'] == {"$lt": (budget / 100) * 10}:
                count = count + 1
            if allworker[x]['Address'] == location:
                count = count + 1
            similarity = count / 2
            if similarity > 0.5:
                workers.append(allworker[x])
            x = x + 1
            count = 0
        except:
            break
    return jsonify({"workers": workers})


@app.route('/algoElectrician', methods=["GET"])
@token_required
def Algoelectricians():
    Worker = connection["Worker"]
    workers = []
    allworker = Worker.find({'Category': 'electrrician'},
                            {'_id': 0})
    x = 0
    count = 0
    while True:
        try:
            if allworker[x]['Price'] == {"$lt": (budget / 100) * 10}:
                count = count + 1
            if allworker[x]['Address'] == location:
                count = count + 1
            similarity = count / 2
            if similarity > 0.5:
                workers.append(allworker[x])
            x = x + 1
            count = 0
        except:
            break
    return jsonify({"workers": workers})


@app.route('/algoPainter', methods=['POST'])
@token_required
def Algopainter():
    Worker = connection["Worker"]
    workers = []
    allworker = Worker.find({'Category': 'Painter'},
                            {'_id': 0})
    x = 0
    count = 0
    while True:
        try:
            if allworker[x]['Price'] == {"$lt": (budget / 100) * 10}:
                count = count + 1
            if allworker[x]['Address'] == location:
                count = count + 1
            similarity = count / 2
            if similarity > 0.5:
                workers.append(allworker[x])
            x = x + 1
            count = 0
        except:
            break
    return jsonify({"workers": workers})


@app.route('/AlgoPlumbers', methods=['POST'])
@token_required
def Algoplumbers():
    Worker = connection["Worker"]
    workers = []
    allworker = Worker.find({'Category': 'electrrician'},
                            {'_id': 0})
    x = 0
    count = 0
    while True:
        try:
            if allworker[x]['Price'] == {"$lt": (budget / 100) * 10}:
                count = count + 1
            if allworker[x]['Address'] == location:
                count = count + 1
            similarity = count / 2
            if similarity > 0.5:
                workers.append(allworker[x])
            x = x + 1
            count = 0
        except:
            break
    return jsonify({"workers": workers})


@app.route('/AllArchitects', methods=['GET'])
@token_required
def AllArchitect():
    Worker = connection["Worker"]
    workers = []
    allworker = Worker.find({'Category': 'Architect'},
                            {"_id": 0})
    x = 0
    while True:
        try:
            workers.append(allworker[x])
            x = x + 1
        except:
            break
    for a in range(0, len(workers), 1):
        workers[a]['Ratings'] = getRating(workers[a])
    return jsonify({"workers": workers})


@app.route('/AllCarpenters', methods=['GET'])
@token_required
def AllCarpenters():
    Worker = connection["Worker"]
    workers = []
    allworker = Worker.find({'Category': 'Carpenter'},
                            {"_id": 0})
    x = 0
    while True:
        try:
            workers.append(allworker[x])
            x = x + 1
        except:
            break
    for a in range(0, len(workers), 1):
        workers[a]['Ratings'] = getRating(workers[a])
    return jsonify({"workers": workers})


@app.route('/AllContractors', methods=['GET'])
@token_required
def AllContractors():
    Worker = connection["Worker"]
    workers = []
    allworker = Worker.find({'Category': 'Contractor'},
                            {"_id": 0})
    x = 0
    while True:
        try:
            workers.append(allworker[x])
            x = x + 1
        except:
            break
    for a in range(0, len(workers), 1):
        workers[a]['Ratings'] = getRating(workers[a])
    return jsonify({"workers": workers})


@app.route('/AllElectrician', methods=['GET'])
@token_required
def AllWorkers():
    Worker = connection["Worker"]
    workers = []
    allworker = Worker.find({'Category': 'electrrician'},
                            {"_id": 0})
    x = 0
    while True:
        try:
            workers.append(allworker[x])
            x = x + 1
        except:
            break
    for a in range(0, len(workers), 1):
        workers[a]['Ratings'] = getRating(workers[a])
    return jsonify({"workers": workers})


@app.route('/AllPainter', methods=['GET'])
@token_required
def AllPainter():
    Worker = connection["Worker"]
    workers = []
    allworker = Worker.find({'Category': 'Painter'},
                            {"_id": 0})
    x = 0
    while True:
        try:
            workers.append(allworker[x])
            x = x + 1
        except:
            break
    for a in range(0, len(workers), 1):
        workers[a]['Ratings'] = getRating(workers[a])
    return jsonify({"workers": workers})


@app.route('/AllPlumbers', methods=['GET'])
@token_required
def AllPlumber():
    Worker = connection["Worker"]
    workers = []
    allworker = Worker.find({'Category': 'plumber'},
                            {"_id": 0})
    x = 0
    while True:
        try:
            workers.append(allworker[x])
            x = x + 1
        except:
            break
    for a in range(0, len(workers), 1):
        workers[a]['Ratings'] = getRating(workers[a])
    return jsonify({"workers": workers})


@app.route('/AllProjects', methods=['GET'])
@token_required
def AllProjects():
    Worker = connection["Projects"]
    workers = []
    allworker = Worker.find({},
                            {"_id": 0})
    x = 0
    while True:
        try:
            workers.append(allworker[x])
            x = x + 1
        except:
            break
    return jsonify({"projects": workers})


@app.route('/bidsActive', methods=['POST'])
def bidding():
    request_data = request.get_json()
    Needs = connection["Needs"]
    AllNeeds = Needs.find({'Category': request_data['category']}, {'_id': 0})
    needs = []
    x = 0
    while True:
        try:
            if AllNeeds[x]['End'] <= datetime.now().date():
                needs.append(AllNeeds[x])
                x = x + 1
        except:
            break
    return jsonify({'needs': needs})


@app.route('/Changepassword', methods=['POST'])
@token_required
def Changepass():
    request_data = request.get_json()
    Worker = connection["Login"]
    login_worker = Worker.find_one({"NIC": request_data["NIC"]})
    if login_worker:
        Worker.update_one(filter={"NIC": request_data["NIC"]},
                          update={'$set': {'password': request_data['password']}})
        return 'Password updated'
    return 'NIC incorrect'


@app.route('/Clientdetail', methods=['POST'])
@token_required
def ClientData():
    request_data = request.get_json()
    Worker = connection["Client"]
    login_worker = Worker.find_one({"NIC": request_data["NIC"]}, {'_id': 0})
    if login_worker:
        print(login_worker)
        return jsonify(login_worker)
    else:
        return "Client not found"


@app.route('/CreateProject', methods=['POST'])
# @token_required
def CreateProject():
    Worker = connection["Worker"]
    request_data = request.get_json()
    plumbers = []
    electricians = []
    architect = []
    contractor = []
    carpenter = []
    painter = []
    # location = request_data['location']
    budget = request_data['budget']
    allworker = Worker.find({'Category': 'plumber'},
                            {"_id": 0})
    x = 0
    while True:
        try:
            # if allworker[x]['Price'] == {"$lt": (budget / 100) * 10}:
            #     count = count + 1
            # if allworker[x]['Address'] == location:
            #     count = count + 1
            # similarity = count + getRating(allworker[x]) / 3
            # if similarity > 0:
            plumbers.append(allworker[x])
            x = x + 1
        except:
            break
    allworker = Worker.find({'Category': 'Contractor'},
                            {"_id": 0})
    x = 0
    while True:
        try:
            # if allworker[x]['Price'] == {"$lt": (budget / 100) * 30}:
            #     count = count + 1
            # if allworker[x]['Address'] == location:
            #     count = count + 1
            # similarity = count + getRating(allworker[x]) / 3
            # if similarity > 0:
            contractor.append(allworker[x])
            x = x + 1
        except:
            break
    allworker = Worker.find({'Category': 'Architect'},
                            {"_id": 0})
    x = 0
    while True:
        try:
            # if allworker[x]['Price'] == {"$lt": (budget / 100) * 30}:
            #     count = count + 1
            # if allworker[x]['Address'] == location:
            #     count = count + 1
            # similarity = count + getRating(allworker[x]) / 3
            # if similarity > 0:
            architect.append(allworker[x])
            x = x + 1
        except:
            break
    allworker = Worker.find({'Category': 'electrrician'},
                            {"_id": 0})
    x = 0
    while True:
        try:
            # if allworker[x]['Price'] == {"$lt": (budget / 100) * 10}:
            #     count = count + 1
            # if allworker[x]['Address'] == location:
            #     count = count + 1
            # similarity = count + getRating(allworker[x]) / 3
            # if similarity > 0:
            electricians.append(allworker[x])
            x = x + 1
        except:
            break
    allworker = Worker.find({'Category': 'Carpenter'},
                            {"_id": 0})
    x = 0
    while True:
        try:
            # if allworker[x]['Price'] == {"$lt": (budget / 100) * 10}:
            #     count = count + 1
            # if allworker[x]['Address'] == location:
            #     count = count + 1
            # similarity = count + getRating(allworker[x]) / 3
            # if similarity > 0:
            carpenter.append(allworker[x])
            x = x + 1
        except:
            break
    allworker = Worker.find({'Category': 'Painter'},
                            {"_id": 0})
    x = 0
    while True:
        try:
            # if allworker[x]['Price'] == {"$lt": (budget / 100) * 10}:
            #     count = count + 1
            # if allworker[x]['Address'] == location:
            #     count = count + 1
            # similarity = count + getRating(allworker[x]) / 3
            # if similarity > 0:
            painter.append(allworker[x])
            x = x + 1
        except:
            break

    plumber1 = plumbers[0]
    painters1 = painter[0]
    carpenters1 = carpenter[0]
    contractors1 = contractor[0]
    architects1 = architect[0]
    electrician1 = electricians[0]
    best = electrician1['Price'] + plumber1['Price'] + painters1['Price'] + carpenters1['Price'] + contractors1[
        'Price'] + architects1['Price']
    print(best)
    for a in range(0, len(plumbers), 1):
        for b in range(0, len(electricians), 1):
            for c in range(0, len(contractor), 1):
                for d in range(0, len(architect), 1):
                    for e in range(0, len(carpenter), 1):
                        for f in range(0, len(painter), 1):
                            if request_data['Type'] == 'Type1':
                                cost = plumbers[a]['Price'] + electricians[b]['Price'] + contractor[c]['Price'] + \
                                       architect[d]['Price'] + carpenter[e]['Price'] + painter[f]['Price']
                                if best < cost < int(request_data['budget']):
                                    electrician1 = electricians[b]
                                    plumber1 = plumbers[a]
                                    contractors1 = contractor[c]
                                    architects1 = architect[d]
                                    carpenters1 = carpenter[e]
                                    painters1 = painter[f]
                                    best = cost
                                    print(cost)
                            elif request_data['Type'] == 'Type2':
                                cost = plumbers[a]['Price'] + electricians[b]['Price'] + contractor[c]['Price'] + \
                                       architect[d]['Price'] + carpenter[e]['Price'] + painter[f]['Price']
                                if best < cost < int(request_data['budget']):
                                    electrician1 = electricians[b]
                                    plumber1 = plumbers[a]
                                    contractors1 = contractor[c]
                                    architects1 = architect[d]
                                    carpenters1 = carpenter[e]
                                    painters1 = painter[f]
                                    best = cost

    electrician1['Ratings'] = getRating(electrician1)
    painters1['Ratings'] = getRating(painters1)
    plumber1['Ratings'] = getRating(plumber1)
    architects1['Ratings'] = getRating(architects1)
    contractors1['Ratings'] = getRating(contractors1)
    carpenters1['Ratings'] = getRating(carpenters1)
    workers = [electrician1, plumber1, painters1, architects1, carpenters1, contractors1]
    return jsonify({'ProjectWorker': workers})


@app.route('/embeddedupdate')
@token_required
def update():
    Worker = connection["Worker"]
    Worker.update_one(filter={'NIC': '4210115700899'},
                      update={'$push': {'Date': {'Start': '2018-12-12', 'End': '2018-15-12', 'Project': 3}}})
    return "Hello"


@app.route('/finalizeProject', methods=['POST'])
@token_required
def createproject():
    id = 1
    request_data = request.get_json()
    project = connection['Project']
    projects = project.find().sort([("ID", -1)])
    try:
        id = projects[0]['ID'] + 1
    except:
        id = 1
    project.insert_one(
        {'start': request_data['start'], 'end': request_data['end'], 'budget': request_data['budget'],
         'estimatedBudget': request_data['estimatedBudget'], 'type': request_data['type'],
         'electrician': request_data['electrician'], 'plumber': request_data['plumber'],
         'contractor': request_data['contractor'], 'carpenter': request_data['carpenter'],
         'architect': request_data['architect'], 'painter': request_data['painter'], 'ID': id})
    print(request_data['start'])
    architectstartdate = datetime.strptime(request_data['start'], '%b/%d/%Y')
    contractorstartdate = architectstartdate + timedelta(days=20)
    plumberstartdate = contractorstartdate + timedelta(days=20)
    electricianstartdate = plumberstartdate + timedelta(days=5)
    painterstartdate = electricianstartdate + timedelta(days=3)
    carpenterstartdate = painterstartdate + timedelta(days=2)
    architectenddate = datetime.strptime(request_data['start'], '%b/%d/%Y') + timedelta(days=20)
    contractorenddate = contractorstartdate + timedelta(days=40)
    plumberenddate = plumberstartdate + timedelta(days=25)
    electricianenddate = electricianstartdate + timedelta(days=15)
    painterenddate = painterstartdate + timedelta(days=10)
    carpenterenddate = carpenterstartdate + timedelta(days=10)
    architectstartdate = datetime.strftime(architectstartdate, '%d-%b-%Y')
    architectenddate = datetime.strftime(architectenddate, '%d-%b-%Y')
    contractorstartdate = datetime.strftime(contractorstartdate, '%d-%b-%Y')
    contractorenddate = datetime.strftime(contractorenddate, '%d-%b-%Y')
    carpenterenddate = datetime.strftime(carpenterenddate, '%d-%b-%Y')
    carpenterstartdate = datetime.strftime(carpenterstartdate, '%d-%b-%Y')
    electricianstartdate = datetime.strftime(electricianstartdate, '%d-%b-%Y')
    electricianenddate = datetime.strftime(electricianenddate, '%d-%b-%Y')
    plumberenddate = datetime.strftime(plumberenddate, '%d-%b-%Y')
    plumberstartdate = datetime.strftime(plumberstartdate, '%d-%b-%Y')
    painterenddate = datetime.strftime(painterenddate, '%d-%b-%Y')
    painterstartdate = datetime.strftime(painterstartdate, '%d-%b-%Y')
    Worker = connection["Worker"]
    Worker.update_one(filter={'NIC': request_data['electrician']},
                      update={
                          '$push': {'Date': {'Start': electricianstartdate, 'End': electricianenddate, 'Project': id}}})
    Worker.update_one(filter={'NIC': request_data['plumber']},
                      update={'$push': {'Date': {'Start': plumberstartdate, 'End': plumberenddate, 'Project': id}}})
    Worker.update_one(filter={'NIC': request_data['contractor']},
                      update={
                          '$push': {'Date': {'Start': contractorstartdate, 'End': contractorenddate, 'Project': id}}})
    Worker.update_one(filter={'NIC': request_data['carpenter']},
                      update={'$push': {'Date': {'Start': carpenterstartdate, 'End': carpenterenddate, 'Project': id}}})
    Worker.update_one(filter={'NIC': request_data['architect']},
                      update={'$push': {'Date': {'Start': architectstartdate, 'End': architectenddate, 'Project': id}}})
    Worker.update_one(filter={'NIC': request_data['painter']},
                      update={'$push': {'Date': {'Start': painterstartdate, 'End': painterenddate, 'Project': id}}})
    return jsonify(
        {"architectend": architectenddate, "architectstart": architectstartdate, "carpenterend": carpenterenddate,
         "carpenterstart": carpenterstartdate,
         "contractorend": contractorenddate, "contractorstart": contractorstartdate,
         "electricianend": electricianenddate, "electricianstart": electricianstartdate,
         "message": 'Congratulations Your Project has been created we hope to satisfy you with our services',
         "painterend": painterenddate, "painterstart": painterstartdate,
         "plumberstart": plumberstartdate, "plumberend": plumberenddate})


@app.route('/Login', methods=['POST'])
def x():
    request_data = request.get_json()
    users = connection["Login"]
    login_user = users.find_one({"NIC": request_data['CNIC']})
    Hashpass = hashlib.md5(request_data['Password'].encode()).hexdigest()
    if login_user:
        if login_user['password'] == Hashpass:
            token = jwt.encode(
                {'user': request_data['CNIC'], 'exp': datetime.now() + timedelta(minutes=5)},
                app.config['SECRET_KEY'])
            print(len(token))
            return jsonify({'token': str(token), 'type': 'bachodi'})
    return 'Invalid nic/password'


@app.route('/placeBid', methods=['Post'])
def placebid():
    Id = 1
    request_data = request.get_json()
    Bid = connection['Bids']
    Bid.insert_one({"Need": request_data['need'], "Vendor": request_data['vendor'], "Price": request_data['price'],
                    "Date": datetime.now().date(), "ID": Id})
    return "Bid placed successfully"


@app.route('/removeBid', methods=['Post'])
def removebid():
    request_data = request.get_json()
    bid = connection["Bids"]
    bid.remove({"ID": request_data["ID"]})
    return "Bid removed"


@app.route('/startBid', methods=['POST'])
@token_required
def startbid():
    id = 1;
    request_data = request.get_json()
    needs = connection["Needs"]
    needs.insert_one({"Date": request_data['date'], "Worker": request_data['worker'], "Item": request_data['item'],
                      "End": request_data['end'], "Category": request_data['category'], "ID": id})
    return "Bid Started"


@app.route('/Types', methods=['GET'])
@token_required
def types():
    Types = connection["Type"]
    type = []
    alltypes = Types.find({}, {"_id": 0})
    x = 0
    while True:
        try:
            type.append(alltypes[x])
            x = x + 1
        except:
            break
    return jsonify({"Type": type})


@app.route('/Workerattribute', methods=['Post'])
@token_required
def workerattribute():
    request_data = request.get_json()
    Worker = connection["Worker"]
    worker = Worker.find_one({'NIC': '42101-654541-4', 'Date.Project': 2})
    print(worker)
    Worker.update_one(filter={'NIC': '42101-654541-4', },
                      update={'$set': {'Date.$.Start': '2017-01-01',
                                       'Date.$.End': '2017-08-01',
                                       'Project': 2}
                              }
                      )
    worker = Worker.find_one({'NIC': '42101-654541-4', 'Date.Project': 2})
    print(worker)
    return 'Updated'


@app.route('/workerDetail', methods=['POST'])
# @token_required
def WorkerData():
    request_data = request.get_json()
    Worker = connection["Worker"]
    login_worker = Worker.find_one({"NIC": request_data["CNIC"]}, {'_id': 0})
    if login_worker:
        #        print(login_worker)
        login_worker['Ratings'] = getRating(login_worker)
        return jsonify({"worker": login_worker})
    else:
        return "Worker not found"


# app.run(port=8000, host='192.168.1.105')
app.run(port=8000)
