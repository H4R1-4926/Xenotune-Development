import firebase_admin
from firebase_admin import credentials, storage

# Initialize Firebase app with credentials and storage bucket
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'storageBucket': "xenotune-fromx.appspot.com"})

def upload_to_firebase(local_file_path, firebase_path):
    bucket = storage.bucket()
    blob = bucket.blob(firebase_path)

    # Upload local file to Cloud Storage
    blob.upload_from_filename(local_file_path)

    # Optional: Make the file public (or handle secure token-based access)
    blob.make_public()

    print(f"✅ Uploaded to: {blob.public_url}")
    return blob.public_url

# Example usage
upload_to_firebase('music.mp3', 'generated_music/music.mp3')