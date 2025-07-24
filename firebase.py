import os
import firebase_admin
from firebase_admin import credentials, storage
from main import write_service_account_file
 
# Initialize Firebase app only once
firebase_initialized = False
 
def init_firebase():
    global firebase_initialized
    if not firebase_initialized:
        write_service_account_file()
        #cred_path = os.getenv("FIREBASE_CRED_PATH", "assets/serviceAccountKey.json")
        cred_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Firebase credential file not found at: {cred_path}")
 
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'storageBucket': os.getenv('FIREBASE_BUCKET', 'xenotune-fromx.firebasestorage.app')
        })
        firebase_initialized = True
 
 
def upload_to_firebase(local_file_path: str, firebase_path: str) -> str:
 
    # Ensure Firebase is initialized
    init_firebase()
 
    if not os.path.isfile(local_file_path):
        raise FileNotFoundError(f"❌ File not found: {local_file_path}")
 
    try:
        bucket = storage.bucket()
        blob = bucket.blob(firebase_path)
 
        blob.upload_from_filename(local_file_path)
        blob.make_public()
 
        public_url = blob.public_url
        print(f"✅ Uploaded to Firebase Storage: {public_url}")
        return public_url

    except Exception as e:
        print(f"❌ Failed to upload to Firebase: {e}")
        raise
 
 
if __name__ == "__main__":
    # Example usage with default env settings
    try:
        url = upload_to_firebase('output/music.mp3', 'generated_music/music.mp3')
        print(f"Public URL: {url}")
    except Exception as e:
        print(f"Error: {e}")
 
 