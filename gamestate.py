@app.route("/game_state", methods=["POST"])
def game_state():
    try:
        # 获取请求中的 JSON 数据
        data = request.get_json()
        print("Received data:", data)  # 记录收到的数据

        if data is None:
            print("No JSON data received")  # 如果没有接收到数据
            return "No JSON data received", 400  # 返回错误信息

        print(json.dumps(data, indent=4))  # 打印接收到的数据到控制台

        # 将数据通过 WebSocket 推送到前端
        socketio.emit('game_state_update', data)

        return "OK", 200
    except Exception as e:
        print(f"Error: {e}")  # 打印错误
        return str(e), 500  # 返回错误信息
