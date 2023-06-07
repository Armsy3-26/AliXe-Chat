user_admin_outreaches  = {"Armsy": "restraunt1", "armsy2": "restaurant2", "armsy3": "restaurant3", "fakii": "restraunt1"}

session_ids = {"Armsy": "session_army", "armsy2": "session_army","armsy3": "session_army", "fakii": "session_fakii"}


menu_users = []

def get_payload(payload):

    restaurant_name  = payload['restaurant']

    for k,v in user_admin_outreaches.items():
        if v == restaurant_name:
            menu_users.append(k)
    
    for k,v in session_ids.items():
        if k in menu_users:
            print(v)
            

get_payload({"restaurant": "restraunt1"})