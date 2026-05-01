from flask import Flask, render_template, request, redirect, url_for, session
import random
import os

app = Flask(__name__)
# 必須設定 Secret Key 才能使用 session 功能來記住輸入的名字
app.secret_key = os.urandom(24)

# ⭐ PythonAnywhere 部署需要的關鍵變數
application = app

# ===============================
# 題庫設定 (動態帶入使用者設定的名字)
# ===============================
def get_questions(name, name_all):
    return {
        "Q1_choice": {
            "text": f"{name}突然問你：「前女友漂亮，還是我漂亮？」",
            "options": {
                "A": "當然是你好看啦～你眼睛比她大，腿比她好看100倍",
                "B": "前女友？她哪位？我不記得了",
                "C": "你比她可愛",
                "D": "傻瓜，你是我的第一任女友啊"
            },
            "answer": "D",
            "type": "choice"
        },
        "Q2_choice": {
            "text": f"某天你們吵架了，{name}一氣之下叫你走，你會怎麼做？",
            "options": {
                "A": "先離開，等到她冷靜一點再聯絡她",
                "B": "和她好好溝通，搞清楚到底是哪裡出錯了",
                "C": "立刻抱住她，說我錯了，我愛你～",
                "D": "帥氣又瀟灑的，頭也不回，走人！"
            },
            "answer": "C",
            "type": "choice"
        },
        "Q1_1": {
            "text": f"走在街上的時候，你突然鬆開{name}的手，低頭滑起手機。{name}不高興地問：「你在幹嘛？」她真正感到不快的原因是?",
            "required_concepts": [["牽", "手"], ["放", "鬆","開"]],
            "type": "short_answer"
        },
        "Q2_1": {
            "text": f"你買了造型髮箍直接往{name}頭上一戴，開心地說：「嘿嘿~我們一組的～」{name}卻皺起眉。原因是什麼?",
            "required_concepts": [["髮箍"], ["弄亂", "頭","頭髮"]],
            "type": "short_answer"
        },
        "Q2_2": {
            "text": f"你說要幫{name}買食物，轉身就去買了，留下她一個人繼續排隊。她真正生氣的原因是?",
            "required_concepts": [["走掉","丟下"], ["孤獨"], ["一個人","她"]],
            "type": "short_answer"
        },
        "Q3_1": {
            "text": f"你看到前方的女生，立刻揮手喊道：「{name_all}！嗨～～在這裡！」{name}表情有些不自然。為什麼?",
            "required_concepts": [["全名"], ["叫"]],
            "type": "short_answer"
        },
        "Q4_2": {
            "text": f"{name}認真地問：「你愛我嗎？」你回答：「我...真的非常喜歡你。」她表情變了。為什麼?",
            "required_concepts": [["愛"], ["沒有說"]],
            "type": "short_answer"
        }
    }

# ===============================
# 評語字典
# ===============================
FEEDBACK_DICT = {
    "90": [{"short": "哇，你簡直是她的靈魂伴侶！", "long": "你就像她的小心情雷達，能感受到細微波動。記得偶爾給她小驚喜，讓她知道你不只懂她，也願意用心維護關係。"}],
    "60": [{"short": "你有時能猜到她的心思，但還有進步空間。", "long": "愛情就像解謎，你抓到部分線索，但有些女生在意的小細節你漏掉了。多站在她的角度想想吧！"}],
    "0": [{"short": "求生欲警報！你需要多加把勁了。", "long": "觀察她的表情、語氣、動作，慢慢你會抓到更多線索。耐心和細心是你最好的工具。"}],
}

def get_feedback(score):
    if score >= 60: key = "90"
    elif score >= 30: key = "60"
    else: key = "0"
    return random.choice(FEEDBACK_DICT[key])

def score_short_answer(user_answer, qdata):
    if not user_answer: return 0
    score = 0
    total = len(qdata["required_concepts"])
    for group in qdata["required_concepts"]:
        if any(word in user_answer for word in group):
            score += 1
    return (score / total) * 10

# ===============================
# 網頁路由
# ===============================
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        session['name_all'] = request.form.get("name_all") or "劉知珉"
        session['name'] = request.form.get("name") or "Karina"
        return redirect(url_for("question"))
    return render_template("index.html")

@app.route("/question", methods=["GET", "POST"])
def question():
    name = session.get('name', 'Karina')
    name_all = session.get('name_all', '劉知珉')
    questions = get_questions(name, name_all)

    if request.method == "POST":
        score_total = 0
        for qid, qdata in questions.items():
            user_answer = request.form.get(qid, "")
            if qdata["type"] == "choice":
                if user_answer == qdata["answer"]: score_total += 10
            elif qdata["type"] == "short_answer":
                score_total += round(score_short_answer(user_answer, qdata))
        
        feedback = get_feedback(score_total)
        return redirect(url_for("result", score=score_total, short=feedback["short"], long=feedback["long"]))

    return render_template("question.html", questions=questions)

@app.route("/result")
def result():
    return render_template("result.html", 
                           score=request.args.get("score"), 
                           short=request.args.get("short"), 
                           long=request.args.get("long"))

if __name__ == "__main__":
    app.run(debug=True)
