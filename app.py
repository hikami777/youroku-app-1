import requests
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

# Flaskアプリケーションのセットアップ
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key")  # 環境変数から読み込む

# AI21 LabsのAPIキーを設定
AI21_API_KEY = os.environ.get("m2V05g5fjeMVh6TQYcuL5K04hKAO7Tty")

# Flask-Loginのセットアップ
login_manager = LoginManager()
login_manager.init_app(app)

# ユーザーデータ（ここでは簡単に辞書で管理）
users = {"teacher": {"password": "hikaminishi123"}}  # ユーザー名: teacher, パスワード: password123

# ユーザー管理クラス
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# ログイン時に呼ばれるコールバック関数
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# AI21 Labs APIを使ってレポートを生成する関数
def generate_academic_report(attitude, strong_subject, effort, assignment):
    prompt = f"授業態度: {attitude}\n得意科目: {strong_subject}\n努力: {effort}\n課題: {assignment}\n\n以下の情報をもとに、200文字程度の学業評価を生成してください。"

    headers = {
        'Authorization': f'Bearer {AI21_API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        "prompt": prompt,
        "numResults": 1,
        "maxTokens": 150,
        "temperature": 0.7
    }

    # AI21 Labs APIを呼び出してレポート生成
    response = requests.post('https://api.ai21.com/studio/v1/j1-jumbo/complete', headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        print(result)  # レスポンス内容を確認
        report = result['completions'][0]['text'].strip()
        return report
    else:
        print(f"Error: {response.status_code}")
        return "レポート生成に失敗しました。"

# ホームページ
@app.route('/')
def index():
    return render_template('login.html')  # ログインページへリダイレクト

# ログイン処理
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username in users and users[username]['password'] == password:
        user = User(username)
        login_user(user)
        return redirect(url_for('generate_form'))
    return 'Invalid username or password'

# ログイン後、フォームを表示
@app.route('/generate_form')
@login_required
def generate_form():
    return render_template('generate_form.html')

# レポート生成
@app.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    attitude = request.form['attitude']
    strong_subject = request.form['strong_subject']
    effort = request.form['effort']
    assignment = request.form['assignment']

    if not all([attitude, strong_subject, effort, assignment]):
        return "All fields are required!"

    # レポート生成処理
    report = generate_academic_report(attitude, strong_subject, effort, assignment)
    
    # デバッグ情報を設定
    debug_info = f"Attitude: {attitude}\nStrong Subject: {strong_subject}\nEffort: {effort}\nAssignment: {assignment}"

    # レポートとデバッグ情報をresult.htmlに渡す
    return render_template('result.html', report=report, debug_info=debug_info)


# ログアウト処理
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)