import os
import json
import datetime
import logging
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit

# ===============================
# 关闭 werkzeug 默认日志
# ===============================
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # 注意这里也要设置

# ===============================
# stats.json 文件路径
# ===============================
stats_file = 'stats.json'

# ===============================
# 加载和保存每日统计数据
# ===============================
def load_stats():
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            return json.load(f)
    else:
        return {}  # 如果不存在，返回空字典

def save_stats(stats):
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=4)

# ===============================
# 获取今天的统计对象
# ===============================
def get_today_stats(stats):
    today = datetime.date.today().isoformat()
    if today not in stats:
        stats[today] = {
            "previous_kills": 0,
            "previous_hs": 0,
            "total_kills": 0,
            "total_hs": 0
        }
    return stats[today]

# ===============================
# 初始化全局统计
# ===============================
stats = load_stats()

# ===============================
# 存储当前玩家信息
# ===============================
current_player_info = {
    "team": "",
    "health": 0,
    "armor": 0,
    "money": 0,
    "round_kills": 0,
    "round_killhs": 0
}

# ===============================
# 根页面 - HTML界面供OBS显示
# ===============================
@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CS:GO 队伍数据</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: Arial, sans-serif;
                background: transparent;
                color: white;
            }
            
            .data-container {
                padding: 15px;
            }
            
            .team-name {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
                text-align: center;
            }
            
            .human .team-name {
                color: #3498db;
            }
            
            .zombie .team-name {
                color: #e74c3c;
            }
            
            .stat-row {
                display: flex;
                align-items: center;
                font-size: 16px;
                line-height: 1.3;
                margin-bottom: 6px;
            }
            
            .stat-label {
                font-weight: bold;
                width: 90px;
            }
            
            .stat-value {
                font-weight: bold;
            }
            
            .health-value {
                color: #2ecc71;
            }
            
            .armor-value {
                color: #3498db;
            }
            
            .money-value {
                color: #f1c40f;
            }
            
            .kills-value {
                color: #e74c3c;
            }
            
            .hs-value {
                color: #9b59b6;
            }
            
            .no-data {
                color: #ccc;
                font-size: 14px;
                text-align: center;
                padding: 20px;
            }
        </style>
    </head>
    <body>
        <div id="dataDisplay" class="data-container">
            <div class="no-data">等待游戏数据...</div>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>
        <script>
            // 连接到WebSocket服务器
            const socket = io();
            
            function updateDisplay(data) {
                const container = document.getElementById('dataDisplay');
                
                if (data.team === '人类') {
                    container.className = 'data-container human';
                    container.innerHTML = `
                        <div class="team-name">${data.team}</div>
                        <div class="stat-row">
                            <span class="stat-label">血量:</span>
                            <span class="stat-value health-value">${data.health}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">金钱:</span>
                            <span class="stat-value money-value">$${data.money}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">回合击杀:</span>
                            <span class="stat-value kills-value">${data.round_kills}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">回合爆头:</span>
                            <span class="stat-value hs-value">${data.round_killhs}</span>
                        </div>
                    `;
                } else if (data.team === '僵尸') {
                    container.className = 'data-container zombie';
                    container.innerHTML = `
                        <div class="team-name">${data.team}</div>
                        <div class="stat-row">
                            <span class="stat-label">血量:</span>
                            <span class="stat-value health-value">${data.health}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">护甲:</span>
                            <span class="stat-value armor-value">${data.armor}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">金钱:</span>
                            <span class="stat-value money-value">$${data.money}</span>
                        </div>
                    `;
                } else {
                    container.className = 'data-container';
                    container.innerHTML = '<div class="no-data">等待游戏数据...</div>';
                }
            }
            
            // 监听服务器推送的数据更新
            socket.on('player_update', function(data) {
                updateDisplay(data);
            });
            
            // 页面加载时获取初始数据
            document.addEventListener('DOMContentLoaded', () => {
                fetch('/current_info')
                    .then(response => response.json())
                    .then(data => {
                        updateDisplay(data);
                    })
                    .catch(error => {
                        console.error('获取初始数据失败:', error);
                    });
            });
        </script>
    </body>
    </html>
    """

# ===============================
# /stats 路由，获取每日统计（供OBS等外部调用）
# ===============================
@app.route("/stats")
def get_stats():
    today_stats = get_today_stats(stats)
    save_stats(stats)  # 确保文件更新
    
    # 添加CORS响应头，允许OBS浏览器源访问
    response = jsonify(today_stats)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    
    return response

# ===============================
# /current_info 路由，获取当前玩家信息
# ===============================
@app.route("/current_info")
def get_current_info():
    response = jsonify(current_player_info)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# ===============================
# /game_state 路由，接收 GSI 数据
# ===============================
@app.route("/game_state", methods=["POST"])
def game_state():
    data = request.get_json()
    
    today_stats = get_today_stats(stats)

    # 提取玩家信息
    player_state = data.get('player', {}).get('state', {})
    
    if data['player']['team'] == 'CT':
        team = '人类'
        
        # 处理人类队伍的统计
        current_kills = player_state.get('round_kills', 0)
        current_hs = player_state.get('round_killhs', 0)

        # 增量计算，避免重复累加
        kills_delta = max(current_kills - today_stats["previous_kills"], 0)
        hs_delta = max(current_hs - today_stats["previous_hs"], 0)

        today_stats["total_kills"] += kills_delta
        today_stats["total_hs"] += hs_delta

        # 更新前一次回合的击杀数
        today_stats["previous_kills"] = current_kills
        today_stats["previous_hs"] = current_hs
        
        # 更新当前玩家信息（人类）
        current_player_info.update({
            "team": team,
            "health": player_state.get('health', 0),
            "armor": player_state.get('armor', 0),
            "money": player_state.get('money', 0),
            "round_kills": current_kills,
            "round_killhs": current_hs
        })

    elif data['player']['team'] == 'T':
        team = '僵尸'
        
        # 更新当前玩家信息（僵尸）
        current_player_info.update({
            "team": team,
            "health": player_state.get('health', 0),
            "armor": player_state.get('armor', 0),
            "money": player_state.get('money', 0),
            "round_kills": 0,
            "round_killhs": 0
        })

    # 通过WebSocket实时推送数据到所有客户端
    socketio.emit('player_update', current_player_info)

    save_stats(stats)  # 保存统计数据

    return "OK", 200

# ===============================
# /reset_stats 路由（可选）：重置今日统计
# ===============================
@app.route("/reset_stats")
def reset_stats():
    today = datetime.date.today().isoformat()
    stats[today] = {
        "previous_kills": 0,
        "previous_hs": 0,
        "total_kills": 0,
        "total_hs": 0
    }
    save_stats(stats)
    response = jsonify({"message": "今日统计已重置", "stats": stats[today]})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# ===============================
# 启动 Flask + SocketIO
# ===============================
if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=3000, debug=False)