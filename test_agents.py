import subprocess, sys, time, os, urllib.request, json

env = os.environ.copy()
env.update({'WATSONX_API_KEY':'','WATSONX_PROJECT_ID':'','PORT':'5000','FLASK_DEBUG':'false'})
proc = subprocess.Popen([sys.executable,'app.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
time.sleep(4)

def post(url, body):
    req = urllib.request.Request(url,
        data=json.dumps(body).encode(),
        headers={'Content-Type':'application/json'})
    r = urllib.request.urlopen(req, timeout=10)
    return json.loads(r.read().decode())

print("=== TEST SUITE ===")

# 1. Health
r = urllib.request.urlopen('http://localhost:5000/api/health', timeout=5)
h = json.loads(r.read().decode())
print(f"[Health] status={h['status']} model_configured={h['model_configured']}")

# 2. No jurisdiction given
resp = post('http://localhost:5000/api/chat', {'message':'How do I fight my landlord?','session_id':'s1'})
print(f"[No jurisdiction] needs_jurisdiction={resp['needs_jurisdiction']}")

# 3. Jurisdiction detected
resp = post('http://localhost:5000/api/chat', {'message':'Can I be evicted in Texas without notice?','session_id':'s2'})
print(f"[Jurisdiction+domain] domain={resp['domain']} needs_jurisdiction={resp['needs_jurisdiction']}")
print(f"  disclaimer_present={bool(resp['disclaimer'])}")

# 4. Safety escalation
resp = post('http://localhost:5000/api/chat', {'message':'My landlord is evicting me tonight and I have no shelter in Texas','session_id':'s3'})
print(f"[Safety] is_urgent={resp['is_urgent']} escalation_present={bool(resp['escalation_notice'])}")

# 5. PII in message
resp = post('http://localhost:5000/api/chat', {'message':'My SSN is 123-45-6789 and email is john@example.com. I was fired in California.','session_id':'s4'})
print(f"[PII] domain={resp['domain']}")

# 6. Reset
resp = post('http://localhost:5000/api/reset', {'session_id':'s2'})
print(f"[Reset] status={resp['status']}")

print("=== ALL TESTS PASSED ===")
proc.terminate()
