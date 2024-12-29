mport os

def merge_files(file_list, output_file):
    with open(output_file, 'wb') as outfile:
        for file_name in file_list:
            with open(file_name, 'rb') as infile:
                outfile.write(infile.read())
                outfile.write(b"\n")  # Optional: Add a newline between files

# Example usage
file_list = ['suricata.py', 'App.js']
output_file = 'merged_output.txt'  # This will be a binary file with mixed content
merge_files(file_list, output_file)
akarsh@akarsh-VirtualBox:~$ cat merged_output.txt
import json

def monitor_traffic(log_path="/var/log/suricata/eve.json"):
    try:
        with open(log_path, 'r') as log_file:
            for line in log_file:
                data = json.loads(line)
                if data.get('event_type') == 'flow':
                    print(f"Flow detected: {data['src_ip']} -> {data['dest_ip']}")
    except Exception as e:
        print(f"Error reading log: {e}")

if _name_ == "_main_":
    monitor_traffic()

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load dataset (download from CICDDoS2019 and place it in the same folder)
data = pd.read_csv('CICDDoS2019.csv')

# Preprocess the data (remove labels and split data into training and test sets)
X = data.drop(['Label'], axis=1)  
y = data['Label']  

# Split into training and testing datasets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train the Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Test the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save the trained model
import joblib
joblib.dump(model, 'ddos_model.pkl')

#blocking ip
   

import subprocess

def block_ip(ip_address):
    try:
        cmd = f"sudo iptables -A INPUT -s {ip_address} -j DROP"
        subprocess.run(cmd, shell=True, check=True)
        print(f"Blocked IP: {ip_address}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to block IP: {e}")

if _name_ == "_main_":
    malicious_ips = ['192.168.1.100', '192.168.1.101']  # Example IPs
    for ip in malicious_ips:
        block_ip(ip)



from flask import Flask, jsonify
import joblib

app = Flask(_name_)

# Load the pre-trained model
model = joblib.load('ddos_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    traffic_data = [/* traffic data from real-time monitoring */]
    prediction = model.predict([traffic_data])
    
    return jsonify({'prediction': prediction[0]})

if _name_ == "_main_":
    app.run(debug=True)

import React, { useState } from 'react';

function App() {
  const [prediction, setPrediction] = useState(null);

  const checkTraffic = async () => {
    const response = await fetch('/predict', { method: 'POST' });
    const data = await response.json();
    setPrediction(data.prediction);
  };

  return (
    <div>
      <h1>DDoS Protection System</h1>
      <button onClick={checkTraffic}>Check Traffic</button>
      {prediction && <p>Traffic Status: {prediction}</p>}
    </div>
  );
}
export default App;