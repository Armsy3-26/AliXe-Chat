#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 13:58:57 2022

@author: armsy326
"""

import os
from flask import Flask, request,jsonify,Response
from flask_socketio import SocketIO, emit, send


app = Flask(__name__)
app.config['SECRET_KEY'] = 'terrible secret key'

socketio  = SocketIO(app, cors_allowed_origins="*")

#stores connected devices with there random id's
session_ids  = {}
#will be used to notify users when a managerial system goes online
#user_admin_outreaches has {"client": "restaurant_connected_to"}
user_admin_outreaches = {}

#on connect a session id for the connected client is sent back to the client
@socketio.on('connect')
def onconnect(msg):
    #print(session_ids)
    pass
    
@socketio.on('connection')
def savesessionid(payload):
   
    client_id = request.sid
    
    client_name = payload['sender']
    
    session_ids[client_name] = client_id
    
    request_origin = payload['origin']
        
        
    if request_origin == "user":
        user_admin_outreaches[payload['sender']] = payload['receiver']
        
        try:
            
            #check if receiver is connected to the server
            #if receiver is connected a "user is connected" status is sent back to client(mobile)
            #sender(mobile(client)) emits data to show online status
            receiver_session_id = session_ids[payload['receiver']]
            sender_session_id  = session_ids[payload['sender']]
            connection_payload = {"feedback": f"online"}
            emit('connectionstatus', connection_payload, room=sender_session_id)
            #this connection payload will be sent to management system to show user status
            connection_payload  = {"user": client_name, "status": "online"}
            
            emit('connectionstatus', connection_payload, room=receiver_session_id)
            
        except Exception as e:
            sender_session_id  = session_ids[payload['sender']]
            
            if e.__class__.__name__ == 'KeyError':
                payload = {"feedback": f"offline"}
                emit('connectionstatus', payload, room=sender_session_id)
                
    #admin refering to management system outreach
    elif request_origin == "admin":
        #once online it sends online status to mobile client
        for k,v in user_admin_outreaches.items():
            
            if v == client_name:
                
                #get sid for users connected to the management system
                user_session_id = session_ids[k]
                payload = {"feedback": f"{client_name} is connected."}
                emit('connectionstatus', payload, room=user_session_id)
                
                
        #check if mobile has connected to management outreach while 
        #it was not connected to the serve and emit online status
        try:
            
            for k,v in user_admin_outreaches.items():
                
                if v == client_name:
                    
                    #get sid for the management system connected
                    management_session_id = session_ids[client_name]
                    
                    connection_payload  = {"user": k, "status": "online"}
                    
                    emit('connectionstatus', connection_payload, room=management_session_id)
            
        except Exception:
            pass
                    
        
@socketio.on('message')
def handleMessage(payload):
    
    message  = payload['message']
    try:
        
        receiver_session_id  = session_ids[payload['receiver']]
        
        payload = {"message": message, "sender": payload['sender']}
        
        emit('message', payload, room=receiver_session_id)
    
    except Exception as e:
        #print(payload)
        sender_session_id  = session_ids[payload['sender']]
        
        if e.__class__.__name__ == 'KeyError':
            payload = {"message": 'Last message not sent', "feedback": 'Sent-Status'}
            emit('message', payload, room=sender_session_id)
            
@socketio.on('statusRequest')

def status_request(payload):
    
    client_session_id  = session_ids[payload['sender']]
    
    try:
        
        #use the key if succes , send online status back
        
        session_ids[payload['restrauntName']]
        
        payload = {"status": "online"}
        
        emit('statusRequest', payload, room=client_session_id)
        
    except Exception as e:
        
        if e.__class__.__name__ == 'KeyError':
            payload = {"status": "offline"}
            
            emit('statusRequest', payload, room=client_session_id)
            
        else:
            
            payload = {"status": "connecting..."}
            
            emit('statusRequest', payload, room=client_session_id)
        
    
#send receipts notifications or reservations
@socketio.on('notification')

def notifyReceipt(payload):
    
    try:
        #print(payload)
        receiver_session_id  = session_ids[payload['receiver']]
        
        payload = {"notification": payload['receiptType'] }
        
        emit('notification', payload, room=receiver_session_id)
    
    except Exception as e:
        #print(e)
        pass

#menu update notification, it will be sent to active users in the respesctive restaurants  
menu_users = []
         
@socketio.on('menustatus')
def onMenuUpdate(payload):
    menu_users.clear()
    #get the restaurant name(restaurant which has had it's menu updated)
    restaurant_name = payload['restaurant']
    #print(restaurant_name)
    try:
        for k,v in user_admin_outreaches.items():
            if v == restaurant_name:
                menu_users.append(k)
        
        for k,v in session_ids.items():
            if k in menu_users:
                
                emit("menustatus", payload, room=v)
                
    except Exception  as e:
        pass
        #print("Error occurred on menu update function")

@socketio.on('disconnect')
def ondisconnect():
    #specify clients to get offline using message ids
    disconnected_client = []
    for k,v in list(session_ids.items()):
        
        if v == request.sid:
            disconnected_client.append(k)
            session_ids.pop(k)
            
    if user_admin_outreaches.get(disconnected_client[0]) != None:
        
        if session_ids.get(user_admin_outreaches[disconnected_client[0]]) != None:
            
            receiver_session_id = session_ids[user_admin_outreaches[disconnected_client[0]]]
            #0 status means offline
            connection_payload  = {"user": disconnected_client[0], "status": "offline"}
            
            emit("connectionstatus", connection_payload, room=receiver_session_id)
            
            user_admin_outreaches.pop(disconnected_client[0])
            
    for k,v in user_admin_outreaches.items():
        
        if v == disconnected_client[0]:
            
            #get sid for users connected to the management system
            user_session_id = session_ids[k]
            payload = {"feedback": f"offline"}
            emit('connectionstatus', payload, room=user_session_id)
            
    disconnected_client.clear()
"""
    THE FOLLOWING ARE DEDICATED ROUTES THAT CAN BE USED TO SEND REAL TIME NOTIFICATIONS FROM THE BACKEND.
"""
#create a dedicated route to send receipt notifications from the web
@app.route('/confirm/receipt', methods=['POST'])
def cash_receipt_webhook():
    
    try:
        data = request.get_json()['payload']

        receiver_session_id  = session_ids[data['restaurant']]

        payload = {"notification": 'dinein' }
        
        socketio.emit('notification', payload, room=receiver_session_id)

        return jsonify({"status": "success"})

    except Exception as e:
        
        return jsonify({"status": "error"})
        
#create a dedicated route for payment confirmation
@app.route('/confirm/payment', methods=['POST'])
def payment_webhook():
    
    data = request.get_json()['payload']

    try:
        receiver_session_id  = session_ids[data['restaurant']]
            #data = {"payload": {"receipt_id":receipt_id , "user": username, "amount": get_amount, "restaurant": 'Future Restaurant'}}
        payload = {"payment": {"user": data['user'], "receipt_id": data['receipt_id'],"amount": data['amount']} }
        
        #the emit function is not present in regular flask routes: so must include socketio.emit
        socketio.emit('payment', payload, room=receiver_session_id)
        
        return jsonify({"status": "success"})
    except Exception as e:
        
        return jsonify({"status": "error"})
    
"""    
#tries to restore a conversation
@socketio.on('restore')
def restoreConvo(payload):
    #take in username, which restaurant is being requested and origin as payload
    #send to management have it loop for username
    #send back conversation or no conversation message
    
    if payload['origin'] == "client":
        
        try:
            
            receiver_session_id  = session_ids[payload['requested']]
            
            payload = {"username": payload['username']}
            
            emit('restore', payload, room=receiver_session_id)
        
        except Exception as e:
            #print(payload)
            sender_session_id  = session_ids[payload['username']]
            
            if e.__class__.__name__ == 'KeyError':
                payload = {"status": 'failed'}
                emit('restore', payload, room=sender_session_id)
                
    elif payload['origin'] == "admin":
        
        try:
            
            receiver_session_id  = session_ids[payload['username']]
            
            if payload['status'] == "ok":
                
                payload = {"status":"ok", "conversation":payload['payload']}
                
                emit('restore', payload, room=receiver_session_id)
                
            else:
                payload = {"status":"ok"}
                
                emit('restore', payload, room=receiver_session_id)
                
            
        except Exception:
            pass"""
    

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000)
  



    