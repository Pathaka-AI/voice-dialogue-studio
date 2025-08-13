# Voice Dialogue Studio 🎙️

[![GitHub](https://img.shields.io/github/license/Pathaka-AI/voice-dialogue-studio)](https://github.com/Pathaka-AI/voice-dialogue-studio/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Pathaka-AI/voice-dialogue-studio)](https://github.com/Pathaka-AI/voice-dialogue-studio/stargazers)

**AI-powered voice dialogue generation with Neuphonic API.** A complete solution featuring voice cloning, multi-speaker TTS, parallel processing, and comprehensive testing tools.

## 🌟 Features

### 🎨 **Modern Web Interface**
- **Next.js 15.4** frontend with responsive design
- **Real-time generation timer** with performance tracking
- **Speed controls** for individual voices (0.7x - 2.0x)
- **Language filtering** and voice management
- **Preset downloads** for testing and reproducibility

### ⚡ **Advanced Generation**
- **Parallel Processing**: 66% faster longform generation
- **Two Quality Modes**: SSE (fast, 22kHz) vs Longform (studio, 48kHz)
- **Multi-speaker dialogue** with automatic voice assignment
- **Custom speed per speaker** for natural conversations

### 🔒 **Production Ready**
- **Secure API key management** via environment variables
- **Comprehensive audio file exclusion** (no large files in repo)
- **Automated setup scripts** for one-command deployment
- **Error handling and validation** throughout

### 🎛️ **Voice Management**
- **Voice cloning** from audio samples
- **Voice library** with preview capabilities
- **Language support** with filtering
- **Voice mapping** persistence

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/Pathaka-AI/voice-dialogue-studio.git
cd voice-dialogue-studio

# Copy environment configuration
cp .env.example .env
# Edit .env and add your Neuphonic API key
```

### 2. Install Dependencies
```bash
# Python dependencies
pip install -r requirements-api.txt

# Node.js dependencies  
npm install --legacy-peer-deps
```

### 3. Configure API Key
```bash
# Option 1: Set environment variable
export NEUPHONIC_API_KEY='your_neuphonic_api_key_here'

# Option 2: Add to .env file
echo "NEUPHONIC_API_KEY=your_neuphonic_api_key_here" >> .env
```

### 4. Start the Application
```bash
# One-command startup (recommended)
./start.sh

# Or manually:
# Terminal 1: Start backend
python3 backend_api.py

# Terminal 2: Start frontend
npm run dev
```

### 5. Access the Interface
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📝 Script Format

Create multi-speaker dialogues using this format:

```
<Alex> Welcome to Mysteries of the Mind, I'm Alex, joined as always by my curious co-host Rowan.
<Rowan> Thanks Alex! Today we're diving into one of the most fascinating substances known to science.
<Alex> That's right, we're talking about DMT - the compound that can make fifteen minutes feel like forever.
```

## 🎛️ Interface Guide

### **Script Input**
- Paste or type your dialogue script
- Real-time speaker detection and statistics
- Script validation and helpful tips

### **Voice Assignment**
- Automatic voice mapping for Alex/Rowan
- Speed controls per speaker (0.7x - 2.0x)
- Language filtering for voice selection
- Voice preview functionality

### **Quality Settings**
- **Speed**: SSE mode (22kHz, fast)
- **Highest Quality**: Longform mode (48kHz, studio quality)
- **Parallel Processing**: 66% faster longform generation
- Advanced sampling rate and encoding controls

### **Generation & Download**
- Real-time timer during generation
- Audio player with download capability
- **Preset download**: Complete generation settings for testing
- Performance metrics and processing method display

## 📊 Testing & Performance

### **Preset Downloads**
Every generation creates a downloadable preset containing:
- Complete script and speaker information
- Voice mappings and speed settings
- Quality configuration and performance data
- Timing metrics for method comparison

Example preset filename: `voice-preset_2024-01-15_Longform_Parallel_45-7s.json`

### **Performance Comparison**
- **Sequential Longform**: Reliable but slower
- **Parallel Longform**: 66% speed improvement
- **SSE**: Fastest for shorter content

## 🏗️ Architecture

### **Backend (Python)**
- **`neuphonic_backend.py`**: Core Neuphonic API integration
- **`backend_api.py`**: FastAPI REST wrapper
- **Voice cloning, TTS generation, and audio processing**

### **Frontend (Next.js)**
- **`app/page.js`**: Main interface component
- **`app/components/ScriptUploader.js`**: Script input and parsing
- **`app/lib/api.js`**: API integration utilities

### **Configuration**
- **`.env`**: Environment variables (API keys)
- **`voice_mapping.json`**: Speaker to voice ID mappings
- **`script.txt`**: Default sample script

## 🔧 API Endpoints

The FastAPI backend provides:

- `GET /voices` - List available voices
- `POST /voices/clone` - Clone a voice from audio
- `POST /voices/preview` - Generate voice preview
- `POST /generate/dialogue` - Generate multi-speaker dialogue
- `POST /generate/simple` - SSE generation
- `POST /generate/longform` - High-quality generation
- `GET /sample-script` - Get default script
- `GET /health` - Health check

## 🛠️ Development

### **Backend Development**
```bash
# Run backend directly
python3 neuphonic_backend.py list-voices
python3 backend_api.py

# Test API endpoints
curl http://localhost:8000/health
```

### **Frontend Development**
```bash
# Start development server
npm run dev

# Build for production
npm run build
npm start
```

### **Environment Variables**
- `NEUPHONIC_API_KEY`: Your Neuphonic API key (required)
- `NODE_ENV`: Development/production mode
- `DEBUG`: Enable debug output

## 📋 Requirements

### **Python**
- Python 3.8+
- pyneuphonic
- fastapi
- uvicorn
- requests
- pydub (for audio processing)

### **Node.js**
- Node.js 18.17.0+
- Next.js 15.4
- React 19
- Tailwind CSS
- Lucide React (icons)

## 🔐 Security

- **No hardcoded API keys**: All sensitive data via environment variables
- **Audio file exclusion**: Comprehensive `.gitignore` prevents large file commits
- **Input validation**: Script parsing and voice mapping validation
- **Error handling**: Graceful degradation and helpful error messages

## 📱 Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Issues**: [GitHub Issues](https://github.com/Pathaka-AI/voice-dialogue-studio/issues)
- **Documentation**: [API Docs](http://localhost:8000/docs) (when running)
- **Neuphonic API**: [Official Documentation](https://docs.neuphonic.com/)

## 🏆 Credits

- **Neuphonic**: AI voice technology
- **Pathaka.ai**: Development and innovation
- **Community**: Testing and feedback

---

**Made with ❤️ by [Pathaka.ai](https://github.com/Pathaka-AI)** 