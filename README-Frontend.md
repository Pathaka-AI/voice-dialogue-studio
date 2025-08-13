# Voice Dialogue Studio - Next.js Frontend

A production-ready Next.js 15.4 frontend for professional voice dialogue generation with AI-powered voice cloning, built to integrate seamlessly with your working Neuphonic backend.

## 🌟 Features

### 🎙️ **Complete Voice Pipeline**
- **Script Processing**: Real-time parsing with `<Speaker> dialogue` format
- **Voice Assignment**: Intuitive mapping of speakers to voices
- **Quality Control**: Multiple generation modes (SSE vs Longform)
- **Audio Generation**: Full integration with your Neuphonic backend

### 🎵 **Voice Management**
- **Voice Library**: Browse all available preset and cloned voices
- **Voice Preview**: Real-time voice testing with sample audio
- **Voice Cloning**: Upload audio samples to create custom voices
- **Auto-Assignment**: Smart voice mapping for detected speakers

### ⚙️ **Production Features**
- **Next.js 15.4**: Latest framework with App Router
- **Real Backend Integration**: Direct connection to your working Python backend
- **Professional UI**: Tailwind CSS with responsive design
- **Error Handling**: Comprehensive error management and user feedback
- **Audio Playback**: Built-in player with download functionality

## 🚀 Quick Start

### Prerequisites
- Node.js 18.17.0 or higher
- Python 3.8+ with your working Neuphonic backend
- Your existing `neuphonic_backend.py` and dependencies

### Installation & Setup

1. **Install Dependencies**
   ```bash
   # Install Node.js dependencies
   npm install
   
   # Install Python API dependencies
   pip3 install -r requirements-api.txt
   ```

2. **Start the Application**
   ```bash
   # Option 1: Use the provided start script (recommended)
   chmod +x start.sh
   ./start.sh
   
   # Option 2: Start services manually
   # Terminal 1 - Start FastAPI backend
   python3 backend_api.py
   
   # Terminal 2 - Start Next.js frontend
   npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📋 Usage Guide

### 1. Script Input
1. Navigate to the **Generator** tab
2. Enter your dialogue script using the format:
   ```
   <Alex> Welcome to our show!
   <Sarah> Thanks for having me, Alex.
   <Alex> Today we're discussing...
   ```
3. The system automatically detects speakers and validates format

### 2. Voice Assignment
1. Once speakers are detected, the **Voice Assignment** panel appears
2. Select voices for each speaker from your available voice library
3. Use the preview button to test voices before generation
4. The system attempts auto-assignment based on available voices

### 3. Quality Settings
- **Speed Mode**: Fast generation with SSE (22kHz)
- **Highest Quality**: Studio quality with Longform (48kHz)
- **Custom Settings**: Manual control over sampling rate and encoding

### 4. Audio Generation
1. Click **Generate Dialogue** once all speakers have assigned voices
2. Wait for generation to complete (time varies by quality setting)
3. Use the built-in audio player to preview results
4. Download the generated dialogue as a WAV file

### 5. Voice Library Management
1. Switch to the **Voice Library** tab
2. Browse all available preset and cloned voices
3. Preview any voice with sample text
4. (Future) Clone new voices from audio samples

## 🏗️ Architecture

### Frontend Stack
- **Next.js 15.4**: React framework with App Router
- **Tailwind CSS**: Utility-first styling framework
- **Lucide React**: Modern icon library
- **React Hooks**: State management with useState/useEffect

### Backend Integration
- **FastAPI Wrapper**: `backend_api.py` exposes your Python backend as REST API
- **Direct Integration**: No mocking - works with your actual Neuphonic backend
- **File Handling**: Proper audio upload/download with temporary file management
- **Error Handling**: Comprehensive error propagation from Python to frontend

### API Endpoints
```
GET  /voices              - List all voices
POST /voices/clone        - Clone voice from audio
POST /voices/preview      - Generate voice preview
POST /generate/dialogue   - Generate full dialogue
POST /generate/longform   - Generate high-quality audio
GET  /health             - Health check
```

## 🔧 Technical Details

### Component Structure
```
app/
├── components/
│   └── ScriptUploader.js     - Script input and validation
├── lib/
│   └── api.js               - Backend API integration
├── globals.css              - Tailwind styles and components
├── layout.js               - Root layout
└── page.js                 - Main application
```

### State Management
- **Application State**: Single source of truth in main component
- **Voice Data**: Real-time loading from your backend
- **Audio Management**: Object URLs for audio playback/download
- **Error Handling**: User-friendly error messages and fallbacks

### Quality Modes
- **SSE Mode**: Fast generation using your existing SSE implementation
- **Longform Mode**: High-quality 48kHz using your working longform system
- **Custom Settings**: Direct control over sampling rate and encoding

## 🎯 Production Ready

### Performance
- **Lazy Loading**: Components load only when needed
- **Audio Optimization**: Efficient blob handling for large audio files
- **Error Boundaries**: Graceful error handling throughout the application
- **Loading States**: Clear feedback during async operations

### Responsive Design
- **Mobile Support**: Touch-friendly interface for all screen sizes
- **Accessible**: Proper semantic HTML and keyboard navigation
- **Professional**: Clean, modern design suitable for business use

### Security
- **CORS Configuration**: Proper cross-origin setup
- **File Validation**: Audio file type and size checking
- **Error Sanitization**: Safe error message display

## 🔄 Integration with Your Backend

The frontend directly integrates with your existing Neuphonic backend:

- **Voice Listing**: Uses your `backend.list_voices()` method
- **Voice Cloning**: Integrates with your `backend.clone_voice()` function
- **Audio Generation**: Supports both SSE and Longform via your existing methods
- **Script Processing**: Compatible with your script parsing logic
- **File Management**: Works with your outputs directory structure

## 🛠️ Development

### Development Server
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

### Customization
- **Styling**: Modify `app/globals.css` for custom styles
- **Components**: Extend components in `app/components/`
- **API Integration**: Update `app/lib/api.js` for backend changes
- **Settings**: Adjust quality presets and defaults

### Adding Features
- **Voice Cloning UI**: Implement file upload modal
- **Batch Processing**: Add support for multiple script processing
- **Progress Tracking**: Real-time generation progress
- **Voice Analytics**: Usage statistics and voice performance metrics

## 📝 Notes

- The frontend is designed to work with your exact existing backend
- No mock data - all functionality connects to real API endpoints
- Audio generation uses your working longform inference system
- Voice management integrates with your existing voice mapping system
- Quality settings match your backend's SSE and Longform capabilities

## 🎉 Ready to Use

This is a complete, production-ready frontend that integrates seamlessly with your working Neuphonic backend. Simply run the start script and you'll have a professional voice dialogue studio interface connected to your proven audio generation system!

**Next Steps:**
1. Run `./start.sh` to launch the complete system
2. Access http://localhost:3000 to use the interface
3. Test with your existing Hadrian's Wall script
4. Generate professional-quality dialogues with your cloned voices! 