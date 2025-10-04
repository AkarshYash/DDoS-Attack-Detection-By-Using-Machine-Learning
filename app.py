from flask import Flask, render_template
from chatbot.agent import ChatbotAgent
from admin_panel.views import render_admin_dashboard
from employee_panel.views import render_employee_dashboard

app = Flask(__name__)

# Initialize the chatbot agent
chatbot_agent = ChatbotAgent()

@app.route('/')
def home():
    return render_template('chatbot.html')

@app.route('/admin')
def admin():
    return render_admin_dashboard()

@app.route('/employee')
def employee():
    return render_employee_dashboard()

@app.route('/chatbot/respond', methods=['POST'])
def respond_to_query():
    query = request.form['query']
    response = chatbot_agent.respond_to_query(query)
    return {'response': response}

if __name__ == '__main__':
    app.run(debug=True)