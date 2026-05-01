from flask import Flask, render_template, request, redirect, url_for, session
import random
import os

app = Flask(__name__)
# 設定 Secret Key 以便使用 Session 儲存使用者輸入的名字
app.secret_key = os.urandom(24)

# ⭐ PythonAnywhere 部署需要的變數
application = app

# ===============================
# 題庫與評分邏輯
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
            "text": f"1-1 走在街上的時候，你突然鬆開{name}的手，低頭滑起手機。{name}停下腳步問：「你在幹嘛？」你回：「我在查餐廳在哪裡啊！」她真正感到不快的原因是?",
            "required_concepts": [["牽", "手"], ["放", "鬆","開"]],
            "type": "short_answer"
        },
        "Q2_1": {
            "text": f"2-1 你買了造型髮箍直接往{name}頭上一戴說：「嘿嘿~我們一組的～」{name}卻皺起眉、轉過頭不理你。生氣的原因是?",
            "required_concepts": [["髮箍"], ["弄亂", "頭","頭髮"]],
            "type": "short_answer"
        },
        "Q2_2": {
            "text": f"2-2 你說要幫{name}買食物，轉身就去買了，留下她一個人繼續排隊。她真正生氣的原因是?",
            "required_concepts": [["走掉","丟下"], ["孤獨"], ["一個人","她"]],
            "type": "short_answer"
        },
        "Q2_3": {
            "text": f"2-3 {name}遞給你她的飲料：「想喝一口嗎？」你接過後，用手擦了擦吸管才喝。她不悅的原因是?",
            "required_concepts": [["吸管"], ["口水"], ["嫌", "棄"],["擦"]],
            "type": "short_answer"
        },
        "Q3_1": {
            "text": f"3-1 你看到前面的女生大喊：「{name_all}！嗨～～在這裡！」{name}尷尬地笑笑，表情不太自然。原因是什麼?",
            "required_concepts": [["全名"], ["叫"]],
            "type": "short_answer"
        },
        "Q3_2": {
            "text": f"3-2 你吃完最後一口，問{name}：「欸，你吃完了嗎？」她還在慢慢嚼，眉頭微皺。她不開心的原因是?",
            "required_concepts": [["等"], ["吃飯"], ["耐心"],["催"]],
            "type": "short_answer"
        },
        "Q4_1": {
            "text": f"4-1 回家路上，{name}說：「天色晚了，有點冷耶...」你緊握她的手催促：「快點回家吧！」她卻不高興了。為什麼?",
            "required_concepts": [["直接","沒有留戀","毅然決然","依依不捨"],["挽留"]],
            "type": "short_answer"
        },
        "Q4_2": {
            "text": f"4-2 {name}問：「你愛我嗎？」你回答：「我...真的非常非常喜歡你。」她表情變了。原因是什麼?",
            "required_concepts": [["愛"], ["沒有說"],["喜歡"]],
            "type": "short_answer"
        },
        "Q4_3": {
            "text": f"4-3 你說：「你先走啦。」她回：「不，你先走！」你正氣凜然地轉頭就走。她生氣的原因是?",
            "required_concepts": [["轉頭","轉身"], ["走掉"], ["留戀","毅然決然"]],
            "type": "short_answer"
        }
    }

FEEDBACK_DICT = {
    "90": [
        {"short": "哇，你幾乎抓到她所有的小心思！", "long": "你就像她的小心情雷達，能感受到細微波動。記得偶爾給她小驚喜，讓她知道你不只懂她，也願意用心維護。"}
    ],
    "80": [
        {"short": "你大部分時間能猜到她的心思，偶爾小迷糊也無妨。", "long": "你對她的情緒敏感，能理解她的感受。這讓你們的互動更真實，也有趣味。多留心觀察，你會越來越得心應手。"}
    ],
    "60": [
        {"short": "你有時能猜到她的心思，但也常讓她覺得你心不在焉。", "long": "愛情就像解謎，你抓到部分線索，還需要慢慢探索。多花時間觀察她的表情和語氣，你會發現其實能理解更多。"}
    ],
    "40": [
        {"short": "嗯……她生氣的原因你大概只抓到一半吧？", "long": "別緊張，猜錯很正常。重要的是你有心去理解她。每一次錯誤都是學習的機會，耐心一點。"}
    ],
    "0": [
        {"short": "欸……你完全沒抓到重點喔。", "long": "沒關係，先從觀察和傾聽開始。重點不是猜對，而是你願意關心她的情緒。"}
    ]
}

def get_feedback(score):
    if score >= 90: choices = FEEDBACK_DICT["90"]
    elif score >= 80: choices = FEEDBACK_DICT["80"]
    elif score >= 60: choices = FEEDBACK_DICT["60"]
    elif score >= 40: choices = FEEDBACK_DICT["40"]
    else: choices = FEEDBACK_DICT["0"]
    return random.choice(choices)

def score_short_answer(user_answer, qdata):
    if not user_answer: return 0
    score = 0
    total = len(qdata["required_concepts"])
    for group in qdata["required_concepts"]:
        if any(word in user_answer for word in group):
            score += 1
    return (score / total) * 8  # 簡答題權重設定

# ===============================
# 路由設定
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
                if user_answer == qdata["answer"]:
                    score_total += 10
            elif qdata["type"] == "short_answer":
                s = score_short_answer(user_answer, qdata)
                score_total += round(s)
        
        feedback = get_feedback(score_total)
        return redirect(url_for("result", score=score_total, short=feedback["short"], long=feedback["long"]))

    return render_template("question.html", questions=questions)

@app.route("/result")
def result():
    score = request.args.get("score")
    short = request.args.get("short")
    long = request.args.get("long")
    return render_template("result.html", score=score, short=short, long=long)

if __name__ == "__main__":
    app.run(debug=True)