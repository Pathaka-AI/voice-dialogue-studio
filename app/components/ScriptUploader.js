'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { FileText, Users, Clock, AlertCircle, FileCode } from 'lucide-react';
import { scriptUtils } from '../lib/api';

export default function ScriptUploader({ script, onScriptChange, onSpeakersDetected }) {
  const [validation, setValidation] = useState({ isValid: true, errors: [] });
  const [stats, setStats] = useState({ characters: 0, words: 0, lines: 0, speakers: 0, estimatedDuration: 0 });
  const [loadingSample, setLoadingSample] = useState(false);

  // Function to load sample script
  const handleLoadSample = async () => {
    try {
      setLoadingSample(true);
      const sampleScript = await scriptUtils.getSampleScript();
      if (sampleScript) {
        onScriptChange(sampleScript);
      }
    } catch (error) {
      console.error('Failed to load sample script:', error);
      alert('Failed to load sample script. Please try again.');
    } finally {
      setLoadingSample(false);
    }
  };

  // Memoize the parsed script to prevent unnecessary recalculations
  const parsedScript = useMemo(() => {
    return script ? scriptUtils.parseScript(script) : { lines: [], speakers: [], totalLines: 0 };
  }, [script]);

  // Memoize speakers array to prevent triggering callback when speakers haven't changed
  const detectedSpeakers = useMemo(() => parsedScript.speakers, [parsedScript.speakers]);

  // Only call the parent callback when speakers actually change
  useEffect(() => {
    if (detectedSpeakers.length > 0 && onSpeakersDetected) {
      onSpeakersDetected(detectedSpeakers);
    }
  }, [detectedSpeakers, onSpeakersDetected]);

  useEffect(() => {
    if (script) {
      // Validate script
      const validationResult = scriptUtils.validateScript(script);
      setValidation(validationResult);

      // Calculate stats using memoized parsed script
      const characters = script.length;
      const words = script.split(/\s+/).filter(word => word.length > 0).length;
      const estimatedDuration = scriptUtils.estimateDuration(script);

      setStats({
        characters,
        words,
        lines: parsedScript.totalLines,
        speakers: parsedScript.speakers.length,
        estimatedDuration,
      });
    } else {
      setStats({ characters: 0, words: 0, lines: 0, speakers: 0, estimatedDuration: 0 });
      setValidation({ isValid: true, errors: [] });
    }
  }, [script, parsedScript]);

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center space-x-2">
          <FileText className="w-5 h-5 text-primary-600" />
          <h3 className="card-title">Script Input</h3>
        </div>
        <button
          onClick={handleLoadSample}
          disabled={loadingSample}
          className="btn-sm btn-secondary flex items-center space-x-1"
        >
          <FileCode className="w-3 h-3" />
          <span>{loadingSample ? 'Loading...' : 'Load Sample'}</span>
        </button>
      </div>

      <div className="space-y-4">
        {/* Help text */}
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <h4 className="text-sm font-medium text-blue-900 mb-2">Script Format</h4>
          <p className="text-sm text-blue-700 mb-2">
            Use the format: <code className="bg-blue-100 px-1 rounded">&lt;Speaker&gt; dialogue text</code>
          </p>
          <div className="text-xs text-blue-600 space-y-1">
            <div><code>&lt;Alex&gt; Welcome to our show!</code></div>
            <div><code>&lt;Sarah&gt; Thanks for having me, Alex.</code></div>
          </div>
        </div>

        {/* Script textarea */}
        <div>
          <textarea
            value={script}
            onChange={(e) => onScriptChange(e.target.value)}
            placeholder="Enter your dialogue script here...

<Alex> Welcome to Mysteries of the Mind, I'm Alex.
<Rowan> And I'm Rowan, ready to explore today's fascinating topic.
<Alex> Today we're diving into something extraordinary..."
            className={`textarea min-h-[300px] font-mono text-sm ${
              !validation.isValid ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''
            }`}
            rows={12}
          />
        </div>

        {/* Validation errors */}
        {!validation.isValid && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex items-center space-x-2 mb-2">
              <AlertCircle className="w-4 h-4 text-red-600" />
              <span className="text-sm font-medium text-red-900">Script Issues</span>
            </div>
            <ul className="text-sm text-red-700 space-y-1">
              {validation.errors.map((error, index) => (
                <li key={index}>• {error}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600">{stats.characters} chars</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">{stats.words} words</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600">{stats.lines} lines</span>
          </div>
          <div className="flex items-center space-x-2">
            <Users className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600">{stats.speakers} speakers</span>
          </div>
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600">~{formatDuration(stats.estimatedDuration)}</span>
          </div>
        </div>

        {/* Speaker preview */}
        {stats.speakers > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <h4 className="text-sm font-medium text-green-900 mb-2">Detected Speakers</h4>
            <div className="flex flex-wrap gap-2">
              {detectedSpeakers.map((speaker) => (
                <span key={speaker} className="badge-success">
                  {speaker}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 