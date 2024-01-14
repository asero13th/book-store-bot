import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase-admin.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

collection_name = "books"
books_collection_ref =  db.collection(collection_name)
docs = books_collection_ref.stream()

for doc in docs:
    data = doc.to_dict()
    print(f'{data["title"]}')
