import os
import json
import threading
from flask import Flask, jsonify, render_template
app = Flask(__name__, template_folder="frontend")


# Deriv market symbol
SYMBOL = os.getenv("DERIV_SYMBOL", "1HZ100V")

# Latest market data
market_data = {
    "symbol": SYMBOL,
    "price": None,
    "epoch": None,
    "status": "connecting",
    "signal": "WAIT",
    "trend": "UNKNOWN"
}


def calculate_signal(price):
    """
    Version 1 simple signal engine.
    We will replace this with a stronger strategy later.
    """

    if price is None:
        return "WAIT", "UNKNOWN"

    # Initial version: WAIT until we add candle/indicator analysis.
    return "WAIT", "UNKNOWN"


def on_message(ws, message):
    global market_data

    try:
        data = json.loads(message)

        if data.get("msg_type") == "tick":
            tick = data.get("tick", {})

            price = tick.get("quote")
            epoch = tick.get("epoch")

            signal, trend = calculate_signal(price)

            market_data.update({
                "price": price,
                "epoch": epoch,
                "status": "connected",
                "signal": signal,
                "trend": trend
            })

    except Exception as e:
        market_data["status"] = f"error: {str(e)}"


def on_error(ws, error):
    market_data["status"] = "error"


def on_close(ws, close_status_code, close_msg):
    market_data["status"] = "disconnected"


def on_open(ws):
    market_data["status"] = "connected"

    request = {
        "ticks": SYMBOL,
        "subscribe": 1,
        "req_id": 1
    }

    ws.send(json.dumps(request))


def start_deriv_connection():
    url = "wss://ws.binaryws.com/websockets/v3"

    while True:
        try:
            ws = websocket.WebSocketApp(
                url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )

            ws.run_forever()

        except Exception:
            market_data["status"] = "reconnecting"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/status")
def status():
    return jsonify(market_data)


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "Deriv Analysis Tool"
    })


if __name__ == "__main__":
    thread = threading.Thread(
        target=start_deriv_connection,
        daemon=True
    )
    thread.start()

    port = int(os.getenv("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
 json
