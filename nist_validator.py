import re
import os

DICTIONARY_FILE = 'rockyou.txt'

def validate_password(password):
    if not isinstance(password, str):
        password = str(password) if password is not None else ""
        
    score = 100
    details = []
    
    # 1. Check length > 8
    if len(password) < 8:
        score -= 50
        details.append("Length is less than 8 characters (NIST minimum).")
    elif len(password) >= 15:
        details.append("Good length (15+ characters).")
    else:
        score -= 20
        details.append("Length is acceptable (8+ characters) but 15+ is recommended.")
        
    # 2. Check repetitive, sequential, or low-variance patterns
    unique_chars = len(set(password))
    
    try:
        if re.search(r'(.)\1{2,}', password):
            score -= 30
            details.append("Contains repetitive patterns (e.g., 'aaa').")
        elif unique_chars <= 3 and len(password) >= 6:
            # Catches alternating keyboard smashes like 'abababab' or 'ahahahaha'
            score -= 60
            details.append("Extremely low character variance (predictable pattern or keyboard smash).")
        elif re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            score -= 30
            details.append("Contains predictable sequential characters (e.g., '123' or 'abc').")
    except Exception as e:
        details.append(f"Pattern checking encountered an error: {str(e)}.")
        
    # 3. Check against local dictionary
    in_dictionary = False
    try:
        if os.path.isfile(DICTIONARY_FILE):
            with open(DICTIONARY_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if password == line.strip():
                        in_dictionary = True
                        break
    except Exception as e:
        details.append(f"Could not check dictionary: {str(e)}.")
                    
    # Final score calculation
    if in_dictionary:
        score = 0
        details.append("Password found in dictionary of compromised passwords! Extremely weak.")
    else:
        details.append("Password not found in local compromised dictionary (or dictionary unavailable).")
        
    if len(password) < 8:
        score = min(score, 20)
    
    if unique_chars <= 3 and len(password) >= 6:
        score = min(score, 20)
        
    # Final score adjustment
    score = max(0, min(100, score))
    
    status = "Strong"
    if score < 50:
        status = "Weak"
    elif score < 80:
        status = "Moderate"
        
    return {
        'score': score,
        'status': status,
        'details': details
    }
