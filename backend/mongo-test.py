from pymongo import MongoClient

uri = "mongodb+srv://devwikiracing.lifgoh4.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='X509-cert-7030048765736591719.pem')
                     #server_api=ServerApi('1'))

db = client['WikiRacing']

users = db['Users']

users.insert_one({'name': 'Vimal', 'score': 50})