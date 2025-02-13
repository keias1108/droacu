from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# 종이별 기본 가격 설정
PAPER_PRICES = {
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
def calculate_price(width, height, base_price):
    width_thresholds = [60, 95, 185, 275, 370, 460]
    height_thresholds = [40, 55, 105, 155, 210, 260, 310, 360, 410, 460, 510]

    width_step = sum(1 for w in width_thresholds if width >= w)
    height_step = sum(1 for h in height_thresholds if height >= h)

    price = base_price * (width_step + 1) * (height_step + 1)
    return price

@app.route('/kakao', methods=['POST'])
def kakao_chatbot():
    try:
        data = request.get_json(force=True)
        print("Received Data:", data)  # 디버깅용 데이터 출력

        # ✅ `clientExtra` 또는 `extra`에서 `paper_type` 값 가져오기
        paper_type = data.get('action', {}).get('clientExtra', {}).get('paper_type', '') or \
                     data.get('action', {}).get('extra', {}).get('paper_type', '')

        # ✅ 종이 재질이 선택되지 않았으면 "재질을 먼저 선택해주세요" 메시지 출력
        if not paper_type or paper_type not in PAPER_PRICES:
            return jsonify({
                "version": "2.0",
                "template": {
                    "outputs": [{"simpleText": {"text": "❗️ 먼저 종이를 선택해주세요!"}}]
                }
            })

        # ✅ 사용자가 입력한 사이즈 (300x300, 300*300 등의 형식)
        user_message = data.get('userRequest', {}).get('utterance', '').replace(" ", "").lower()

        # ✅ 정규식으로 사이즈 추출 (x, X, ×, * 모두 허용)
        match = re.match(r"(\d{2,4})[xX×*](\d{2,4})", user_message)
        if not match:
            raise ValueError("형식 오류")

        width, height = int(match.group(1)), int(match.group(2))

        # ✅ 제작 가능 범위 검사
        if width < 60 or width > 530 or height < 40 or height > 530:
            return jsonify({
                "version": "2.0",
                "template": {
                    "outputs": [{"simpleText": {"text": "❌ 해당 사이즈는 제작이 불가능합니다. (가능 범위: 60~530mm x 40~530mm)"}}]
                }
            })

        # ✅ 종이별 가격 가져오기
        base_price = PAPER_PRICES[paper_type]

        # ✅ 최종 가격 계산
        price = calculate_price(width, height, base_price)
        response_text = f"✅ {paper_type} {width}mm x {height}mm 가격은 {price:,}원 입니다."

    except Exception as e:
        print(f"오류 발생: {e}")
        response_text = "⚠️ 입력 형식이 올바르지 않습니다. (예: 500x500)"

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": response_text}}]
        }
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
