from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.before_request
def redirect_non_https():
    """ HTTP 요청을 HTTPS로 자동 변환하지 않도록 방지 """
    if request.headers.get("X-Forwarded-Proto", "http") == "http":
        return "HTTPS 사용 필요", 400  # 강제로 HTTP 차단

def calculate_price(width, height):
    base_price = 4180  # 기본 가격
    width_thresholds = [60, 95, 185, 275, 370, 460]
    width_step = sum(1 for w in width_thresholds if width >= w) - 1
    height_thresholds = [40, 55, 105, 155, 210, 260]
    height_step = sum(1 for h in height_thresholds if height >= h) - 1

    if height > 260:
        height_step += (height - 260) // 50

    return base_price * (width_step + 1) * (height_step + 1)

@app.route('/kakao', methods=['POST'])
def kakao_chatbot():
    try:
        data = request.get_json(force=True)
        user_message = data.get('action', {}).get('params', {}).get('utterance', '').replace(" ", "").lower()

        if 'x' not in user_message:
            raise ValueError("형식 오류")

        width, height = map(int, user_message.split('x'))
        price = calculate_price(width, height)
        response_text = f"{width}mm x {height}mm 가격은 {price:,}원 입니다."

    except Exception as e:
        response_text = "입력 형식이 올바르지 않습니다. (예: 500x500)"
        print(f"오류 발생: {e}")

    response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": response_text
                    }
                }
            ]
        }
    }
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
