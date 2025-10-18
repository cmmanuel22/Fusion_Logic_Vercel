# api/index.py

import traceback
import sys

try:
    from flask import Flask, request, jsonify
    # CORRECTED IMPORT: Look for fusion_logic in the same (api) directory
    from .fusion_logic import hybrid_fusion, FusionOutput
    from dataclasses import asdict
    import time
    print("INFO: All libraries imported successfully.")
except Exception:
    print("FATAL: A required library is missing. Check requirements.txt.", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)

app = Flask(__name__)

def get_latest_sensor_data_from_supabase():
    print("-> PLACEHOLDER: Fetching latest data from Supabase...")
    mock_data = {
        "audio_risk_level": 1,
        "spo2_percent": 96.5,
        "breathing_rate_bpm": 38
    }
    return mock_data

def save_assessment_to_supabase(result: FusionOutput, inputs: dict):
    print(f"-> PLACEHOLDER: Saving assessment to Supabase...")
    return True

@app.route('/api/assess-risk', methods=['POST'])
def assess_risk_endpoint():
    try:
        print("\nReceived new request to /api/assess-risk")
        sensor_data = get_latest_sensor_data_from_supabase()
        audio_risk = sensor_data.get("audio_risk_level")
        spo2_value = sensor_data.get("spo2_percent")
        bpm = sensor_data.get("breathing_rate_bpm")

        if any(v is None for v in [audio_risk, spo2_value, bpm]):
            return jsonify({"error": "Missing required sensor data"}), 400

        fusion_result = hybrid_fusion(audio_risk, spo2_value, bpm)
        raw_inputs = {'spo2': spo2_value, 'bpm': bpm}
        save_assessment_to_supabase(fusion_result, raw_inputs)
        return jsonify(asdict(fusion_result)), 200
    except Exception:
        print("--- RUNTIME ERROR CAUGHT ---", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        print("--------------------------", file=sys.stderr)
        return jsonify({"error": "A server error occurred. Check Vercel logs."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
