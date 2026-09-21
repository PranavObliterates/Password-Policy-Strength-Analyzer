import hashlib
import time
import os

DICTIONARY_FILE = 'rockyou.txt'

def identify_hash(target_hash):
    length = len(target_hash)
    if length == 32:
        return 'md5'
    elif length == 40:
        return 'sha1'
    elif length == 64:
        return 'sha256'
    elif length == 128:
        return 'sha512'
    else:
        return 'unknown'

def crack_hash(target_hash):
    if not isinstance(target_hash, str):
        target_hash = str(target_hash) if target_hash is not None else ""
    target_hash = target_hash.strip()
    
    algo = identify_hash(target_hash)
    
    if algo == 'unknown':
        return {
            'status': 'Error',
            'algorithm': 'Unknown',
            'cracked': False,
            'details': f"Unsupported hash length ({len(target_hash)})."
        }
        
    target_hash = target_hash.lower()
    start_time = time.time()
    
    cracked_password = None
    
    if os.path.isfile(DICTIONARY_FILE):
        try:
            with open(DICTIONARY_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    word = line.strip()
                    
                    try:
                        # Compute hash
                        if algo == 'md5':
                            computed = hashlib.md5(word.encode('utf-8', errors='ignore')).hexdigest()
                        elif algo == 'sha1':
                            computed = hashlib.sha1(word.encode('utf-8', errors='ignore')).hexdigest()
                        elif algo == 'sha256':
                            computed = hashlib.sha256(word.encode('utf-8', errors='ignore')).hexdigest()
                        elif algo == 'sha512':
                            computed = hashlib.sha512(word.encode('utf-8', errors='ignore')).hexdigest()
                            
                        if computed == target_hash:
                            cracked_password = word
                            break
                    except Exception:
                        pass
        except Exception:
            pass
            
    elapsed_time = time.time() - start_time
    
    if cracked_password:
        return {
            'status': 'Cracked',
            'algorithm': algo.upper(),
            'cracked': True,
            'password': cracked_password,
            'time_taken_sec': round(elapsed_time, 4),
            'details': f"Hash cracked in {round(elapsed_time, 4)} seconds."
        }
    else:
        details = f"Hash survived dictionary attack ({round(elapsed_time, 4)} seconds)."

        return {
            'status': 'Survived',
            'algorithm': algo.upper(),
            'cracked': False,
            'time_taken_sec': round(elapsed_time, 4),
            'details': details
        }
