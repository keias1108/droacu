from flask import Flask, request, jsonify

app = Flask(__name__)

# 종이별 가격 정보
paper_prices = {
    "누브지": 4180,
    "휘라레린넨": 3850,
    "스타드림": 4730,
    "랑데뷰": 3960,
    "컨셉블루": 4070,
    "팝셋": 5940,
    "스코틀랜드백색": 5940,
    "몽블랑백색": 4290
}

# 가격 계산 함수
def calculate_price(width, height, paper_type):
    base_price = paper_prices.get(paper_type, 4180)  # 기본값 누브지
    width_thresholds = [60, 95, 185, 275, 370, 460]
    height_thresholds = [40, 55, 105, 155, 210, 260, 310, 360, 410, 460, 510]

    width_step = sum(1 for w in width_thresholds if width >= w) - 1
    height_step = sum(1 for h in height_thresholds if height >= h) - 1

    if height > 510:
        height_step += (height - 510) // 50 + 1

    final_price = base_price * (width_step + 1) * (height_step + 1)
    return final_price

@app.route('/kakao', methods=['POST'])
def kakao_chatbot():
    data = request.get_json(force=True)
    user_message = data['userRequest']['utterance'].replace(" ", "").lower()
    paper_type = data['action'].get('clientExtra', {}).get('paper_type')

    if not paper_type:
        return jsonify({
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText": {"text": "📢 먼저 종이를 선택해주세요!"}}]
            }
        })

    try:
        width, height = map(int, user_message.split('x'))
        if width < 60 or height < 40 or width > 530 or height > 530:
            response_text = "⚠ 해당 사이즈는 제작이 가능하지 않습니다."
        else:
            price = calculate_price(width, height, paper_type)
            response_text = f"✅ {paper_type} {width}mm x {height}mm 가격은 {price:,}원 입니다."
    except ValueError:
        response_text = "⚠ 올바른 형식이 아닙니다. (예: 500x500)"

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": response_text}}]
        }
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
