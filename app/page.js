'use client';

import { useState, useEffect, useCallback } from 'react';
import { Mic, Play, Library, Settings, Wand2, Download, Clock, FileDown } from 'lucide-react';
import ScriptUploader from './components/ScriptUploader';
import { voiceAPI, audioAPI, scriptUtils } from './lib/api';

export default function VoiceDialogueStudio() {
  // Main application state
  const [activeTab, setActiveTab] = useState('generator');
  const [script, setScript] = useState('');
  const [speakers, setSpeakers] = useState([]);
  const [voiceMapping, setVoiceMapping] = useState({});
  const [speedMapping, setSpeedMapping] = useState({}); // Add speed mapping state
  const [voices, setVoices] = useState([]);
  const [languageFilter, setLanguageFilter] = useState('all'); // Add language filter state
  const [loading, setLoading] = useState(false);
  const [generatedAudio, setGeneratedAudio] = useState(null);
  const [generationTime, setGenerationTime] = useState(null); // Add generation timer state
  const [startTime, setStartTime] = useState(null); // Track start time
  const [currentTime, setCurrentTime] = useState(0); // Real-time timer display
  const [lastGenerationPreset, setLastGenerationPreset] = useState(null); // Store last generation data
  const [qualitySettings, setQualitySettings] = useState({
    samplingRate: 48000,
    encoding: 'pcm_linear',
    speed: 1.0,
    prioritizeQuality: true,
    streamingMode: 'longform',
    useParallel: false, // Add parallel processing toggle
  });

  // Load initial data
  useEffect(() => {
    loadVoices();
    loadSampleScript();
  }, []);

  // Real-time timer effect
  useEffect(() => {
    let interval = null;
    
    if (loading && startTime) {
      interval = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        setCurrentTime(elapsed);
      }, 100); // Update every 100ms for smooth display
    } else {
      setCurrentTime(0);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [loading, startTime]);

  const loadVoices = async () => {
    try {
      setLoading(true);
      const loadedVoices = await voiceAPI.listVoices();
      setVoices(loadedVoices);
    } catch (error) {
      console.error('Failed to load voices:', error);
      // You can add a toast notification here
      alert('Failed to load voices. Make sure the backend is running on localhost:8000');
    } finally {
      setLoading(false);
    }
  };

  const loadSampleScript = async () => {
    try {
      const sampleScript = await scriptUtils.getSampleScript();
      if (sampleScript && !script) { // Only load if no script is already present
        setScript(sampleScript);
      }
    } catch (error) {
      console.error('Failed to load sample script:', error);
      // Don't show an error to the user, just continue without the sample
    }
  };

  // Get unique languages from voices
  const getAvailableLanguages = useCallback(() => {
    const languages = [...new Set(voices.map(voice => voice.langCode))].filter(Boolean);
    return languages.sort();
  }, [voices]);

  // Filter voices by selected language
  const getFilteredVoices = useCallback(() => {
    if (languageFilter === 'all') {
      return voices;
    }
    return voices.filter(voice => voice.langCode === languageFilter);
  }, [voices, languageFilter]);

  // Get language display name
  const getLanguageDisplayName = (langCode) => {
    const languageNames = {
      'en': 'English',
      'es': 'Spanish',
      'fr': 'French', 
      'de': 'German',
      'pt': 'Portuguese',
      'nl': 'Dutch',
      'ru': 'Russian',
      'ar': 'Arabic',
      'hi': 'Hindi',
      'zh': 'Chinese',
      'ca': 'Catalan',
      'kn': 'Kannada',
      'ta': 'Tamil',
      'te': 'Telugu',
      'it': 'Italian',
      'ja': 'Japanese',
      'ko': 'Korean'
    };
    return languageNames[langCode] || langCode?.toUpperCase() || 'Unknown';
  };

  const handleSpeakersDetected = useCallback((detectedSpeakers) => {
    setSpeakers(detectedSpeakers);
    
    // Only auto-assign voices for NEW speakers that don't already have assignments
    setVoiceMapping(prev => {
      const newMapping = { ...prev };
      
      detectedSpeakers.forEach(speaker => {
        // Only assign if this speaker doesn't already have a voice assigned
        if (!newMapping[speaker]) {
          // Specific mapping for your voices (from voice_mapping.json)
          if (speaker === "Alex") {
            // Alex voice ID from your mapping
            const alexVoice = voices.find(v => v.id === "6654e5a9-143e-46f4-a44a-4fcb9e1fe2a6");
            if (alexVoice) {
              newMapping[speaker] = alexVoice.id;
            }
          } else if (speaker === "Rowan") {
            // Rowan voice ID from your mapping
            const rowanVoice = voices.find(v => v.id === "aed5585d-b1ce-43fa-895f-de746fdf1e67");
            if (rowanVoice) {
              newMapping[speaker] = rowanVoice.id;
            }
          } else {
            // For other speakers, try to find any available voice
            const availableVoice = voices.find(v => 
              !Object.values(newMapping).includes(v.id) && 
              (v.type === 'cloned' || v.type === 'preset')
            );
            if (availableVoice) {
              newMapping[speaker] = availableVoice.id;
            }
          }
        }
      });
      
      return newMapping;
    });

    // Initialize speed settings for new speakers
    setSpeedMapping(prev => {
      const newSpeedMapping = { ...prev };
      
      detectedSpeakers.forEach(speaker => {
        // Only assign default speed if this speaker doesn't already have one
        if (!newSpeedMapping[speaker]) {
          // Default speeds based on your preferences
          if (speaker === "Alex") {
            newSpeedMapping[speaker] = 0.7; // Alex slower
          } else if (speaker === "Rowan") {
            newSpeedMapping[speaker] = 0.9; // Rowan slightly slower
          } else {
            newSpeedMapping[speaker] = 1.0; // Default normal speed
          }
        }
      });
      
      return newSpeedMapping;
    });
  }, [voices]); // Removed voiceMapping from dependencies

  const handleVoicePreview = async (voiceId) => {
    try {
      const audioUrl = await voiceAPI.previewVoice(voiceId);
      const audio = new Audio(audioUrl);
      audio.play();
      
      // Clean up the object URL after playing
      audio.addEventListener('ended', () => {
        URL.revokeObjectURL(audioUrl);
      });
    } catch (error) {
      console.error('Failed to preview voice:', error);
      alert('Failed to preview voice');
    }
  };

  const handleGenerateDialogue = async () => {
    if (!script || speakers.length === 0) {
      alert('Please enter a script with speakers');
      return;
    }

    const unmappedSpeakers = speakers.filter(s => !voiceMapping[s]);
    if (unmappedSpeakers.length > 0) {
      alert(`Please assign voices to: ${unmappedSpeakers.join(', ')}`);
      return;
    }

    try {
      setLoading(true);
      setGeneratedAudio(null);
      setGenerationTime(null); // Reset previous timer
      
      // Start timing
      const startTimestamp = Date.now();
      setStartTime(startTimestamp);
      
      console.log('Generating dialogue with:', {
        script,
        voiceMapping,
        speedMapping,
        qualitySettings,
      });
      
      const audioUrl = await audioAPI.generateDialogue(script, voiceMapping, qualitySettings, speedMapping);
      
      // Calculate generation time
      const endTimestamp = Date.now();
      const duration = (endTimestamp - startTimestamp) / 1000; // Convert to seconds
      setGenerationTime(duration);
      
      // Create and store generation preset data
      const presetData = createGenerationPreset(duration, new Date(startTimestamp));
      setLastGenerationPreset(presetData);
      
      setGeneratedAudio(audioUrl);
      
      console.log(`✅ Generation completed in ${duration.toFixed(1)} seconds`);
      console.log('📋 Generation preset created:', presetData);
      
    } catch (error) {
      console.error('Generation failed:', error);
      alert('Failed to generate dialogue: ' + error.message);
      setGenerationTime(null); // Clear timer on error
    } finally {
      setLoading(false);
      setStartTime(null); // Reset start time
    }
  };

  const handleDownloadAudio = () => {
    if (generatedAudio) {
      const link = document.createElement('a');
      link.href = generatedAudio;
      link.download = 'dialogue.wav';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const createGenerationPreset = (duration, timestamp = new Date()) => {
    // Get voice details for the preset
    const voiceDetails = {};
    Object.entries(voiceMapping).forEach(([speaker, voiceId]) => {
      const voice = voices.find(v => v.id === voiceId);
      voiceDetails[speaker] = {
        voiceId: voiceId,
        voiceName: voice?.name || 'Unknown',
        voiceType: voice?.type || 'Unknown',
        language: voice?.langCode || 'Unknown',
        languageDisplay: getLanguageDisplayName(voice?.langCode),
        speed: speedMapping[speaker] || 1.0
      };
    });

    // Calculate script statistics
    const scriptStats = scriptUtils.parseScript(script);
    
    return {
      metadata: {
        timestamp: timestamp.toISOString(),
        generationTime: duration,
        formatVersion: "1.0"
      },
      script: {
        content: script,
        totalLines: scriptStats.totalLines,
        totalSpeakers: scriptStats.speakers.length,
        speakers: scriptStats.speakers,
        estimatedDuration: scriptStats.estimatedDuration,
        wordCount: script.split(/\s+/).length,
        characterCount: script.length
      },
      voices: voiceDetails,
      qualitySettings: {
        samplingRate: qualitySettings.samplingRate,
        encoding: qualitySettings.encoding,
        streamingMode: qualitySettings.streamingMode,
        prioritizeQuality: qualitySettings.prioritizeQuality,
        useParallel: qualitySettings.useParallel || false
      },
      performance: {
        generationTimeSeconds: duration,
        generationTimeFormatted: `${duration.toFixed(1)}s`,
        processingMethod: qualitySettings.streamingMode === 'longform' 
          ? (qualitySettings.useParallel ? 'Longform (Parallel)' : 'Longform (Sequential)')
          : 'SSE (Fast)',
        estimatedSpeedup: qualitySettings.useParallel ? '66% faster than sequential' : 'N/A'
      }
    };
  };

  const handleDownloadPreset = () => {
    if (!lastGenerationPreset) {
      alert('No generation data available to download');
      return;
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
    const method = lastGenerationPreset.performance.processingMethod.replace(/[^\w]/g, '_');
    const filename = `voice-preset_${timestamp}_${method}_${lastGenerationPreset.performance.generationTimeFormatted}.json`;
    
    const dataStr = JSON.stringify(lastGenerationPreset, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
    
    console.log('📁 Downloaded generation preset:', filename);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
                <Mic className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">Voice Dialogue Studio</h1>
            </div>

            {/* Navigation */}
            <nav className="flex space-x-1">
              <button
                onClick={() => setActiveTab('generator')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'generator'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Play className="w-4 h-4" />
                <span>Generator</span>
              </button>
              <button
                onClick={() => setActiveTab('library')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'library'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Library className="w-4 h-4" />
                <span>Voice Library</span>
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'generator' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column */}
            <div className="space-y-6">
              {/* Script Uploader */}
              <ScriptUploader
                script={script}
                onScriptChange={setScript}
                onSpeakersDetected={handleSpeakersDetected}
              />

              {/* Voice Mapper */}
              {speakers.length > 0 && (
                <div className="card">
                  <div className="card-header">
                    <div className="flex items-center space-x-2">
                      <Wand2 className="w-5 h-5 text-primary-600" />
                      <h3 className="card-title">Voice Assignment</h3>
                    </div>
                    <div className="flex items-center space-x-2">
                      <label className="text-sm font-medium text-gray-700">Language:</label>
                      <select
                        value={languageFilter}
                        onChange={(e) => setLanguageFilter(e.target.value)}
                        className="select text-sm min-w-[120px]"
                      >
                        <option value="all">All Languages</option>
                        {getAvailableLanguages().map((langCode) => (
                          <option key={langCode} value={langCode}>
                            {getLanguageDisplayName(langCode)}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="space-y-4">
                    {speakers.map((speaker) => {
                      const selectedVoice = voices.find(v => v.id === voiceMapping[speaker]);
                      const filteredVoices = getFilteredVoices();
                      
                      return (
                        <div key={`speaker-${speaker}`} className="p-4 bg-gray-50 rounded-lg">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center space-x-3">
                              <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                                <span className="text-sm font-medium text-primary-700">
                                  {speaker.charAt(0)}
                                </span>
                              </div>
                              <div>
                                <h4 className="font-medium text-gray-900">{speaker}</h4>
                                <p className="text-sm text-gray-500">
                                  {selectedVoice 
                                    ? `${selectedVoice.name} (${getLanguageDisplayName(selectedVoice.langCode)})`
                                    : 'No voice assigned'
                                  }
                                </p>
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-2">
                              <select
                                value={voiceMapping[speaker] || ''}
                                onChange={(e) => {
                                  console.log(`Changing voice for ${speaker} from ${voiceMapping[speaker]} to ${e.target.value}`);
                                  setVoiceMapping(prev => {
                                    const newMapping = {
                                      ...prev,
                                      [speaker]: e.target.value
                                    };
                                    console.log('New voice mapping:', newMapping);
                                    return newMapping;
                                  });
                                }}
                                className="select text-sm min-w-[200px]"
                              >
                                <option value="">Select voice...</option>
                                {filteredVoices.map((voice) => (
                                  <option key={voice.id} value={voice.id}>
                                    {voice.name} ({voice.type}) - {getLanguageDisplayName(voice.langCode)}
                                  </option>
                                ))}
                              </select>
                              
                              {voiceMapping[speaker] && (
                                <button
                                  className="btn-sm btn-secondary"
                                  onClick={() => handleVoicePreview(voiceMapping[speaker])}
                                  disabled={loading}
                                >
                                  <Play className="w-3 h-3" />
                                </button>
                              )}
                            </div>
                          </div>

                          {/* Speed Control */}
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <label className="text-sm font-medium text-gray-700">
                                Speed: {speedMapping[speaker]?.toFixed(1) || '1.0'}x
                              </label>
                            </div>
                            <div className="flex items-center space-x-3">
                              <span className="text-xs text-gray-500">Slow</span>
                              <input
                                type="range"
                                min="0.7"
                                max="2.0"
                                step="0.1"
                                value={speedMapping[speaker] || 1.0}
                                onChange={(e) => {
                                  const newSpeed = parseFloat(e.target.value);
                                  setSpeedMapping(prev => ({
                                    ...prev,
                                    [speaker]: newSpeed
                                  }));
                                }}
                                className="w-24 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                              />
                              <span className="text-xs text-gray-500">Fast</span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              {/* Quality Settings */}
              <div className="card">
                <div className="card-header">
                  <div className="flex items-center space-x-2">
                    <Settings className="w-5 h-5 text-primary-600" />
                    <h3 className="card-title">Quality Settings</h3>
                  </div>
                </div>

                <div className="space-y-4">
                  {/* Quality Presets */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Quality Preset
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      <button
                        onClick={() => setQualitySettings({
                          samplingRate: 22050,
                          encoding: 'pcm_linear',
                          prioritizeQuality: false,
                          streamingMode: 'sse',
                        })}
                        className={`btn-sm ${
                          !qualitySettings.prioritizeQuality ? 'btn-primary' : 'btn-secondary'
                        }`}
                      >
                        Speed
                      </button>
                      <button
                        onClick={() => setQualitySettings({
                          samplingRate: 22050,
                          encoding: 'pcm_linear',
                          prioritizeQuality: false,
                          streamingMode: 'sse',
                        })}
                        className="btn-sm btn-secondary"
                      >
                        Balanced
                      </button>
                      <button
                        onClick={() => setQualitySettings({
                          samplingRate: 48000,
                          encoding: 'pcm_linear',
                          prioritizeQuality: true,
                          streamingMode: 'longform',
                        })}
                        className={`btn-sm ${
                          qualitySettings.prioritizeQuality ? 'btn-primary' : 'btn-secondary'
                        }`}
                      >
                        Highest Quality
                      </button>
                    </div>
                  </div>

                  {/* Advanced Settings */}
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Sampling Rate: {qualitySettings.samplingRate}Hz
                      </label>
                      <select
                        value={qualitySettings.samplingRate}
                        onChange={(e) => setQualitySettings(prev => ({
                          ...prev,
                          samplingRate: parseInt(e.target.value)
                        }))}
                        className="select text-sm"
                      >
                        <option value={22050}>22.05kHz (Standard)</option>
                        <option value={48000}>48kHz (Studio Quality)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Generation Mode
                      </label>
                      <select
                        value={qualitySettings.streamingMode}
                        onChange={(e) => setQualitySettings(prev => ({
                          ...prev,
                          streamingMode: e.target.value,
                          prioritizeQuality: e.target.value === 'longform'
                        }))}
                        className="select text-sm"
                      >
                        <option value="sse">SSE (Fast, 22kHz)</option>
                        <option value="longform">Longform (Best Quality, 48kHz)</option>
                      </select>
                    </div>

                    {/* Parallel Processing Toggle - only show for longform */}
                    {qualitySettings.streamingMode === 'longform' && (
                      <div>
                        <label className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={qualitySettings.useParallel}
                            onChange={(e) => setQualitySettings(prev => ({
                              ...prev,
                              useParallel: e.target.checked
                            }))}
                            className="w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 focus:ring-2"
                          />
                          <span className="text-sm font-medium text-gray-700">
                            Parallel Processing ⚡
                          </span>
                        </label>
                        <p className="text-xs text-gray-500 mt-1">
                          {qualitySettings.useParallel 
                            ? "⚡ Fast: Process all segments simultaneously (66% faster)" 
                            : "🔄 Sequential: Process segments one by one (more reliable)"
                          }
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Quality Info */}
                  <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                    <div className="text-sm text-blue-700">
                      <strong>Current Settings:</strong>
                      <ul className="mt-1 space-y-1 text-xs">
                        <li>• {qualitySettings.samplingRate}Hz sampling rate</li>
                        <li>• {qualitySettings.streamingMode === 'longform' ? 'Studio quality (slower)' : 'Fast generation'}</li>
                        <li>• {qualitySettings.encoding} encoding</li>
                        {qualitySettings.streamingMode === 'longform' && (
                          <li>• {qualitySettings.useParallel ? 'Parallel processing (⚡ 66% faster)' : 'Sequential processing (🔄 reliable)'}</li>
                        )}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Generated Audio Player */}
              {generatedAudio && (
                <div className="card">
                  <div className="card-header">
                    <h3 className="card-title">Generated Audio</h3>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={handleDownloadPreset}
                        disabled={!lastGenerationPreset}
                        className="btn-sm btn-secondary"
                      >
                        <FileDown className="w-4 h-4 mr-1" />
                        Preset
                      </button>
                      <button
                        onClick={handleDownloadAudio}
                        className="btn-sm btn-secondary"
                      >
                        <Download className="w-4 h-4 mr-1" />
                        Audio
                      </button>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <audio controls className="w-full">
                      <source src={generatedAudio} type="audio/wav" />
                      Your browser does not support the audio element.
                    </audio>
                    
                    <div className="text-sm text-gray-600">
                      <p>Quality: {qualitySettings.samplingRate}Hz, {qualitySettings.streamingMode}</p>
                      {generationTime !== null && (
                        <p>Generation time: {generationTime.toFixed(1)}s {qualitySettings.streamingMode === 'longform' && qualitySettings.useParallel ? '(Parallel)' : qualitySettings.streamingMode === 'longform' ? '(Sequential)' : ''}</p>
                      )}
                      {lastGenerationPreset && (
                        <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs">
                          <p className="font-medium text-blue-800 mb-1">Preset includes:</p>
                          <ul className="text-blue-700 space-y-0.5">
                            <li>• Script ({lastGenerationPreset.script.totalLines} lines, {lastGenerationPreset.script.totalSpeakers} speakers)</li>
                            <li>• Voice mappings & speeds for {Object.keys(lastGenerationPreset.voices).length} speakers</li>
                            <li>• Quality settings ({lastGenerationPreset.qualitySettings.samplingRate}Hz, {lastGenerationPreset.performance.processingMethod})</li>
                            <li>• Performance data ({lastGenerationPreset.performance.generationTimeFormatted})</li>
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Generate Button */}
              <div className="card">
                <button
                  onClick={handleGenerateDialogue}
                  disabled={loading || !script || speakers.length === 0 || Object.keys(voiceMapping).length !== speakers.length}
                  className={`w-full btn-lg ${
                    loading || !script || speakers.length === 0 || Object.keys(voiceMapping).length !== speakers.length
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'btn-primary'
                  }`}
                >
                  {loading ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Generating...</span>
                      <div className="flex items-center space-x-1 ml-2">
                        <Clock className="w-4 h-4" />
                        <span className="font-mono">{currentTime.toFixed(1)}s</span>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <Play className="w-5 h-5" />
                      <span>Generate Dialogue</span>
                    </div>
                  )}
                </button>
                
                {/* Timer Display */}
                {generationTime !== null && (
                  <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-md">
                    <div className="flex items-center justify-center space-x-2 text-green-700">
                      <Clock className="w-4 h-4" />
                      <span className="text-sm font-medium">
                        Generation completed in {generationTime.toFixed(1)} seconds
                      </span>
                      {qualitySettings.streamingMode === 'longform' && (
                        <span className="text-xs">
                          ({qualitySettings.useParallel ? 'Parallel' : 'Sequential'})
                        </span>
                      )}
                    </div>
                  </div>
                )}
                
                {speakers.length > 0 && Object.keys(voiceMapping).length !== speakers.length && (
                  <p className="text-sm text-amber-600 mt-2 text-center">
                    Please assign voices to all speakers before generating
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'library' && (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Voice Library</h3>
              <button 
                className="btn-primary"
                onClick={() => alert('Voice cloning feature coming soon!')}
              >
                + Clone New Voice
              </button>
            </div>
            
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-6 h-6 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
                <span className="ml-2">Loading voices...</span>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {voices.map((voice) => (
                  <div key={voice.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-gray-900">{voice.name}</h4>
                      <div className="flex items-center space-x-2">
                        <span className="badge badge-success text-xs">
                          {getLanguageDisplayName(voice.langCode)}
                        </span>
                        <span className={`badge ${
                          voice.type === 'cloned' ? 'badge-primary' : 'badge-secondary'
                        }`}>
                          {voice.type}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex flex-wrap gap-1 mb-3">
                      {voice.tags.map((tag) => (
                        <span key={tag} className="badge badge-secondary text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <button 
                        className="btn-sm btn-secondary"
                        onClick={() => handleVoicePreview(voice.id)}
                        disabled={loading}
                      >
                        <Play className="w-3 h-3 mr-1" />
                        Preview
                      </button>
                      
                      {voice.type === 'cloned' && (
                        <button 
                          className="text-red-600 hover:text-red-800 text-sm"
                          onClick={() => alert('Voice deletion feature coming soon!')}
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
} 