import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask, jsonify, request
import random
import requests
import string
from flask_cors import CORS


cred = credentials.Certificate('serviceKey.json')

firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
CORS(app)

api_key_correct = False

main_collection = db.collection('users')
from flask import request, jsonify



@app.route("/create_readme", methods=["POST"])
def create_readme():
    
    username = request.form.get('name')
    tone = request.form.get('tone')
    repo_url = request.form.get('repo_url')
    description = request.form.get('description')
    github_token = request.form.get('github_token')
    auth_header = request.headers.get('Authorization')
    if auth_header:
        print("Authorization header found:", auth_header)  # Debug print
        if auth_header.startswith('Bearer '):
            api_key = auth_header.split('Bearer ')[1]
            
            response = check_api_key(username,api_key)
            if "api_key" in response:
        # The JSON contains a key called "api_key"
                api_key_value = response["api_key"]
                endpoint = "http://127.0.0.1:5000/create_readme"

                payload = {
                    "repo_url": repo_url,
                    "tone": tone,
                    "description": description,
                    "github_token": github_token,
                }
                response = requests.post(endpoint, json=payload)
        
                return response
            else:
                # The JSON does not contain a key called "api_key"
                print("API Key not found in JSON")
            return response
        else:
            return jsonify({"message": "Authorization header format invalid"}), 401
    else:
        return jsonify({"message": "Authorization header missing"}), 401



# ======================================================================================




@app.route("/analyse_code", methods=["POST"])
def code_analysis():
    
    username = request.form.get('name')
    
    code = request.form.get('code')
    auth_header = request.headers.get('Authorization')
    if auth_header:
        print("Authorization header found:", auth_header)  # Debug print
        if auth_header.startswith('Bearer '):
            api_key = auth_header.split('Bearer ')[1]
            
            response = check_api_key(username,api_key)
            if "api_key" in response:
        # The JSON contains a key called "api_key"
                api_key_value = response["api_key"]
                endpoint = "http://127.0.0.1:5000/analyse_code"

                payload = {
                    "code": code
                }
                response = requests.post(endpoint, json=payload)
        
                return response
            else:
                # The JSON does not contain a key called "api_key"
                print("API Key not found in JSON")
            return response
        else:
            return jsonify({"message": "Authorization header format invalid"}), 401
    else:
        return jsonify({"message": "Authorization header missing"}), 401

# ======================================================================================




@app.route("/get_social_media_post", methods=["POST"])
def get_social_media_post():
    
    username = request.form.get('name')
    repo_url = request.form.get('repo_url')
    tone = request.form.get('tone')
    description = request.form.get('description')
    github_token = request.form.get('github_token')
    auth_header = request.headers.get('Authorization')
    if auth_header:
        print("Authorization header found:", auth_header)  # Debug print
        if auth_header.startswith('Bearer '):
            api_key = auth_header.split('Bearer ')[1]
            
            response = check_api_key(username,api_key)
            if "api_key" in response:
        # The JSON contains a key called "api_key"
                api_key_value = response["api_key"]
                endpoint = "http://127.0.0.1:5000/get_social_media_post"

                payload = {
                    "repo_url": repo_url,
                    "tone": tone,
                    "description": description,
                    "github_token": github_token,
                }
                response = requests.post(endpoint, json=payload)
        
                return response
            else:
                # The JSON does not contain a key called "api_key"
                print("API Key not found in JSON")
            return response
        else:
            return jsonify({"message": "Authorization header format invalid"}), 401
    else:
        return jsonify({"message": "Authorization header missing"}), 401
    
    # ==================================================================



def generate_api_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

@app.route('/generate_api_key', methods=['GET'])
def generate_and_store_api_key():
    username = request.args.get('name') 
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    api_key = generate_api_key()
    
    # Find the user document by username
    user_doc = main_collection.where('name', '==', username).stream() 
    user_doc_ref = None
    for doc in user_doc:
        user_doc_ref = doc.reference
        
    
    if not user_doc_ref:
        return jsonify({'error': 'User not found'}), 404
    
    
    api_keys_subcollection = user_doc_ref.collection('api-keys')
    api_keys_subcollection.add({'api_key': api_key})
    
    return jsonify({'api_key': api_key})


def check_api_key(username, api_key):

    if not username or not api_key:
        return jsonify({'error': 'Both username and API key are required'}), 400

    
    user_doc = main_collection.where('name', '==', username).stream()
    user_doc_ref = None
    for doc in user_doc:
        user_doc_ref = doc.reference
        

    if not user_doc_ref:
        return jsonify({'error': 'User not found'}), 404

    
    api_keys_subcollection = user_doc_ref.collection('api-keys')
    api_key_docs = api_keys_subcollection.where('api_key', '==', api_key).stream()

    
    if not api_key_docs:
        
        return jsonify({'error': 'API key not found'}), 404

    
    for doc in api_key_docs:
        api_key_correct = True
        return jsonify(doc.to_dict()), 200

    return jsonify({'error': 'An unexpected error occurred'}), 500

def delete_api_key(username, api_key):
    

    if not username or not api_key:
        return jsonify({'error': 'Both username and API key are required'}), 400

    
    user_doc = main_collection.where('name', '==', username).stream()
    user_doc_ref = None
    for doc in user_doc:
        user_doc_ref = doc.reference
        

    if not user_doc_ref:
        return jsonify({'error': 'User not found'}), 404

    
    api_keys_subcollection = user_doc_ref.collection('api-keys')
    api_key_docs = api_keys_subcollection.where('api_key', '==', api_key).stream()

    
    if not api_key_docs:
        return jsonify({'error': 'API key not found'}), 404

    
    for doc in api_key_docs:
        doc.reference.delete()
        return jsonify({'message': 'API key successfully deleted'})

    return jsonify({'error': 'An unexpected error occurred'}), 500


if __name__ == '__main__':
    
    app.run(debug=True)


