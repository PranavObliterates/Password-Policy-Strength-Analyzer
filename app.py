from flask import Flask, render_template, request, jsonify, Response
from nist_validator import validate_password
from hash_cracker import crack_hash
from database import init_db, log_audit, get_all_logs
import csv
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 # 1MB limit

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    logs = get_all_logs()
    return render_template('admin.html', logs=logs)

@app.route('/admin/export')
def admin_export():
    logs = get_all_logs()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Timestamp', 'Audit Type', 'Result JSON'])
    for log in logs:
        cw.writerow([log.get('id'), log.get('timestamp'), log.get('audit_type'), log.get('result_json')])
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=audit_logs.csv"}
    )

@app.route('/api/audit', methods=['POST'])
def audit():
    data = request.json or {}
    input_type = data.get('type')
    val = data.get('value')
    input_value = str(val) if val is not None else ''
    
    if not input_type or not input_value:
        return jsonify({'error': 'Missing type or value'}), 400
        
    if len(input_value) > 1000:
        return jsonify({'error': 'Input value exceeds maximum length of 1000 characters'}), 400
        
    result = {}
    
    try:
        if input_type == 'plaintext':
            result = validate_password(input_value)
        elif input_type == 'hash':
            result = crack_hash(input_value)
        else:
            return jsonify({'error': 'Invalid type'}), 400
            
        # Log the audit
        log_audit(input_type, result)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
