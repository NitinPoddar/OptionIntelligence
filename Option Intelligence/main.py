########################################################################################
######################          Import packages      ###################################
########################################################################################
from flask import Blueprint, render_template, flash,jsonify,redirect,url_for
from flask import Flask
from flask_login import login_required, current_user,LoginManager
from __init__ import db,create_app
from waitress import serve
#from UserConnection import connect_and_create_websocket
from flask import request
from models import AlgorithmLogic,AlgorithmExecution,Broker_List,AlgoList,User,AlgoRegister,AlgoStatus,InstrumentList,Condition,Option
from sqlalchemy.exc import IntegrityError
#from InteractiveSocketClient import OrderSocket_io
#from Connect import XTSConnect
#from InteractiveSocketClient import OrderSocket_io
import urllib
import json
import requests
import os
#from SmartApi import SmartConnect
#from SmartApi import SmartWebSocket
#import os
########################################################################################
# our main blueprint
main = Blueprint('main', __name__)

instrument_url="https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response=urllib.request.urlopen(instrument_url)
instrument_List=json.loads(response.read())


@main.route('/') # home page that return 'index'
def index():
    return render_template('index.html')

#boxes_data=get_shapes()
@main.route('/profile') # profile page that return 'profile'
@login_required
def profile():
    #algos = AlgoList.query.all()  # Fetch all algorithms from database
    Brokers=Broker_List.query.all()
    #Register = AlgoRegister.query.all()  # Fetch all algorithms from database
    #Status=AlgoStatus.query.all()
    subquery = db.session.query(AlgoRegister).filter(AlgoRegister.user_id == current_user.id).subquery()
    results = db.session.query(
        AlgoList.id,
        AlgoList.AlgoName,
        AlgoStatus.Profit_Percentage,
        AlgoStatus.NumberofSubscribers,
        AlgoStatus.status,
        
        db.func.coalesce(AlgoStatus.status, 'not registered').label('status')
    ).outerjoin(subquery, AlgoList.AlgoName == subquery.c.algo_name
    ).outerjoin(AlgoStatus, subquery.c.id == AlgoStatus.algo_id
    ).order_by(AlgoList.id).all()
                
    boxes_data = [
        {
            'id': result.id,
            'heading': result.AlgoName,
            'subheading1': result.Profit_Percentage,
            'subheading2': result.NumberofSubscribers,
            'status': result.status
        } for result in results
    ]
    print(boxes_data)
    
    broker_data=[
        {
            'BrokerName': Broker.BrokerName
        }for Broker in Brokers
    ]
    print(broker_data)
    return render_template('profile.html',name=current_user.name,boxes=boxes_data,brokers=broker_data)


@main.route('/AlgoRegistrationform', methods=['GET'])
def AlgoRegistrationform():
    return render_template('AlgoRegistrationform.html')
#@main.route('/AlgoRegistrationform', methods=['POST'])
#@main.route('/process_form', methods=['POST'])
#def process_form():
  #  # Handle form submission here if needed
 #   SelectBroker = request.form.get('Algoname')
#    return jsonify({'message': 'Form submitted successfully!', 'SelectBroker': SelectBroker})



@main.route('/add_broker', methods=['GET', 'POST'])
def add_broker():
    if request.method == 'POST':
       BrokerName = request.form['BrokerName']
       RootAPI = request.form['RootAPI']
       ServerIP= request.form['ServerIP']
       PasswordReq= request.form['PasswordReq']
       AuthenticatorReq= request.form['AuthenticatorReq']
       new_broker = Broker_List(BrokerName=BrokerName, RootAPI=RootAPI,ServerIP=ServerIP,PasswordReq=PasswordReq,AuthenticatorReq=AuthenticatorReq)
       db.session.add(new_broker)
       db.session.commit()
       #return redirect(url_for('index'))  # Redirect to homepage or another page
    return render_template('add_broker.html')

@main.route('/add_algo', methods=['GET', 'POST'])
def add_algo():
    if request.method == 'POST':
        algo_name = request.form['AlgoName']
        
        # Check if algorithm with the same name already exists
        existing_algo = AlgoList.query.filter_by(AlgoName=algo_name).first()
        if existing_algo:
            return jsonify({'status': 'error', 'message': 'Algorithm with this name already exists.'})
        # If not, proceed to add the new algorithm
        try:
            minimum_fund_reqd = request.form['Minimum_Fund_Reqd']
            algo_logic = request.form['Algo_logic']
            algo_description = request.form['Algo_description']
            
            new_algo = AlgoList(AlgoName=algo_name, Minimum_Fund_Reqd=minimum_fund_reqd,Algo_description=algo_description,Algo_logic=algo_logic)
            db.session.add(new_algo)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Algorithm added successfully!'})
        except IntegrityError:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'})

    # Render your add_algo.html template for GET requests
    return render_template('add_algo.html')

@main.route('/algo_list', methods=['GET'])
def algo_list():
    algos = AlgoList.query.all()  # Fetch all algorithms from database
    return render_template('algo_list.html', algos=algos) 

@main.route('/edit_algo/<int:id>', methods=['GET', 'POST'])
def edit_algo(id):
    algo = AlgoList.query.get_or_404(id)
    if request.method == 'POST':
        algo.AlgoName = request.form['AlgoName']
        algo.Minimum_Fund_Reqd = request.form['Minimum_Fund_Reqd']
        algo.Algo_logic = request.form['Algo_logic']
        algo.Algo_description = request.form['Algo_description']
        db.session.commit()
        flash('Algorithm updated successfully!', 'success')
        return redirect(url_for('main.algo_list'))
    
    return render_template('edit_algo.html', algo=algo)

@main.route('/delete_algo/<int:id>', methods=['POST'])
def delete_algo(id):
    algo = AlgoList.query.get_or_404(id)
    db.session.delete(algo)
    db.session.commit()
    flash('Algorithm deleted successfully!', 'success')
    
    return redirect(url_for('main.algo_list'))

@main.route('/register_algo', methods=['POST'])
def register_algo():
    if request.method == 'POST':
        user_id=current_user.id
        algo_name = request.form['AlgoName']
        #LotSize = request.form['SelectLotSize']
        broker_name = request.form['SelectBroker']
        BrokerUsername=request.form['BrokerClientID']
        APIKey = request.form['ClientAPIKey']
        SecretKey = request.form['ClientSecretKey']
        status = 'registered'  #
        new_algorithm = AlgoRegister(user_id=user_id, algo_name=algo_name,APIKey=APIKey,SecretKey=SecretKey, broker_name=broker_name,BrokerUsername=BrokerUsername)
        db.session.add(new_algorithm)
        db.session.commit()
        # Update Algostatus table
        new_status = AlgoStatus(algo=new_algorithm, status=status)
        db.session.add(new_status)
        db.session.commit()
        flash('Algorithm registered successfully!', 'success')
        return redirect(url_for('main.profile'))

@main.route('/run_algo', methods=['POST'])
def run_algo():
    
    if request.method == 'POST':
        user_id=current_user.id
        algo_name = request.form['AlgoNameRun']
        algo_info = AlgoRegister.query.filter_by(algo_name=algo_name, user_id=user_id).first()
    
    if algo_info:
        # Construct the response JSON
        response = {
            'secret_key': algo_info.SecretKey,
            'broker_name': algo_info.broker_name,
            'api_key': algo_info.APIKey,
            'BrokerUsername':algo_info.BrokerUsername,
            'AlgoId':algo_info.id
        }
        print(response)
        LotSize = request.form['SelectLotSize']
        Pwd = request.form['Password']
        Authenticator = request.form['Authenticator']
        status_to_edit = AlgoStatus.query.filter_by(algo_id=response['AlgoId']).first()
        if not status_to_edit:
           return jsonify({'error': 'Algo not found for the given user'}), 404
       
        status_to_edit.status = "run"
        status_to_edit.LotSize = LotSize
        db.session.commit() 
        #api_session = requests.Session()
        #try:
        # Make a GET request to the API using the session
        #------------------------------Market Connection---------------#
            #MarketAPI="ecebb11fd01c27761c2d79"
            #MarketSecret="Ifyi021@uz"
            #source="WEBAPI"
            #MarketConnection=XTSConnect(MarketAPI, MarketSecret, source)
            #MarketResponse = api_session.get(MarketConnection.marketdata_login())    
            #ss=connect_and_create_websocket(response['broker_name'],
             #                               response['api_key'],
              #                              response['secret_key'],
               #                             response['BrokerUsername'],
                #                            Pwd,Authenticator)
            #response = api_session.get(ss.interactive_login())
            #print("Login: ", response)
            #response = api_session.get(MarketConnection.get_ohlc(
             #   exchangeSegment="NSECM",
              #  exchangeInstrumentID="NIFTY 50",
               # startTime='Jul 10 2024 091500',
                #endTime='Jul 10 2024 141100',
                #compressionValue=60))
            #print("OHLC: " + str(response))

            
        #except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the API request
         #   return jsonify({'error': str(e)}), 500

        
        #print(ss)
        # Update Algostatus table
        
    return redirect(url_for('main.profile'))
        
@main.route('/get_minimum_fund', methods=['GET'])
def get_minimum_fund():
    algo_name = request.args.get('algo_name')
    algo = AlgoList.query.filter_by(AlgoName=algo_name).first()
    if algo:
        return jsonify({'minimum_fund': algo.Minimum_Fund_Reqd})
    else:
        return jsonify({'error': 'Algo not found'}), 404

@main.route('/BuildAlgo', methods=['GET', 'POST'])
def BuildAlgo():
    unique_names = InstrumentList().query.distinct(InstrumentList.exch_seg).all()
    Segments_Data=[
        {
            'Name': name.exch_seg
        }for name in unique_names
    ]
    print(Segments_Data)    
    if request.method == 'POST':
        lines_of_code = []
        line_count = int(request.form.get('line_count', 0))

        # Collect each line of code from the form
        for i in range(1, line_count + 1):
            line_content = request.form.get(f'line_{i}')
            if line_content.strip():  # Only add non-empty lines
                lines_of_code.append({'line_number': i, 'line_content': line_content})

        # Process each line of code (example: echo each line)
        results = []
        for line in lines_of_code:
            results.append(f"Line {line['line_number']}: {line['line_content']}")

        return render_template('BuildAlgo.html', results=results,Segments=Segments_Data)

    return render_template('BuildAlgo.html')

@main.route('/insert_instruments', methods=['POST'])
def insert_instruments():
    # Clear existing instrument data
    db.session.query(InstrumentList).delete()
    
    # Fetch new instrument data
    instrument_url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    response = urllib.request.urlopen(instrument_url)
    instrument_List = json.loads(response.read())
    
    # Add new instruments to the database
    for instrument_data in instrument_List:
        new_instrument = InstrumentList(
            token=instrument_data['token'],
            symbol=instrument_data['symbol'],
            name=instrument_data['name'],
            expiry=instrument_data['expiry'],
            strike=float(instrument_data['strike']),
            lotsize=int(instrument_data['lotsize']),
            instrumenttype=instrument_data['instrumenttype'],
            exch_seg=instrument_data['exch_seg'],
            tick_size=float(instrument_data['tick_size'])
        )
        db.session.add(new_instrument)

    # Commit the changes to the database
    db.session.commit()
    
    return jsonify({'message': 'Instruments inserted successfully'})

def fetch_instruments():
    instrument_url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    response = urllib.request.urlopen(instrument_url)
    instruments = json.loads(response.read())

    # Create a dictionary to store expiry dates grouped by instrument name
    instrument_dict = {}
    
    for inst in instruments:
        name = inst['name']
        expiry = inst['expiry']
        
        if name not in instrument_dict:
            instrument_dict[name] = set()  # Use a set to avoid duplicates
        instrument_dict[name].add(expiry)  # Add the expiry date to the set

    # Convert the dictionary to a list of dictionaries
    reduced_instruments = [{'name': name, 'expiry': list(expiries)} for name, expiries in instrument_dict.items()]
    
    return reduced_instruments

def save_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def get_instruments():
    file_path = 'instruments.json'

    # Check if the JSON file exists
    if os.path.exists(file_path):
        # Load from the JSON file
        instruments = read_json_file(file_path)
        print("Instruments loaded from JSON file.")
    else:
        # Fetch from the internet and save to the JSON file
        instruments = fetch_instruments()
        save_json_file(file_path, instruments)
        print("Instruments fetched from the internet and saved to JSON file.")
    
    return instruments
    
@main.route('/add_option')
def add_option_form():
    instruments = get_instruments()
    return render_template('add_option.html', instruments=instruments)
    # Get unique indices from the DataFrame for the dropdown
      
    #underlying_indices = index_expiry_df[['index_id', 'index_name']].drop_duplicates().to_dict(orient='records')
    #return render_template('add_option.html', underlying_indices=instrument_List)

@main.route('/submit_option', methods=['POST'])
def submit_option():
    # Get the data from the form
    algorithm = request.form.get('algorithm')
   
    # Retrieve option data
    num_stocks = request.form.getlist('num_stocks[]')
    instrument_names = request.form.getlist('instrument_name[]')
    expiry_dates = request.form.getlist('expiry_date[]')
    strike_prices = request.form.getlist('strike_price[]')
    option_types = request.form.getlist('option_type[]')
    order_types = request.form.getlist('order_type[]')

    # This will hold the entry and exit conditions for each option
    entry_conditions_list = request.form.getlist('entry_condition[]')
    exit_conditions_list = request.form.getlist('exit_condition[]')

    # Prepare to group entry and exit conditions by option
    options = []
    for i in range(len(instrument_names)):
        # Create a new option entry
        option_data = {
            'algorithm': algorithm,
            'num_stocks': num_stocks[i],
            'instrument_name': instrument_names[i],
            'expiry_date': expiry_dates[i],
            'strike_price': strike_prices[i],
            'option_type': option_types[i],
            'order_type': order_types[i],
            'entry_conditions': [],
            'exit_conditions': []
        }

        # Gather entry conditions for this option
        while entry_conditions_list:
            entry_condition = entry_conditions_list.pop(0)  # Get the first entry condition
            option_data['entry_conditions'].append(entry_condition)

        # Gather exit conditions for this option
        while exit_conditions_list:
            exit_condition = exit_conditions_list.pop(0)  # Get the first exit condition
            option_data['exit_conditions'].append(exit_condition)

        options.append(option_data)

    # Process and store the data in the database
    for option in options:
        # Convert conditions to a format suitable for storage (like a JSON string)
        new_option = AlgorithmLogic(
            algorithm=option['algorithm'],
            num_stocks=option['num_stocks'],
            instrument_name=option['instrument_name'],
            expiry_date=option['expiry_date'],
            strike_price=option['strike_price'],
            option_type=option['option_type'],
            order_type=option['order_type'],
            entry_condition=json.dumps(option['entry_conditions']),  # Store as JSON
            exit_condition=json.dumps(option['exit_conditions'])  # Store as JSON
        )
        db.session.add(new_option)

    db.session.commit()  # Don't forget to commit your changes!
    
    flash('Options submitted successfully!', 'success')
    return redirect(url_for('main.add_option_form'))

#@main.route('/add_algo', methods=['GET', 'POST'])
#def add_algo():
#    if request.method == 'POST':
#       AlgoName = request.form['AlgoName']
#       Minimum_Fund_Reqd = request.form['Minimum_Fund_Reqd']
#       Algo_logic= request.form['Algo_logic']
#       try:
#           exec(Algo_logic)  # Execute the Python code (CAUTION: Be mindful of security implications)
#       except Exception as e:
#           return f"Error executing code: {str(e)}"
#       return "Code executed successfully."
 #      new_algo = AlgoList(AlgoName=AlgoName, Minimum_Fund_Reqd=Minimum_Fund_Reqd,Algo_logic=Algo_logic)
       #print(new_algo)
 #      db.session.add(new_algo)
  #     db.session.commit()
   #    flash('Algo added successfully!', 'success')
       #return redirect(url_for('index'))  # Redirect to homepage or another page
    
    #return render_template('add_algo.html')

app = create_app() # we initialize our flask app using the __init__.py function
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # create the SQLite database
    #serve(app,port=50100,threads=2)
    app.run(debug=True,use_reloader=False) # run the flask app on debug mode
