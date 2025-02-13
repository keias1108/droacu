from flask import Flask, request, jsonify
import math

app = Flask(__name__)

def calculate_price(width, height):
    base_price = 4180  # 기본 가격

    # 가로 단계 계산
    # 기준 데이터: 60, 95, 185, 275, 370, 460
    width_thresholds = [60, 95, 185, 275, 370, 460]
    width_count = 0
    for threshold in width_thresholds:
        if width >= threshold:
            width_count += 1
        else:
            break
    # 가로 단계: 충족한 기준 개수에서 1을 뺀 값 (최소 단계 0)
    width_step = width_count - 1 if width_count > 0 else 0

    # 세로 단계 계산
    # 기준 데이터: 40, 55, 105, 155, 210, 260
    height_thresholds = [40, 55, 105, 155, 210, 260]
    height_count = 0
    for threshold in height_thresholds:
        if height >= threshold:
            height_count += 1
        else:
            break
    height_step = height_count - 1 if height_count > 0 else 0

    # 260mm 초과 시 50mm 단위로 추가 단계 계산 (완료된 구간만)
    if height > height_thresholds[-1]:
        additional_steps = (height - height_thresholds[-1]) // 50
        height_step += additional_steps

    # 최종 가격 계산 (각 단계에 1을 더하여 곱함)
    final_price = base_price * (width_step + 1) * (height_step + 1)
    return final_price

@app.route('/kakao', methods=['POST'])
def kakao_chatbot():
    """
    카카오톡 챗봇 플랫폼에서 전송되는 JSON 구조는
    'userRequest' 내부의 'utterance' 키에 사용자가 입력한 메시지를 포함합니다.
    메시지는 "가로x세로" 형식(공백 제거된 문자열)이어야 합니다.
    """
    try:
        data = request.get_json(force=True)
        user_message = data['userRequest']['utterance']
        # 공백 제거 후 소문자 변환
        user_message = user_message.replace(" ", "").lower()
        if 'x' not in user_message:
            raise ValueError("형식 오류")
        width_str, height_str = user_message.split('x')
        width = int(width_str)
        height = int(height_str)

        price = calculate_price(width, height)
        response_text = f"입력하신 크기 {width}mm x {height}mm 의 가격은 {price:,}원 입니다."
    except Exception:
        response_text = "입력 형식이 올바르지 않습니다. (예: 500x500)"

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
    # 서버 실행: 호스트는 외부 접근 가능하도록 0.0.0.0, 포트는 5000 사용
    app.run(host='0.0.0.0', port=5000, debug=True)
