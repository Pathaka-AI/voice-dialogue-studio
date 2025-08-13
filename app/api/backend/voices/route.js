import { NextResponse } from 'next/server';

// Proxy to your Python backend for voice listing
export async function GET(request) {
  try {
    // Call your Python backend's list_voices function
    // This would integrate with your neuphonic_backend.py
    
    // For now, let's create a direct integration approach
    // You can replace this with actual subprocess calls to your Python backend
    // or expose your Python backend as a REST API
    
    const { spawn } = await import('child_process');
    
    return new Promise((resolve) => {
      const pythonProcess = spawn('python3', [
        '-c',
        `
import sys
import os
sys.path.append('${process.cwd()}')
from neuphonic_backend import NeuphonicBackend
import json

try:
    backend = NeuphonicBackend()
    voices = backend.list_voices()
    result = {
        "voices": voices,
        "status": "success"
    }
    print(json.dumps(result))
except Exception as e:
    result = {
        "error": str(e),
        "status": "error"
    }
    print(json.dumps(result))
        `
      ]);

      let output = '';
      let errorOutput = '';

      pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });

      pythonProcess.on('close', (code) => {
        try {
          if (code !== 0) {
            console.error('Python process error:', errorOutput);
            resolve(NextResponse.json(
              { error: 'Backend process failed', details: errorOutput },
              { status: 500 }
            ));
            return;
          }

          const result = JSON.parse(output.trim());
          
          if (result.status === 'error') {
            resolve(NextResponse.json(
              { error: result.error },
              { status: 500 }
            ));
            return;
          }

          resolve(NextResponse.json(result));
        } catch (parseError) {
          console.error('Failed to parse Python output:', parseError);
          console.error('Raw output:', output);
          resolve(NextResponse.json(
            { error: 'Failed to parse backend response', details: output },
            { status: 500 }
          ));
        }
      });
    });

  } catch (error) {
    console.error('Voice listing error:', error);
    return NextResponse.json(
      { error: 'Failed to list voices', details: error.message },
      { status: 500 }
    );
  }
} 