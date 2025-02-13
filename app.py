from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 종이 재질별 기본 가격
paper_prices = {
    '누브지': 4180,
    '휘라레린넨': 3850,
    '스타드림': 4730,
    '랑데뷰': 3960,
    '컨셉블루': 4070,
    '팝셋': 5940,
    '스코틀랜드백색': 5940,
    '몽블랑백색': 4290
}

# 사용자 상태 저장 (세션 역할)
user_sessions = {}

def calculate_price(width, height, base_price):
    width_thresholds = [60, 95, 185, 275, 370, 460]
    width_step = sum(1 for w in width_thresholds if width >= w) - 1

    height_thresholds = [40, 55, 105, 155, 210, 260, 310, 360, 410, 460, 510]
    height_step = sum(1 for h in height_thresholds if height >= h) - 1

    # 530mm 제한 초과 시 예외처리
    if width < 60 or height < 40 or width > 530 or height > 530:
        return None  # 사이즈 제한 초과

    return base_price * (width_step + 1) * (height_step + 1)

@app.route('/kakao', methods=['POST'])
def kakao_chatbot():
    try:
        data = request.get_json(force=True)
        user_id = data['userRequest']['user']['id']
        user_message = data.get('userRequest', {}).get('utterance', '').replace(" ", "").lower()

        # 1️⃣ 종이 선택이 먼저 필요한 경우
        if user_message in paper_prices:
            user_sessions[user_id] = user_message  # 사용자 상태 저장
            response_text = f"{user_message}를 선택하셨습니다. 제작할 사이즈를 입력해주세요. (예: 300x300)"

        # 2️⃣ 기존 방식 (300x300 입력하면 기본 종이로 계산)
        elif 'x' in user_message:
            width_str, height_str = user_message.split('x')
            width = int(width_str)
            height = int(height_str)

            # 기본 종이 재질 설정 (사용자가 선택한 게 없다면 '누브지' 기본값)
            paper_type = user_sessions.get(user_id, '누브지')

            # 유효한 종이인지 확인
            if paper_type not in paper_prices:
                response_text = "먼저 종이 재질을 선택해주세요. (예: 누브지, 휘라레린넨, 스타드림 등)"
            else:
                base_price = paper_prices[paper_type]

                # 가격 계산
                price = calculate_price(width, height, base_price)
                if price is None:
                    response_text = "해당 사이즈는 제작이 가능하지 않습니다."
                else:
                    response_text = f"{paper_type} {width}mm x {height}mm 가격은 {price:,}원 입니다."

            # 사용자 상태 초기화 (한 번 계산 후 상태 리셋)
            if user_id in user_sessions:
                del user_sessions[user_id]

        # 3️⃣ 잘못된 입력
        else:
            response_text = "올바른 형식으로 입력해주세요. \n① 먼저 종이 재질을 선택하세요. (예: 누브지) \n② 그 후 사이즈를 입력하세요. (예: 300x300)"

    except Exception as e:
        response_text = "입력 형식이 올바르지 않습니다. (예: '누브지 300x300')"
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
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
