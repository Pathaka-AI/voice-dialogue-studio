#!/usr/bin/env python3
"""
FastAPI wrapper for the Neuphonic backend
Provides REST endpoints for the Next.js frontend
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import tempfile
import uvicorn
from pathlib import Path

# Import your existing backend
from neuphonic_backend import NeuphonicBackend

app = FastAPI(
    title="Voice Dialogue Studio API",
    description="REST API for Neuphonic voice dialogue generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize backend
backend = NeuphonicBackend()

# Pydantic models for API
class VoiceCloneRequest(BaseModel):
    voice_name: str
    voice_tags: List[str] = []

class AudioGenerationRequest(BaseModel):
    text: str
    voice_id: str
    speed: float = 1.0
    sampling_rate: int = 22050
    encoding: str = "pcm_linear"

class DialogueGenerationRequest(BaseModel):
    script: str
    voice_mapping: Dict[str, str]
    speed_mapping: Dict[str, float] = {}  # Add speed mapping with default empty dict
    use_longform: bool = False
    sampling_rate: int = 48000
    encoding: str = "pcm_linear"

class VoicePreviewRequest(BaseModel):
    voice_id: str
    text: str = "Hello, this is a voice preview."

# Voice management endpoints
@app.get("/voices")
async def list_voices(cloned_only: bool = False):
    """List all available voices"""
    try:
        voices = backend.list_voices(show_cloned_only=cloned_only)
        return {"voices": voices, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voices/clone")
async def clone_voice(
    audio_file: UploadFile = File(...),
    voice_name: str = Form(...),
    voice_tags: str = Form("[]")
):
    """Clone a voice from an audio sample"""
    try:
        # Parse tags
        tags = json.loads(voice_tags) if voice_tags else []
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Clone the voice
            voice_id = backend.clone_voice(voice_name, temp_file_path, tags)
            
            return {
                "voice_id": voice_id,
                "voice_name": voice_name,
                "status": "success"
            }
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voices/preview")
async def preview_voice(request: VoicePreviewRequest):
    """Generate a voice preview"""
    try:
        # Use longform for reliable preview generation (it's working well)
        audio_file = backend.generate_longform_audio(
            text=request.text,
            voice_id=request.voice_id,
            output_filename=f"preview_{request.voice_id[:8]}.wav",
            speed=1.0  # Normal speed for preview
        )
        
        if audio_file and os.path.exists(audio_file):
            return FileResponse(
                audio_file,
                media_type="audio/wav",
                filename=f"preview_{request.voice_id[:8]}.wav"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate preview")
            
    except Exception as e:
        print(f"❌ Preview generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/voices/{voice_id}")
async def delete_voice(voice_id: str):
    """Delete a cloned voice"""
    try:
        # Note: Your backend doesn't have delete functionality yet
        # This is a placeholder for future implementation
        return {"status": "success", "message": "Voice deletion not yet implemented"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Audio generation endpoints
@app.post("/generate/simple")
async def generate_simple_audio(request: AudioGenerationRequest):
    """Generate audio using SSE (simple/fast mode)"""
    try:
        print(f"🎯 SSE Generation Request: {request.text[:50]}... Speed: {request.speed}")
        
        audio_file = backend.generate_simple_audio(
            text=request.text,
            voice_id=request.voice_id,
            speed=request.speed,  # Pass the speed parameter
            output_filename=f"simple_{request.voice_id[:8]}.wav"
        )
        
        if audio_file and os.path.exists(audio_file):
            print(f"✅ SSE audio generated: {audio_file}")
            return FileResponse(
                audio_file,
                media_type="audio/wav",
                filename=f"simple_{request.voice_id[:8]}.wav"
            )
        else:
            print("❌ SSE generation failed - no audio file created")
            raise HTTPException(status_code=500, detail="SSE generation failed - no audio generated")
            
    except Exception as e:
        print(f"❌ SSE generation error: {e}")
        raise HTTPException(status_code=500, detail=f"SSE generation failed: {str(e)}")

@app.post("/generate/longform")
async def generate_longform_audio(request: AudioGenerationRequest):
    """Generate high-quality audio using longform inference"""
    try:
        audio_file = backend.generate_longform_audio(
            text=request.text,
            voice_id=request.voice_id,
            speed=request.speed,
            output_filename=f"longform_{request.voice_id}.wav"
        )
        
        if audio_file and os.path.exists(audio_file):
            return FileResponse(
                audio_file,
                media_type="audio/wav",
                filename=f"longform_{request.voice_id}.wav"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate longform audio")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/dialogue")
async def generate_dialogue(request: DialogueGenerationRequest):
    """Generate dialogue from script"""
    try:
        # Create a temporary script file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt") as script_file:
            script_file.write(request.script)
            script_file_path = script_file.name
        
        # Update voice mapping
        backend._update_voice_mapping_bulk(request.voice_mapping)
        
        try:
            # Generate the podcast
            output_file = backend.create_podcast_from_script(
                script_file=script_file_path,
                output_filename="dialogue_output.wav",
                use_longform=request.use_longform,
                speed_mapping=request.speed_mapping  # Pass speed mapping
            )
            
            if output_file and os.path.exists(output_file):
                return FileResponse(
                    output_file,
                    media_type="audio/wav",
                    filename="dialogue_output.wav"
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to generate dialogue")
                
        finally:
            # Clean up temp script file
            os.unlink(script_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Utility endpoints
@app.get("/status/{job_id}")
async def check_status(job_id: str):
    """Check generation status (placeholder for async operations)"""
    # This is a placeholder - your current backend is synchronous
    return {"status": "completed", "progress": 100}

@app.get("/download/{job_id}")
async def download_audio(job_id: str):
    """Download generated audio (placeholder)"""
    # This is a placeholder for async download functionality
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Voice Dialogue Studio API is running"}

@app.get("/sample-script")
async def get_sample_script():
    """Get the default sample script"""
    try:
        script_path = Path("script.txt")
        if script_path.exists():
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"script": content, "status": "success"}
        else:
            # Fallback sample script if file doesn't exist
            fallback_script = """<Alex> Welcome to Mysteries of the Mind, I'm Alex, joined as always by my curious co-host Rowan. Today we're diving into one of the most fascinating substances known to science.
<Rowan> And I have to say, I'm really excited about this one. We're talking about D M T, right? The compound that can make fifteen minutes feel like... forever?
<Alex> Exactly. Imagine experiencing what feels like an entire lifetime in just fifteen minutes. That's the reality of D M T, a molecule that's been baffling scientists and challenging our understanding of consciousness for decades.
<Rowan> It's pretty mind bending when you think about it... How can time stretch like that? And this isn't just some new designer drug, is it?
<Alex> Not at all. D M T has actually been used in Amazonian ceremonies for thousands of years. But what's really interesting is how it's now at the center of cutting edge research into consciousness, neuroscience, and even quantum physics."""
            return {"script": fallback_script, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add a helper method to the backend for bulk voice mapping updates
def _update_voice_mapping_bulk(self, voice_mapping: Dict[str, str]):
    """Update voice mapping with multiple entries"""
    mapping = self._load_voice_mapping()
    mapping.update(voice_mapping)
    
    with open(self.voice_mapping_file, 'w') as f:
        json.dump(mapping, f, indent=4)

# Monkey patch the method to the backend
NeuphonicBackend._update_voice_mapping_bulk = _update_voice_mapping_bulk

if __name__ == "__main__":
    print("🚀 Starting Voice Dialogue Studio API server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 Interactive docs at: http://localhost:8000/docs")
    print("🎙️ Frontend should connect to: http://localhost:3000")
    
    uvicorn.run(
        "backend_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 