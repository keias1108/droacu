from flask import Flask, request, jsonify
import os

app = Flask(__name__)

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

        # 1. `utterance` 값이 있는지 확인
        user_message = data.get('action', {}).get('params', {}).get('utterance', '')

        # 2. 또는 `width`와 `height` 개별 파라미터 확인
        width = data.get('action', {}).get('params', {}).get('width', None)
        height = data.get('action', {}).get('params', {}).get('height', None)

        # 3. width & height가 개별적으로 넘어오면 이를 사용
        if width and height:
            width, height = int(width), int(height)
        elif 'x' in user_message:
            width_str, height_str = user_message.replace(" ", "").lower().split('x')
            width, height = int(width_str), int(height_str)
        else:
            raise ValueError("형식 오류")

        # 가격 계산
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
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
