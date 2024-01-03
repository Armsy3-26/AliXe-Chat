import requests

data = {"payload": {"receipt_id":'receipt_id' , "user": 'username', "amount": 'get_amount', "restaurant": 'restaurant_name'}}
                
# URL of the Flask-SocketIO app's webhook endpoint
webhook_url = 'http://51.255.62.21:3000/confirm/payment'  # socketio-real time url

# Send the webhook message
response = requests.post(webhook_url, json=data)

# Handle the response from the Flask-SocketIO app (if needed)
print(response.json())