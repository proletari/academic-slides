import React, { useCallback, useState } from 'react';
import { Upload, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface PaperUploaderProps {
  onPaperUploaded: (paper: any) => void;
  onError: (error: string) => void;
}

export function PaperUploader({ onPaperUploaded, onError }: PaperUploaderProps) {
  const [status, setStatus] = useState<'idle' | 'uploading' | 'parsing' | 'success' | 'error'>('idle');
  const [fileName, setFileName] = useState<string>('');

  const handleFile = useCallback(async (file: File) => {
    if (!file.name.endsWith('.pdf')) {
      onError('Only PDF files are supported');
      return;
    }

    setFileName(file.name);
    setStatus('uploading');

    const formData = new FormData();
    formData.append('file', file);

    try {
      setStatus('parsing');
      const resp = await fetch('/api/papers', {
        method: 'POST',
        body: formData,
      });

      if (!resp.ok) {
        const data = await resp.json();
        throw new Error(data.error || 'Upload failed');
      }

      const result = await resp.json();
      setStatus('success');
      onPaperUploaded(result);
    } catch (err: any) {
      setStatus('error');
      onError(err.message || 'Failed to upload paper');
    }
  }, [onPaperUploaded, onError]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }, [handleFile]);

  return (
    <div
      className="border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer hover:border-blue-400 dark:hover:border-blue-500"
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
    >
      {status === 'idle' && (
        <label className="flex flex-col items-center gap-3 cursor-pointer">
          <Upload className="w-10 h-10 text-gray-400" />
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Click or drag to upload paper PDF
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Supports .pdf — AI will extract sections, figures, and references
            </p>
          </div>
          <input
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={handleInputChange}
          />
        </label>
      )}

      {(status === 'uploading' || status === 'parsing') && (
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {status === 'uploading' ? 'Uploading...' : 'Parsing paper...'}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {fileName}
            </p>
          </div>
        </div>
      )}

      {status === 'success' && (
        <div className="flex flex-col items-center gap-3">
          <CheckCircle className="w-10 h-10 text-green-500" />
          <div>
            <p className="text-sm font-medium text-green-700 dark:text-green-400">
              Paper parsed successfully
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {fileName}
            </p>
          </div>
        </div>
      )}

      {status === 'error' && (
        <div className="flex flex-col items-center gap-3">
          <AlertCircle className="w-10 h-10 text-red-500" />
          <div>
            <p className="text-sm font-medium text-red-700 dark:text-red-400">
              Failed to parse paper
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {fileName}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
