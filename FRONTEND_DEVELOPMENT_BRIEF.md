# Voice Dialogue Studio - Frontend Development Brief

## Project Overview
A comprehensive voice dialogue generation application with voice cloning capabilities, built as a Next.js frontend that interfaces with a FastAPI backend supporting Neuphonic TTS and voice cloning APIs.

## Application Architecture

### Tech Stack
- **Framework**: Next.js 14+ with TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **State Management**: React useState/useEffect
- **API Integration**: Next.js API routes as proxy to FastAPI backend

### Backend API Assumptions
The frontend expects a working FastAPI backend with these endpoints:
- `GET /voices` - List all voices (preset + cloned)
- `POST /voices/clone` - Clone voice from audio sample
- `POST /voices/preview` - Generate voice preview
- `PATCH /voices/{id}` - Update voice metadata
- `DELETE /voices/{id}` - Delete cloned voice
- `POST /generate` - Generate dialogue from script
- `GET /status/{job_id}` - Check generation status
- `GET /download/{job_id}` - Download generated audio

## Page Layout & Navigation

### Header
- **Logo**: Microphone icon in blue circle + "Voice Dialogue Studio" title
- **Navigation Tabs**:
  - "Generator" (Play icon) - Main dialogue generation interface
  - "Voice Library" (Library icon) - Full voice management interface

### Main Content Areas

#### Generator Tab (Primary Interface)
Split into 2 main columns:

**Left Column (50%):**
1. **Script Uploader Component**
2. **Voice Mapper Component** (appears when speakers detected)

**Right Column (50%):**
1. **Quality Settings Component**
2. **Quick Voice Access Component** (compact voice library)
3. **Generation Progress Component** (when active)
4. **Audio Player Component** (when audio ready)
5. **Generate Button** (always at bottom)

#### Voice Library Tab
Full-page voice management interface with advanced filtering and management tools.

## Core Components

### 1. Script Uploader (`ScriptUploader.tsx`)

**Purpose**: Text input for dialogue scripts
**Features**:
- Large textarea for script input
- Real-time parsing to detect speakers
- Format guide showing `<Speaker>dialogue` syntax
- Character/word count
- Script validation

**Props**:
```typescript
interface ScriptUploaderProps {
  script: string
  onScriptChange: (content: string) => void
}
```

**Layout**:
- Card with title "Script Input"
- Textarea (minimum 6 rows, expandable)
- Help text showing format example
- Statistics bar (characters, estimated duration)

### 2. Voice Mapper (`VoiceMapper.tsx`)

**Purpose**: Assign voices to detected speakers
**Features**:
- Lists all detected speakers from script
- Dropdown for each speaker to select voice
- Voice preview buttons
- "Clone New Voice" quick action
- Visual indication of mapped/unmapped speakers

**Props**:
```typescript
interface VoiceMapperProps {
  speakers: string[]
  voiceMapping: Record<string, string>
  voices: Voice[]
  onMappingChange: (mapping: Record<string, string>) => void
  onTestVoice: (voiceId: string) => void
  onCloneVoice: () => void
}
```

**Layout**:
- Card with title "Voice Assignment"
- List of speakers with:
  - Speaker name
  - Voice selection dropdown
  - Play button for preview
  - Status indicator (mapped/unmapped)

### 3. Quality Settings (`QualitySettings.tsx`)

**Purpose**: Configure audio generation quality
**Features**:
- Preset quality levels (Speed, Balanced, Highest Quality)
- Manual controls for:
  - Sampling Rate (8kHz, 16kHz, 22kHz, 48kHz)
  - Encoding (PCM Linear, PCM μ-law)
  - Speed (0.7x to 2.0x)
  - Streaming Mode (Batch, SSE, WebSocket)
  - Quality Priority toggle
- Estimated output size/duration
- Real-time calculations

**Props**:
```typescript
interface QualitySettingsProps {
  defaultSettings: QualityConfig
  onSettingsChange: (settings: QualityConfig) => void
  estimatedDuration: number
}
```

**Layout**:
- Card with title "Quality Settings"
- Preset buttons row
- Expandable advanced settings
- Estimation display

### 4. Voice Cloner (`VoiceCloner.tsx`)

**Purpose**: Clone new voices from audio samples
**Features**:
- File upload (drag & drop + browse)
- Supported formats: WAV, MP3, M4A
- Real-time audio validation:
  - Duration check (3-120 seconds, ideal 5-15s)
  - Quality assessment
  - Noise level analysis
- Voice metadata input:
  - Name
  - Tags
- Audio preview with waveform visualization
- Quality score indicator
- Progress tracking during cloning

**Props**:
```typescript
interface VoiceClonerProps {
  isOpen: boolean
  onClose: () => void
  onVoiceCreated: (voiceId: string, voiceName: string) => void
}
```

**Layout**:
- Modal overlay
- File upload area with drag/drop
- Audio preview section
- Metadata form
- Validation feedback
- Action buttons (Cancel, Clone Voice)

### 5. Voice Library (`VoiceLibrary.tsx`)

**Purpose**: Comprehensive voice management
**Features**:
- Search functionality
- Filter by type (All, Preset, Cloned)
- Filter by tags
- View modes (Grid, List)
- Voice actions:
  - Preview/Play
  - Edit metadata
  - Delete
  - Select for mapping
- Bulk operations:
  - Import voices
  - Export voice library
- Voice cards showing:
  - Name, tags, type
  - Creation date
  - Usage statistics
  - Quick actions

**Props**:
```typescript
interface VoiceLibraryProps {
  voices: Voice[]
  onVoiceSelect?: (voiceId: string) => void
  onVoiceEdit?: (voiceId: string) => void
  onVoiceDelete?: (voiceId: string) => void
  onVoicePreview?: (voiceId: string) => void
  onImportVoices?: () => void
  onExportVoices?: () => void
  onCloneNewVoice?: () => void
  isCompact?: boolean
}
```

**Layouts**:
- **Compact Mode**: Simplified list for sidebar
- **Full Mode**: Complete interface with filters and grid

### 6. Generation Progress (`GenerationProgress.tsx`)

**Purpose**: Real-time generation tracking
**Features**:
- Overall progress bar
- Line-by-line status
- Estimated time remaining
- Error reporting
- Cancellation option
- Live status updates via polling

**Props**:
```typescript
interface GenerationProgressProps {
  jobId: string
  status: JobStatus
  progress: number
  totalLines: number
  completedLines: number
  errors: string[]
}
```

**Layout**:
- Card with title "Generation Progress"
- Progress bar with percentage
- Status text
- Line counter
- Error list if any

### 7. Audio Player (`AudioPlayer.tsx`)

**Purpose**: Play and download generated audio
**Features**:
- Standard playback controls
- Waveform visualization (mock)
- Download button
- Duration display
- Quality information
- File size information

**Props**:
```typescript
interface AudioPlayerProps {
  audioUrl: string
  duration: number
  onDownload: () => void
}
```

**Layout**:
- Card with title "Generated Audio"
- Audio controls row
- Waveform display
- Metadata and download section

## Data Types

### Core Types
```typescript
interface Voice {
  id: string
  name: string
  tags: string[]
  type: 'preset' | 'cloned'
  createdAt: string
  lastUsed?: string
  modelType?: string
  sampleUrl?: string
}

interface QualityConfig {
  samplingRate: 8000 | 16000 | 22050 | 48000
  encoding: 'pcm_linear' | 'pcm_mulaw'
  speed: number // 0.7 to 2.0
  streamingMode: 'batch' | 'sse' | 'websocket'
  prioritizeQuality: boolean
}

interface AppState {
  script: string
  speakers: string[]
  voiceMapping: Record<string, string>
  qualitySettings: QualityConfig
  voiceLibrary: {
    voices: Voice[]
    loading: boolean
    filter: {
      type: 'all' | 'preset' | 'cloned'
      tags: string[]
      search: string
    }
  }
  voiceCloning: {
    isCloning: boolean
    audioFile: File | null
    audioPreview: string | null
    metadata: { name: string; tags: string[] }
    validation: {
      duration: number
      noiseLevel: number
      isValid: boolean
      errors: string[]
    }
  }
  generationJob: {
    id: string
    status: JobStatus
    progress: number
    errors: string[]
    mode: 'batch' | 'streaming'
  } | null
  generatedAudio: {
    url: string
    duration: number
    fileSize: number
    quality: QualityConfig
  } | null
}
```

## API Integration

### Next.js API Routes (Proxy Layer)
All frontend API calls go through Next.js API routes that proxy to the FastAPI backend:

- `/api/voices` - GET voices list
- `/api/voices/clone` - POST voice cloning
- `/api/voices/preview` - POST voice preview
- `/api/voices/[voiceId]` - PATCH/DELETE voice operations
- `/api/generate-dialogue` - POST dialogue generation
- `/api/check-status/[jobId]` - GET job status
- `/api/download/[jobId]` - GET audio download

### Backend Response Mapping
The frontend maps backend responses to frontend types:
```typescript
// Backend voice response -> Frontend Voice type
const mapped: Voice[] = (data.voices || []).map((v: any) => ({
  id: v.id,
  name: v.name,
  tags: Array.isArray(v.tags) ? v.tags : [],
  type: v.type === 'Cloned Voice' ? 'cloned' : 'preset',
  createdAt: v.created_at || new Date().toISOString(),
  sampleUrl: v.sample_url,
  modelType: v.model
}))
```

## User Workflows

### 1. Basic Dialogue Generation
1. User enters script in Script Uploader
2. System detects speakers automatically
3. Voice Mapper appears with detected speakers
4. User assigns voices to each speaker
5. User adjusts Quality Settings if needed
6. User clicks "Generate Dialogue"
7. Generation Progress shows real-time status
8. Audio Player appears when complete
9. User can play and download result

### 2. Voice Cloning Workflow
1. User clicks "Clone Voice" button
2. Voice Cloner modal opens
3. User uploads audio file (drag/drop or browse)
4. System validates audio (duration, quality, noise)
5. User enters voice name and tags
6. User clicks "Clone Voice"
7. System processes cloning with progress
8. New voice appears in Voice Library
9. Voice is immediately available for mapping

### 3. Voice Management
1. User switches to "Voice Library" tab
2. Full library interface loads all voices
3. User can search, filter, and organize voices
4. Voice actions: preview, edit, delete
5. Bulk operations: import/export
6. Changes sync across all components

## Design Patterns

### State Management
- Single `AppState` object managed at top level
- State updates flow down via props
- Event handlers bubble up via callbacks
- Optimistic updates for better UX

### Error Handling
- Try/catch blocks around all API calls
- User-friendly error messages
- Graceful fallbacks (e.g., show cached data)
- Progress indication during long operations

### Performance Considerations
- Voice list fetched once on mount
- Real-time polling for job status
- Debounced search inputs
- Lazy loading for large voice libraries
- Audio file validation before upload

### Responsive Design
- Mobile-first approach
- Collapsible sections on small screens
- Adaptive grid layouts
- Touch-friendly interface elements

## Development Notes

### Required Dependencies
```json
{
  "next": "^14.2.0",
  "react": "^18.3.0",
  "react-dom": "^18.3.0",
  "typescript": "^5.3.0",
  "tailwindcss": "^3.4.0",
  "lucide-react": "^0.263.0",
  "clsx": "^2.0.0",
  "react-dropzone": "^14.2.0"
}
```

### File Structure
```
frontend/
├── app/
│   ├── components/
│   │   ├── ScriptUploader.tsx
│   │   ├── VoiceMapper.tsx
│   │   ├── QualitySettings.tsx
│   │   ├── VoiceCloner.tsx
│   │   ├── VoiceLibrary.tsx
│   │   ├── GenerationProgress.tsx
│   │   └── AudioPlayer.tsx
│   ├── lib/
│   │   ├── types/index.ts
│   │   └── utils/index.ts
│   ├── api/
│   │   └── [various proxy routes]
│   └── page.tsx (main application)
```

### Testing Considerations
- Component isolation testing
- API integration tests
- File upload testing
- Audio playback testing
- Real-time updates testing
- Error scenario testing

This brief provides a complete specification for replicating the Voice Dialogue Studio frontend with a working Longform-enabled backend. 