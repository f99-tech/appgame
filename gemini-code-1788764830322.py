import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(
    page_title="Tom & Jerry: Cheese Dash",
    page_icon="🧀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# 1. إدارة جلسة اللاعب ولوحة الصدارة
# --------------------------------------------------
if "player_name" not in st.session_state:
    st.session_state.player_name = ""

if "leaderboard" not in st.session_state:
    # قائمة افتراضية أولية للمشاركين
    st.session_state.leaderboard = [
        {"name": "سلطان", "score": 1450},
        {"name": "محمد", "score": 1100},
        {"name": "أحمد", "score": 850},
    ]

# استقبال نتائج اللعبة بعد انتهاء الجولة عبر رابط التفاعل
query_params = st.query_params
if "player" in query_params and "score" in query_params:
    try:
        p_name = query_params["player"]
        p_score = int(query_params["score"])
        
        # تجنب التكرار المباشر لنفس النتيجة
        if not any(item["name"] == p_name and item["score"] == p_score for item in st.session_state.leaderboard):
            st.session_state.leaderboard.append({"name": p_name, "score": p_score})
            st.toast(f"🎉 تم تسجيل النتيجة بنجاح للاعب {p_name}: {p_score} نقطة!")
    except:
        pass

# --------------------------------------------------
# 2. الشريط الجانبي (لوحة الصدارة لجميع المشاركين)
# --------------------------------------------------
with st.sidebar:
    st.title("🏆 لوحة المتصدرين")
    st.caption("أعلى نتائج المشاركين في الهروب من توم:")
    
    # ترتيب النتائج من الأعلى إلى الأقل
    sorted_board = sorted(st.session_state.leaderboard, key=lambda x: x['score'], reverse=True)
    
    for idx, item in enumerate(sorted_board[:15], 1):
        medal = "🥇" if idx == 1 else ("🥈" if idx == 2 else ("🥉" if idx == 3 else "🎖️"))
        st.markdown(f"**{medal} #{idx} {item['name']}** — `{item['score']} نقطة`")
    
    st.divider()
    if st.session_state.player_name:
        st.success(f"👤 اللاعب الحالي: **{st.session_state.player_name}**")
        if st.button("تغيير اسم اللاعب 🔄"):
            st.session_state.player_name = ""
            st.rerun()

# --------------------------------------------------
# 3. الواجهة الرئيسية - شاشة التسجيل أو اللعبة
# --------------------------------------------------
st.title("🧀 Tom & Jerry: Cheese Dash")

# إذا لم يقم اللاعب بتسجيل اسمه بعد
if not st.session_state.player_name:
    st.subheader("👋 مرحباً بك! يرجى تسجيل اسمك أولاً للدخول إلى اللعبة:")
    
    with st.form("entry_form"):
        input_name = st.text_input("أدخل اسمك للمشاركة:", max_chars=15, placeholder="مثال: جيري الشجاع")
        submit_btn = st.form_submit_button("بدء اللعبة وتحدي الجميع 🚀")
        
        if submit_btn:
            if input_name.strip() != "":
                st.session_state.player_name = input_name.strip()
                st.rerun()
            else:
                st.warning("يرجى إدخال اسمك أولاً للانضمام للوحة الصدارة.")

else:
    # دخول اللعبة فور تسجيل الاسم
    st.write(f"أهلاً بك **{st.session_state.player_name}**! اجمع الجبن واهرب من **توم**. تجنب العقبات بالقفز أو الانحناء.")

    game_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            background-color: #1a1a2e;
            color: #fff;
            font-family: sans-serif;
            text-align: center;
        }}
        #gameContainer {{
            position: relative;
            width: 800px;
            margin: 10px auto;
        }}
        canvas {{
            background: linear-gradient(to bottom, #1f4068, #162447);
            border: 4px solid #e94560;
            border-radius: 12px;
            box-shadow: 0px 8px 20px rgba(0,0,0,0.5);
        }}
        .controls-info {{
            margin-top: 8px;
            font-size: 14px;
            color: #00fff5;
        }}
        .btn-container {{
            margin-top: 10px;
        }}
        .game-btn {{
            background-color: #e94560;
            color: white;
            border: none;
            padding: 10px 22px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            margin: 0 5px;
        }}
        .game-btn:hover {{
            background-color: #0f3460;
        }}
    </style>
    </head>
    <body>

    <div id="gameContainer">
        <canvas id="canvas" width="800" height="350"></canvas>
        <div class="controls-info">
            🎮 <b>التحكم:</b> استخدم السهم العلوي (↑) أو [Space] للقفز | السهم السفلي (↓) للانحناء
        </div>
        <div class="btn-container">
            <button class="game-btn" onclick="jump()">Jump (قفز)</button>
            <button class="game-btn" onclick="crouch()">Crouch (انحناء)</button>
            <button class="game-btn" style="background-color: #00adb5;" onclick="restartGame()">إعادة اللعب 🔄</button>
        </div>
    </div>

    <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    let playerName = "{st.session_state.player_name}";
    let score = 0;
    let gameOver = false;
    let gameSpeed = 5;
    let frame = 0;

    const floorY = 280;

    let jerry = {{
        x: 250,
        y: floorY - 40,
        width: 35,
        height: 40,
        vy: 0,
        gravity: 0.8,
        jumping: false,
        crouching: false,
        stumbled: false,
        stumbleTimer: 0
    }};

    let tom = {{
        x: 50,
        y: floorY - 70,
        width: 60,
        height: 70
    }};

    let obstacles = [];
    let cheeses = [];

    document.addEventListener('keydown', (e) => {{
        if (e.code === 'ArrowUp' || e.code === 'Space') jump();
        if (e.code === 'ArrowDown') crouch();
    }});

    document.addEventListener('keyup', (e) => {{
        if (e.code === 'ArrowDown') {{
            jerry.crouching = false;
            if (!jerry.jumping) jerry.height = 40;
        }}
    }});

    function jump() {{
        if (!jerry.jumping && !jerry.crouching && !gameOver) {{
            jerry.vy = -13;
            jerry.jumping = true;
        }}
    }}

    function crouch() {{
        if (!jerry.jumping && !gameOver) {{
            jerry.crouching = true;
            jerry.height = 20;
        }}
    }}

    function restartGame() {{
        score = 0;
        gameOver = false;
        gameSpeed = 5;
        frame = 0;
        jerry.x = 250;
        jerry.stumbled = false;
        tom.x = 50;
        obstacles = [];
        cheeses = [];
        animate();
    }}

    function spawnObstacle() {{
        let type = Math.random() > 0.5 ? 'ground' : 'air';
        if (type === 'ground') {{
            obstacles.push({{
                x: canvas.width + 50,
                y: floorY - 35,
                width: 25,
                height: 35,
                type: 'ground'
            }});
        }} else {{
            obstacles.push({{
                x: canvas.width + 50,
                y: floorY - 65,
                width: 30,
                height: 30,
                type: 'air'
            }});
        }}
    }}

    function spawnCheese() {{
        cheeses.push({{
            x: canvas.width + 30,
            y: floorY - 50 - Math.random() * 40,
            width: 20,
            height: 20
        }});
    }}

    function update() {{
        if (gameOver) return;

        frame++;
        score += 1;
        if (frame % 300 === 0) gameSpeed += 0.5;

        jerry.vy += jerry.gravity;
        jerry.y += jerry.vy;

        if (jerry.y >= floorY - jerry.height) {{
            jerry.y = floorY - jerry.height;
            jerry.vy = 0;
            jerry.jumping = false;
        }}

        if (jerry.stumbled) {{
            jerry.stumbleTimer--;
            if (jerry.stumbleTimer <= 0) {{
                jerry.stumbled = false;
            }}
        }} else {{
            if (jerry.x < 250) jerry.x += 0.5;
            if (tom.x > 50) tom.x -= 0.5;
        }}

        if (frame % 120 === 0) spawnObstacle();
        if (frame % 90 === 0) spawnCheese();

        for (let i = 0; i < obstacles.length; i++) {{
            let obs = obstacles[i];
            obs.x -= gameSpeed;

            if (
                jerry.x < obs.x + obs.width &&
                jerry.x + jerry.width > obs.x &&
                jerry.y < obs.y + obs.height &&
                jerry.y + jerry.height > obs.y
            ) {{
                if (!jerry.stumbled) {{
                    jerry.stumbled = true;
                    jerry.stumbleTimer = 60;
                    jerry.x -= 60;
                    tom.x += 40;
                    obstacles.splice(i, 1);
                    i--;

                    if (tom.x + tom.width >= jerry.x) {{
                        endGame();
                    }}
                }}
            }}
        }}

        for (let i = 0; i < cheeses.length; i++) {{
            let ch = cheeses[i];
            ch.x -= gameSpeed;

            if (
                jerry.x < ch.x + ch.width &&
                jerry.x + jerry.width > ch.x &&
                jerry.y < ch.y + ch.height &&
                jerry.y + jerry.height > ch.y
            ) {{
                score += 100;
                cheeses.splice(i, 1);
                i--;
            }}
        }}
    }}

    function endGame() {{
        gameOver = true;
        setTimeout(() => {{
            window.top.location.href = window.top.location.pathname + '?player=' + encodeURIComponent(playerName) + '&score=' + score;
        }}, 1200);
    }}

    function draw() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = '#0f3460';
        ctx.fillRect(0, floorY, canvas.width, canvas.height - floorY);
        ctx.fillStyle = '#e94560';
        ctx.fillRect(0, floorY, canvas.width, 5);

        ctx.fillStyle = '#8e9aaf';
        ctx.fillRect(tom.x, tom.y, tom.width, tom.height);
        ctx.fillStyle = '#ffffff';
        ctx.font = '14px Arial';
        ctx.fillText('🐱 TOM', tom.x + 5, tom.y - 8);

        ctx.fillStyle = jerry.stumbled ? '#ff4d4d' : '#e59866';
        ctx.fillRect(jerry.x, jerry.y, jerry.width, jerry.height);
        ctx.fillStyle = '#ffffff';
        ctx.fillText('🐭 ' + playerName, jerry.x - 5, jerry.y - 8);

        for (let obs of obstacles) {{
            ctx.fillStyle = obs.type === 'ground' ? '#d9534f' : '#f0ad4e';
            ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
            ctx.fillStyle = '#fff';
            ctx.font = '10px Arial';
            ctx.fillText(obs.type === 'ground' ? '⚠️' : '🦅', obs.x + 5, obs.y + 18);
        }}

        for (let ch of cheeses) {{
            ctx.fillStyle = '#f1c40f';
            ctx.beginPath();
            ctx.arc(ch.x + 10, ch.y + 10, 10, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#000';
            ctx.font = '10px Arial';
            ctx.fillText('🧀', ch.x + 2, ch.y + 14);
        }}

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 20px Segoe UI';
        ctx.fillText('النقاط: ' + score, 20, 35);

        if (gameOver) {{
            ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ff4d4d';
            ctx.font = 'bold 36px Segoe UI';
            ctx.fillText('مسكك توم! 😿', canvas.width / 2 - 110, 150);
            ctx.fillStyle = '#ffffff';
            ctx.font = '20px Segoe UI';
            ctx.fillText('مجموع نقاطك: ' + score, canvas.width / 2 - 80, 200);
            ctx.fillText('جاري إضافة النتيجة للوحة الصدارة...', canvas.width / 2 - 160, 240);
        }}
    }}

    function animate() {{
        update();
        draw();
        if (!gameOver) {{
            requestAnimationFrame(animate);
        }}
    }}

    animate();
    </script>
    </body>
    </html>
    """

    components.html(game_html, height=520)