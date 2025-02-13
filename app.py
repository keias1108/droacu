from flask import Flask, request, jsonify
import os

app = Flask(__name__)

def calculate_price(width, height):
    base_price = 4180  # 기본 가격

    # 가로 단계 계산
    width_thresholds = [60, 95, 185, 275, 370, 460]
    width_step = sum(1 for w in width_thresholds if width >= w) - 1

    # 세로 단계 계산
    height_thresholds = [40, 55, 105, 155, 210, 260]
    height_step = sum(1 for h in height_thresholds if height >= h) - 1

    # 260mm 초과 시 50mm 단위로 추가 단계 계산 (완료된 구간만)
    if height > 260:
        height_step += (height - 260) // 50

    # 최종 가격 계산 (각 단계에 1을 더하여 곱함)
    return base_price * (width_step + 1) * (height_step + 1)

@app.route('/kakao', methods=['POST'])
def kakao_chatbot():
    """
    카카오 챗봇에서 보내는 JSON에서 'utterance' 값을 추출하여 가격을 계산하고 응답합니다.
    """
    try:
        # JSON 데이터 가져오기
        data = request.get_json(force=True)

        # utterance 값 가져오기 (action -> params -> utterance)
        user_message = data.get('action', {}).get('params', {}).get('utterance', '').replace(" ", "").lower()

        # 유효한 형식인지 확인
        if 'x' not in user_message:
            raise ValueError("형식 오류")

        # 가로, 세로 값 분리
        width_str, height_str = user_message.split('x')
        width = int(width_str)
        height = int(height_str)

        # 가격 계산
        price = calculate_price(width, height)
        response_text = f"{width}mm x {height}mm 가격은 {price:,}원 입니다."

    except Exception as e:
        response_text = "입력 형식이 올바르지 않습니다. (예: 500x500)"
        print(f"오류 발생: {e}")

    # 카카오 챗봇 응답 포맷
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
    port = int(os.environ.get("PORT", 8080))  # 포트 8080으로 고정
    app.run(host="0.0.0.0", port=port)
