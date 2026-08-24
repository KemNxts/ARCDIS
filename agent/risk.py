class RiskEvaluator:
    @staticmethod
    def evaluate(anomaly_score: float) -> str:
        """
        Translates raw ML anomaly score into a generic risk tier.
        """
        if anomaly_score < 0.5:
            return "LOW"
        elif anomaly_score <= 0.8:
            return "SUSPICIOUS"
        else:
            return "HIGH"
