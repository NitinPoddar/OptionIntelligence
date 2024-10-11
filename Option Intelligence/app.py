# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 17:50:32 2024

@author: Home
"""

from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/AlgoRegistrationform', methods=['GET'])
def userform():
    return render_template('AlgoRegistrationform.html')

@app.route('/process_form', methods=['POST'])
def process_form():
    username = request.form.get('username')
    # Process username or save data to database
    return jsonify({'message': 'Form submitted successfully!', 'username': username})

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)
