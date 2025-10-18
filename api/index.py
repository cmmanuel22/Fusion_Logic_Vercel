# api/index.py

from flask import Flask, request, jsonify
from app.fusion_logic import hybrid_fusion, FusionOutput
from dataclasses import asdict
import time

# --- Initialize Flask App ---
app = Flask(__name__)

# --- ================================================ ---
# --- SUPABASE PLACEHOLDER FUNCTIONS                 ---
# --- ================================================ ---
# --- Replace these functions with your actual Supabase client calls ---

def get_latest_sensor_data_from_supabase():
    """
    PLACEHOLDER: Fetches the latest sensor readings from your Supabase table.
    In reality, you will use the supabase-py library to query your database.
    """
    print("-> PLACEHOLDER: Fetching latest data from Supabase...")
    # This is mock data. Your actual function will run a query.
    # e.g., data = supabase.table('sensor_readings').select('*').order('timestamp', desc=True).limit(1).execute()
    mock_data = {
        "audio_risk_level": 1, # 0="SAFE", 1="MEDIUM", 2="HIGH"
        "spo2_percent": 96.5,
        "breathing_rate_bpm": 38
    }
    return mock_data

def save_assessment_to_supabase(result: FusionOutput, inputs: dict):
    """
    PLACEHOLDER: Saves the final assessment result back to a Supabase table.
    """
    print(f"-> PLACEHOLDER: Saving assessment to Supabase...")
    
    # Prepare the data object to be saved
    record_to_save = {
        "timestamp": time.time(),
        "final_risk": result.final_risk,
        "risk_score": result.risk_score,
        "confidence": result.confidence,
        "reasoning": result.reasoning,
        "spo2_was_critical": result.spo2_was_critical,
        **result.individual_risks, # adds audio, spo2, breathing keys
        "raw_spo2_input": inputs['spo2'],
        "raw_bpm_input": inputs['bpm']
    }
    
    print(f"   Data that would be saved: {record_to_save}")
    # In reality, you'd do:
    # e.g., supabase.table('risk_assessments').insert(record_to_save).execute()
    return True

# --- ================================================ ---
# --- API ENDPOINTS                                  ---
# --- ================================================ ---

@app.route('/api/assess-risk', methods=['POST'])
def assess_risk_endpoint():
    """
    This is the main endpoint that will be called every 30 seconds.
    It gets data, runs the fusion logic, saves the result, and returns it.
    """
    print("\nReceived new request to /api/assess-risk")
    
    # Step 1: Get data from Supabase (using placeholder)
    sensor_data = get_latest_sensor_data_from_supabase()
    
    # Extract values for processing
    audio_risk = sensor_data.get("audio_risk_level")
    spo2_value = sensor_data.get("spo2_percent")
    bpm = sensor_data.get("breathing_rate_bpm")

    # Basic validation
    if any(v is None for v in [audio_risk, spo2_value, bpm]):
        return jsonify({"error": "Missing required sensor data in Supabase record"}), 400

    # Step 2: Run the hybrid fusion logic
    fusion_result = hybrid_fusion(
        audio_risk=audio_risk,
        spo2_value=spo2_value,
        bpm=bpm
    )
    
    # Step 3: Save the assessment result to Supabase (using placeholder)
    raw_inputs = {'spo2': spo2_value, 'bpm': bpm}
    save_assessment_to_supabase(fusion_result, raw_inputs)

    # Step 4: Return the result as JSON to the caller (your dashboard)
    # The dataclasses.asdict function easily converts the result object to a dictionary
    return jsonify(asdict(fusion_result)), 200

# A simple root route to check if the API is running
@app.route('/')
def home():
    return "Asthma Risk Fusion API is running."