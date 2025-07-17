import firebase_admin
from firebase_admin import credentials, storage
import os

# Initialize Firebase app with credentials and storage bucket (initialize only once)
if not firebase_admin._apps:
    cred = credentials.Certificate("assets/serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': "xenotune-fromx.appspot.com"
    })

def upload_to_firebase(local_file_path, firebase_path):
    """Uploads a local file to Firebase Storage and returns its public URL."""
    if not os.path.isfile(local_file_path):
        print(f"❌ File not found: {local_file_path}")
        return None

    bucket = storage.bucket()
    blob = bucket.blob(firebase_path)

    blob.upload_from_filename(local_file_path)
    blob.make_public()

    print(f"✅ Uploaded to Firebase Storage: {blob.public_url}")
    return blob.public_url

# Example usage
if __name__ == "__main__":
    upload_to_firebase('output/music.mp3', 'generated_music/music.mp3')
