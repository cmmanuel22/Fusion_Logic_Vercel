# app/fusion_logic.py
# app/fusion_logic.py
# Refreshing the file for Vercel deployment

import numpy as np
from dataclasses import dataclass
# ... rest of your code
import numpy as np
from dataclasses import dataclass
from typing import Dict

# --- Configuration Constants ---
SENSOR_WEIGHTS: Dict[str, float] = {"audio": 1.0, "spo2": 2.5, "breathing": 1.5}
TOTAL_WEIGHT: float = sum(SENSOR_WEIGHTS.values())
RISK_THRESHOLDS: Dict[str, float] = {"safe_max": 0.67, "medium_max": 1.33, "high_min": 1.33}
SPO2_THRESHOLDS: Dict[str, int] = {"high_max": 92, "safe_min": 95}
BREATHING_THRESHOLDS_3_TO_7_YRS: Dict[str, int] = {"safe_max": 34, "medium_max": 40}

# --- Data Structure for the Output ---
@dataclass
class FusionOutput:
    """A structured representation of the fusion system's final assessment."""
    final_risk: str
    risk_score: float
    confidence: float
    reasoning: str
    individual_risks: Dict[str, int]
    spo2_was_critical: bool

# --- Classification Functions ---
def classify_spo2(spo2_value: float) -> int:
    """Classifies SpO2 value into a risk level (0=Safe, 1=Medium, 2=High)."""
    if spo2_value <= SPO2_THRESHOLDS["high_max"]:
        return 2  # High risk
    elif spo2_value < SPO2_THRESHOLDS["safe_min"]:
        return 1  # Medium risk
    else:
        return 0  # Safe

def classify_breathing_rate(bpm: float) -> int:
    """Classifies breathing rate for a 3-7 year old into a risk level."""
    if bpm > BREATHING_THRESHOLDS_3_TO_7_YRS["medium_max"]:
        return 2  # High risk
    elif bpm > BREATHING_THRESHOLDS_3_TO_7_YRS["safe_max"]:
        return 1  # Medium risk
    else:
        return 0  # Safe

# --- Main Fusion Logic ---
def hybrid_fusion(audio_risk: int, spo2_value: float, bpm: float) -> FusionOutput:
    """
    Calculates the final asthma risk by fusing weighted inputs from multiple sensors.
    Includes a critical override for low SpO2.
    """
    # 1. Classify raw sensor values into risk categories (0, 1, 2)
    spo2_risk = classify_spo2(spo2_value)
    breathing_risk = classify_breathing_rate(bpm)
    individual_risks = {"audio": audio_risk, "spo2": spo2_risk, "breathing": breathing_risk}

    # 2. Safety Guardrail: Critical SpO2 overrides all other logic
    if spo2_risk == 2:
        reasoning = "CRITICAL OVERRIDE: SpO2 at or below 92% triggered the safety guardrail."
        return FusionOutput(
            final_risk="HIGH",
            risk_score=2.0,
            confidence=0.95,
            reasoning=reasoning,
            individual_risks=individual_risks,
            spo2_was_critical=True
        )

    # 3. Weighted Fusion Calculation
    weighted_sum = (
        (SENSOR_WEIGHTS["audio"] * audio_risk) +
        (SENSOR_WEIGHTS["spo2"] * spo2_risk) +
        (SENSOR_WEIGHTS["breathing"] * breathing_risk)
    )
    risk_score = weighted_sum / TOTAL_WEIGHT

    # 4. Determine final risk category based on the score
    if risk_score >= RISK_THRESHOLDS["high_min"]:
        final_risk = "HIGH"
    elif risk_score > RISK_THRESHOLDS["safe_max"]:
        final_risk = "MEDIUM"
    else:
        final_risk = "SAFE"

    # 5. Calculate confidence score based on agreement between sensors
    std_dev = np.std(list(individual_risks.values()))
    confidence = max(0.5, 1.0 - (std_dev * 0.5))
    
    reasoning = f"Weighted fusion score of {risk_score:.2f} resulted in a {final_risk} risk assessment."
    
    return FusionOutput(
        final_risk=final_risk,
        risk_score=risk_score,
        confidence=confidence,
        reasoning=reasoning,
        individual_risks=individual_risks,
        spo2_was_critical=False
    )
