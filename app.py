from flask import Flask, request, jsonify

app = Flask(__name__)

# 가격 계산 함수
def calculate_price(width, height):
    base_price = 4180
    # 단계 계산 로직
    width_step = min((width - 60) // 80 + 1, 6)  # 가로 최대 6단계
    height_step = min((height - 40) // 50 + 1, 11)  # 세로 최대 11단계
    return base_price * width_step * height_step

# 카카오톡 챗봇 요청 처리
@app.route('/kakao', methods=['POST'])
def kakao_chatbot():
    data = request.json
    user_message = data['userRequest']['utterance']  # 사용자가 입력한 메시지
    
    try:
        # "500x500" 형태로 입력된 메시지 파싱
        width, height = map(int, user_message.split('x'))
        price = calculate_price(width, height)
        response = {
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": f"가로: {width}mm, 세로: {height}mm의 가격은 {price:,}원입니다."
                    }
                }]
            }
        }
    except:
        response = {
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": "입력값이 올바르지 않습니다. 예: 500x500"
                    }
                }]
            }
        }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5000)
