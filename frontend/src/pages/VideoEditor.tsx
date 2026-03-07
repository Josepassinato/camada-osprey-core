import React, { useState, useCallback } from 'react';
import { makeApiCall, getApiUrl } from '@/utils/api';

// ============================================================================
// Types
// ============================================================================

interface UploadedFile {
  file_id: string;
  original_name: string;
  size: number;
  extension: string;
}

interface VideoProbe {
  duration: number;
  width: number;
  height: number;
  fps: number;
  codec: string;
  audio_codec: string | null;
  file_size: number;
  bitrate: number;
}

interface VideoOperation {
  type: string;
  [key: string]: any;
}

interface VideoJob {
  job_id: string;
  project_id: string | null;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  output_url?: string;
  error?: string;
}

// ============================================================================
// API Functions
// ============================================================================

async function uploadMediaFile(file: File): Promise<UploadedFile> {
  const formData = new FormData();
  formData.append('file', file);

  const url = getApiUrl('/video/upload');
  const token = localStorage.getItem('osprey_token');

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(err.detail || `Upload failed: ${response.status}`);
  }

  return response.json();
}

async function probeFile(fileId: string): Promise<VideoProbe> {
  return makeApiCall(`/video/probe/${fileId}`, 'GET');
}

async function executePipeline(pipeline: any): Promise<VideoJob> {
  return makeApiCall('/video/execute', 'POST', pipeline);
}

// ============================================================================
// Operation Templates
// ============================================================================

const OPERATION_TEMPLATES: { label: string; type: string; defaults: Record<string, any> }[] = [
  { label: 'Trim', type: 'trim', defaults: { start: 0, end: 10 } },
  { label: 'Text Overlay', type: 'text_overlay', defaults: { text: 'Hello', position: 'bottom_center', font_size: 24, font_color: 'white' } },
  { label: 'Speed', type: 'speed', defaults: { factor: 1.5 } },
  { label: 'Resize', type: 'resize', defaults: { width: 1280, maintain_aspect: true } },
  { label: 'Crop', type: 'crop', defaults: { x: 0, y: 0, width: 640, height: 480 } },
  { label: 'Rotate', type: 'rotate', defaults: { degrees: 90 } },
  { label: 'Filter', type: 'filter', defaults: { filter_type: 'grayscale', intensity: 1.0 } },
  { label: 'Extract Frames', type: 'extract_frames', defaults: { interval: 5, format: 'png' } },
];

// ============================================================================
// Component
// ============================================================================

export default function VideoEditor() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [probeData, setProbeData] = useState<Record<string, VideoProbe>>({});
  const [selectedFileId, setSelectedFileId] = useState<string>('');
  const [operations, setOperations] = useState<VideoOperation[]>([]);
  const [exportSettings, setExportSettings] = useState({
    format: 'mp4',
    video_codec: 'libx264',
    audio_codec: 'aac',
    quality: 23,
  });
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastJob, setLastJob] = useState<VideoJob | null>(null);
  const [error, setError] = useState<string>('');

  const handleUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError('');
    try {
      const uploaded = await uploadMediaFile(file);
      setFiles((prev) => [...prev, uploaded]);
      if (!selectedFileId) setSelectedFileId(uploaded.file_id);

      // Auto-probe video files
      if (['.mp4', '.mov', '.avi', '.mkv', '.webm'].includes(uploaded.extension)) {
        const probe = await probeFile(uploaded.file_id);
        setProbeData((prev) => ({ ...prev, [uploaded.file_id]: probe }));
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  }, [selectedFileId]);

  const addOperation = useCallback((template: typeof OPERATION_TEMPLATES[0]) => {
    setOperations((prev) => [...prev, { type: template.type, ...template.defaults }]);
  }, []);

  const removeOperation = useCallback((index: number) => {
    setOperations((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const updateOperation = useCallback((index: number, field: string, value: any) => {
    setOperations((prev) =>
      prev.map((op, i) => (i === index ? { ...op, [field]: value } : op))
    );
  }, []);

  const moveOperation = useCallback((index: number, direction: -1 | 1) => {
    setOperations((prev) => {
      const newOps = [...prev];
      const targetIndex = index + direction;
      if (targetIndex < 0 || targetIndex >= newOps.length) return prev;
      [newOps[index], newOps[targetIndex]] = [newOps[targetIndex], newOps[index]];
      return newOps;
    });
  }, []);

  const handleExecute = useCallback(async () => {
    if (!selectedFileId || operations.length === 0) {
      setError('Select a file and add at least one operation');
      return;
    }

    setIsProcessing(true);
    setError('');
    setLastJob(null);

    try {
      const pipeline = {
        input_key: selectedFileId,
        operations,
        export_settings: exportSettings,
      };
      const job = await executePipeline(pipeline);
      setLastJob(job);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  }, [selectedFileId, operations, exportSettings]);

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDuration = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold">Video Editor</h1>
        <p className="text-gray-400">Upload media, compose operations, and export your edited video.</p>

        {error && (
          <div className="bg-red-900/50 border border-red-700 text-red-200 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Upload Section */}
        <section className="bg-gray-900 rounded-lg p-6 space-y-4">
          <h2 className="text-xl font-semibold">Media Files</h2>
          <label className="inline-block cursor-pointer bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm font-medium transition">
            {isUploading ? 'Uploading...' : 'Upload File'}
            <input
              type="file"
              className="hidden"
              accept="video/*,audio/*,image/*"
              onChange={handleUpload}
              disabled={isUploading}
            />
          </label>

          {files.length > 0 && (
            <div className="space-y-2">
              {files.map((f) => (
                <div
                  key={f.file_id}
                  className={`flex items-center justify-between p-3 rounded cursor-pointer transition ${
                    selectedFileId === f.file_id
                      ? 'bg-blue-900/40 border border-blue-600'
                      : 'bg-gray-800 hover:bg-gray-750 border border-transparent'
                  }`}
                  onClick={() => setSelectedFileId(f.file_id)}
                >
                  <div>
                    <span className="font-medium">{f.original_name}</span>
                    <span className="text-gray-400 text-sm ml-2">({formatBytes(f.size)})</span>
                  </div>
                  {probeData[f.file_id] && (
                    <div className="text-xs text-gray-400 space-x-3">
                      <span>{probeData[f.file_id].width}x{probeData[f.file_id].height}</span>
                      <span>{probeData[f.file_id].fps} fps</span>
                      <span>{formatDuration(probeData[f.file_id].duration)}</span>
                      <span>{probeData[f.file_id].codec}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Operations Pipeline */}
        <section className="bg-gray-900 rounded-lg p-6 space-y-4">
          <h2 className="text-xl font-semibold">Pipeline</h2>

          <div className="flex flex-wrap gap-2">
            {OPERATION_TEMPLATES.map((t) => (
              <button
                key={t.type}
                className="bg-gray-700 hover:bg-gray-600 px-3 py-1.5 rounded text-sm transition"
                onClick={() => addOperation(t)}
              >
                + {t.label}
              </button>
            ))}
          </div>

          {operations.length === 0 && (
            <p className="text-gray-500 text-sm">No operations added yet. Click an operation above to start building your pipeline.</p>
          )}

          <div className="space-y-3">
            {operations.map((op, i) => (
              <div key={i} className="bg-gray-800 rounded p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-blue-400 capitalize">
                    {i + 1}. {op.type.replace('_', ' ')}
                  </span>
                  <div className="flex gap-1">
                    <button
                      className="text-gray-400 hover:text-white px-2 py-1 text-sm"
                      onClick={() => moveOperation(i, -1)}
                      disabled={i === 0}
                    >
                      Up
                    </button>
                    <button
                      className="text-gray-400 hover:text-white px-2 py-1 text-sm"
                      onClick={() => moveOperation(i, 1)}
                      disabled={i === operations.length - 1}
                    >
                      Down
                    </button>
                    <button
                      className="text-red-400 hover:text-red-300 px-2 py-1 text-sm"
                      onClick={() => removeOperation(i)}
                    >
                      Remove
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  {Object.entries(op)
                    .filter(([key]) => key !== 'type')
                    .map(([key, value]) => (
                      <div key={key}>
                        <label className="block text-gray-400 text-xs mb-1">{key}</label>
                        {typeof value === 'boolean' ? (
                          <input
                            type="checkbox"
                            checked={value}
                            onChange={(e) => updateOperation(i, key, e.target.checked)}
                            className="accent-blue-500"
                          />
                        ) : typeof value === 'number' ? (
                          <input
                            type="number"
                            value={value}
                            onChange={(e) => updateOperation(i, key, parseFloat(e.target.value) || 0)}
                            className="w-full bg-gray-700 text-white px-2 py-1 rounded border border-gray-600"
                          />
                        ) : (
                          <input
                            type="text"
                            value={String(value)}
                            onChange={(e) => updateOperation(i, key, e.target.value)}
                            className="w-full bg-gray-700 text-white px-2 py-1 rounded border border-gray-600"
                          />
                        )}
                      </div>
                    ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Export Settings */}
        <section className="bg-gray-900 rounded-lg p-6 space-y-4">
          <h2 className="text-xl font-semibold">Export Settings</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <label className="block text-gray-400 text-xs mb-1">Format</label>
              <select
                value={exportSettings.format}
                onChange={(e) => setExportSettings((s) => ({ ...s, format: e.target.value }))}
                className="w-full bg-gray-800 text-white px-2 py-1.5 rounded border border-gray-600"
              >
                <option value="mp4">MP4</option>
                <option value="webm">WebM</option>
                <option value="mov">MOV</option>
                <option value="mkv">MKV</option>
                <option value="gif">GIF</option>
              </select>
            </div>
            <div>
              <label className="block text-gray-400 text-xs mb-1">Video Codec</label>
              <select
                value={exportSettings.video_codec}
                onChange={(e) => setExportSettings((s) => ({ ...s, video_codec: e.target.value }))}
                className="w-full bg-gray-800 text-white px-2 py-1.5 rounded border border-gray-600"
              >
                <option value="libx264">H.264</option>
                <option value="libx265">H.265</option>
                <option value="libvpx-vp9">VP9</option>
                <option value="copy">Copy (no re-encode)</option>
              </select>
            </div>
            <div>
              <label className="block text-gray-400 text-xs mb-1">Audio Codec</label>
              <select
                value={exportSettings.audio_codec}
                onChange={(e) => setExportSettings((s) => ({ ...s, audio_codec: e.target.value }))}
                className="w-full bg-gray-800 text-white px-2 py-1.5 rounded border border-gray-600"
              >
                <option value="aac">AAC</option>
                <option value="libmp3lame">MP3</option>
                <option value="libopus">Opus</option>
                <option value="copy">Copy</option>
                <option value="none">No Audio</option>
              </select>
            </div>
            <div>
              <label className="block text-gray-400 text-xs mb-1">Quality (CRF)</label>
              <input
                type="number"
                value={exportSettings.quality}
                min={0}
                max={51}
                onChange={(e) => setExportSettings((s) => ({ ...s, quality: parseInt(e.target.value) || 23 }))}
                className="w-full bg-gray-800 text-white px-2 py-1.5 rounded border border-gray-600"
              />
            </div>
          </div>
        </section>

        {/* Execute */}
        <div className="flex items-center gap-4">
          <button
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed px-6 py-3 rounded-lg font-semibold text-lg transition"
            onClick={handleExecute}
            disabled={isProcessing || !selectedFileId || operations.length === 0}
          >
            {isProcessing ? 'Processing...' : 'Execute Pipeline'}
          </button>

          {lastJob && (
            <div className={`text-sm ${lastJob.status === 'completed' ? 'text-green-400' : 'text-red-400'}`}>
              {lastJob.status === 'completed' ? (
                <span>
                  Done!{' '}
                  <a
                    href={`${getApiUrl('')}${lastJob.output_url?.replace('/api', '')}`}
                    className="underline hover:text-green-300"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Download output
                  </a>
                </span>
              ) : (
                <span>Failed: {lastJob.error}</span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
