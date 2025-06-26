import streamlit as st
import streamlit.components.v1 as components
import os
import json
import tempfile
import base64
from datetime import datetime
import io
import wave
import numpy as np

# Try to import Vosk (will work in local environment)
try:
    import vosk
    import soundfile as sf
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

class VoskProcessor:
    """Handles Vosk offline speech recognition"""
    
    def __init__(self, model_path="vosk-model-small-hi-0.22"):
        self.model_path = model_path
        self.model = None
        self.rec = None
        self.initialized = False
    
    def initialize(self):
        """Initialize Vosk model"""
        if not VOSK_AVAILABLE:
            return False, "Vosk not available. Install with: pip install vosk soundfile"
        
        if not os.path.exists(self.model_path):
            return False, f"Model not found at: {self.model_path}"
        
        try:
            self.model = vosk.Model(self.model_path)
            self.rec = vosk.KaldiRecognizer(self.model, 16000)
            self.initialized = True
            return True, "Vosk model initialized successfully"
        except Exception as e:
            return False, f"Error initializing Vosk: {str(e)}"
    
    def process_audio_file(self, audio_data, sample_rate=16000):
        """Process audio file with Vosk"""
        if not self.initialized:
            return False, "Vosk not initialized"
        
        try:
            # Reset recognizer for new audio
            self.rec = vosk.KaldiRecognizer(self.model, sample_rate)
            
            # Process audio in chunks
            results = []
            chunk_size = 4000
            
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                if self.rec.AcceptWaveform(chunk.tobytes()):
                    result = json.loads(self.rec.Result())
                    if result.get("text"):
                        results.append(result["text"])