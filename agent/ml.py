import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from utils import logger

MODEL_PATH_TREE = os.path.join(os.path.dirname(__file__), 'local_tree_model.pkl')
SCALER_PATH_TREE = os.path.join(os.path.dirname(__file__), 'local_tree_scaler.pkl')
MODEL_PATH_PROCESS = os.path.join(os.path.dirname(__file__), 'local_process_model.pkl')
SCALER_PATH_PROCESS = os.path.join(os.path.dirname(__file__), 'local_process_scaler.pkl')
MODEL_PATH_FS = os.path.join(os.path.dirname(__file__), 'local_fs_model.pkl')
SCALER_PATH_FS = os.path.join(os.path.dirname(__file__), 'local_fs_scaler.pkl')

class LocalAnomalyDetector:
    def __init__(self):
        self.tree_model = None
        self.tree_scaler = None
        self.process_model = None
        self.process_scaler = None
        self.fs_model = None
        self.fs_scaler = None
        self._load_or_train_models()

    def _load_or_train_models(self):
        # Load or train tree model
        if os.path.exists(MODEL_PATH_TREE) and os.path.exists(SCALER_PATH_TREE):
            try:
                self.tree_model = joblib.load(MODEL_PATH_TREE)
                self.tree_scaler = joblib.load(SCALER_PATH_TREE)
                logger.info(f"Loaded existing tree ML model from {MODEL_PATH_TREE}")
            except Exception as e:
                logger.error(f"Failed to load tree model: {e}. Retraining a fresh baseline.")
                self._train_baseline_tree()
        else:
            self._train_baseline_tree()

        # Load or train process model
        if os.path.exists(MODEL_PATH_PROCESS) and os.path.exists(SCALER_PATH_PROCESS):
            try:
                self.process_model = joblib.load(MODEL_PATH_PROCESS)
                self.process_scaler = joblib.load(SCALER_PATH_PROCESS)
                logger.info(f"Loaded existing process ML model from {MODEL_PATH_PROCESS}")
            except Exception as e:
                logger.error(f"Failed to load process model: {e}. Retraining a fresh baseline.")
                self._train_baseline_process()
        else:
            self._train_baseline_process()
            
        # Load or train FS model
        if os.path.exists(MODEL_PATH_FS) and os.path.exists(SCALER_PATH_FS):
            try:
                self.fs_model = joblib.load(MODEL_PATH_FS)
                self.fs_scaler = joblib.load(SCALER_PATH_FS)
                logger.info(f"Loaded existing fs ML model from {MODEL_PATH_FS}")
            except Exception as e:
                logger.error(f"Failed to load fs model: {e}. Retraining a fresh baseline.")
                self._train_baseline_fs()
        else:
            self._train_baseline_fs()

    def _train_baseline_tree(self):
        logger.info("Training initial baseline IsolationForest model for process trees...")
        # Features: [spawn_count_in_window, total_child_memory_mb, avg_child_memory_mb]
        X_normal = np.random.uniform(low=[0, 0, 0], high=[2, 100, 50], size=(500, 3))
        
        self.tree_scaler = StandardScaler()
        X_scaled = self.tree_scaler.fit_transform(X_normal)
        
        self.tree_model = IsolationForest(contamination=0.01, random_state=42)
        self.tree_model.fit(X_scaled)
        
        joblib.dump(self.tree_model, MODEL_PATH_TREE)
        joblib.dump(self.tree_scaler, SCALER_PATH_TREE)
        logger.info(f"Baseline tree model saved to {MODEL_PATH_TREE}")

    def _train_baseline_process(self):
        logger.info("Training initial baseline IsolationForest model for single processes...")
        # Features: [cpu_percent, memory_mb, num_threads]
        # Realistic desktop normal usage (Browsers, IDEs): up to 20% CPU, 2000MB RAM, 150 threads.
        X_normal = np.random.uniform(low=[0, 0, 1], high=[20, 2000, 150], size=(500, 3))
        
        self.process_scaler = StandardScaler()
        X_scaled = self.process_scaler.fit_transform(X_normal)
        
        self.process_model = IsolationForest(contamination=0.01, random_state=42)
        self.process_model.fit(X_scaled)
        
        joblib.dump(self.process_model, MODEL_PATH_PROCESS)
        joblib.dump(self.process_scaler, SCALER_PATH_PROCESS)
        logger.info(f"Baseline process model saved to {MODEL_PATH_PROCESS}")

    def _train_baseline_fs(self):
        logger.info("Training initial baseline IsolationForest model for File System IO...")
        # Features: [write_rate_mb, write_count_rate, protected_open_files]
        # Realistic desktop normal usage: Background apps do write cache, but rarely hold many protected files OPEN simultaneously.
        # So high write_rate is normal, but high write_rate + protected_files is anomalous.
        X_normal = np.random.uniform(low=[0, 0, 0], high=[500, 10000, 2], size=(500, 3))
        
        self.fs_scaler = StandardScaler()
        X_scaled = self.fs_scaler.fit_transform(X_normal)
        
        self.fs_model = IsolationForest(contamination=0.01, random_state=42)
        self.fs_model.fit(X_scaled)
        
        joblib.dump(self.fs_model, MODEL_PATH_FS)
        joblib.dump(self.fs_scaler, SCALER_PATH_FS)
        logger.info(f"Baseline fs model saved to {MODEL_PATH_FS}")

    def _normalize_score(self, raw_score: float) -> float:
        if raw_score >= 0:
            return 0.0
        return min(abs(raw_score) * 2.0, 1.0)

    def evaluate_tree(self, spawn_count: int, total_memory: float, avg_memory: float) -> float:
        if not self.tree_model or not self.tree_scaler:
            return 0.0
            
        X_test = np.array([[spawn_count, total_memory, avg_memory]])
        X_scaled = self.tree_scaler.transform(X_test)
        raw_score = self.tree_model.decision_function(X_scaled)[0]
        
        if spawn_count >= 4:
            return 0.85
            
        anomaly_score = self._normalize_score(raw_score)
        return float(round(anomaly_score, 2))

    def evaluate_fs(self, write_mb_rate: float, write_count_rate: float, protected_open_files: int) -> float:
        if not self.fs_model or not self.fs_scaler:
            return 0.0
            
        # Hard requirement: If the process isn't touching protected files, it's not a ransomware threat.
        if protected_open_files == 0:
            return 0.0
            
        X_test = np.array([[write_mb_rate, write_count_rate, protected_open_files]])
        X_scaled = self.fs_scaler.transform(X_test)
        raw_score = self.fs_model.decision_function(X_scaled)[0]
        
        # Heuristic boost for ransomware: Rapid file creations in protected user directories
        if write_count_rate >= 2 and protected_open_files >= 3:
            return 0.90
            
        anomaly_score = self._normalize_score(raw_score)
        return float(round(anomaly_score, 2))

    def evaluate_process(self, cpu_percent: float, memory_mb: float, num_threads: int) -> float:
        if not self.process_model or not self.process_scaler:
            return 0.0
            
        X_test = np.array([[cpu_percent, memory_mb, num_threads]])
        X_scaled = self.process_scaler.transform(X_test)
        raw_score = self.process_model.decision_function(X_scaled)[0]
        
        # Heuristic boost: Extremely high resource usage
        if memory_mb > 4096 or num_threads > 500:
            return 0.85
            
        anomaly_score = self._normalize_score(raw_score)
        return float(round(anomaly_score, 2))
