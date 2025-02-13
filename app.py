from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 종이 재질별 가격
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

def calculate_price(width, height, paper_type):
    # 기본 가격 확인 (선택된 종이에 따라)
    base_price = paper_prices.get(paper_type, None)

    if base_price is None:
        return None  # 재질 정보 없음

    width_thresholds = [60, 95, 185, 275, 370, 460]
    height_thresholds = [40, 55, 105, 155, 210, 260, 310, 360, 410, 460, 510]

    width_step = sum(1 for w in width_thresholds if width >= w)
    height_step = sum(1 for h in height_thresholds if height >= h)

    # 최종 가격 계산
    price = base_price * (width_step + 1) * (height_step + 1)
    return price

@app.route('/kakao', methods=['POST'])
def kakao_chatbot():
    try:
        data = request.get_json(force=True)

        # 재질 정보 확인 (컨텍스트에서 가져옴)
        paper_type = data.get("contexts", [{}])[0].get("params", {}).get("paper_type", None)

        if not paper_type:
            return jsonify({
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": "📌 먼저 종이 재질을 선택해주세요!"}}]}
            })

        # 사이즈 입력값 확인
        user_message = data.get('userRequest', {}).get('utterance', '').replace(" ", "").lower()

        if 'x' not in user_message:
            return jsonify({
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": "⚠️ 올바른 형식이 아닙니다. (예: 500x500)"}}]}
            })

        width_str, height_str = user_message.split('x')
        width = int(width_str)
        height = int(height_str)

        # 제한 범위 확인
        if width < 60 or height < 40 or width > 530 or height > 530:
            return jsonify({
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": "⚠️ 해당 사이즈는 제작이 불가능합니다."}}]}
            })

        # 가격 계산
        price = calculate_price(width, height, paper_type)
        if price is None:
            return jsonify({
                "version": "2.0",
                "template": {"outputs": [{"simpleText": {"text": "📌 재질을 먼저 선택해주세요!"}}]}
            })

        # 최종 응답
        response_text = f"✅ {paper_type} {width}mm x {height}mm 가격은 {price:,}원 입니다."
        return jsonify({
            "version": "2.0",
            "template": {"outputs": [{"simpleText": {"text": response_text}}]}
        })

    except Exception as e:
        return jsonify({
            "version": "2.0",
            "template": {"outputs": [{"simpleText": {"text": "⚠️ 오류가 발생했습니다. 다시 시도해주세요."}}]}
        })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
