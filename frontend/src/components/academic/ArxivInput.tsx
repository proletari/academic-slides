import React, { useState, useCallback } from 'react';
import { Loader2, CheckCircle, AlertCircle, BookOpen } from 'lucide-react';

interface ArxivInputProps {
  onPaperFetched: (paper: any) => void;
  onError: (error: string) => void;
}

export function ArxivInput({ onPaperFetched, onError }: ArxivInputProps) {
  const [arxivId, setArxivId] = useState('');
  const [status, setStatus] = useState<'idle' | 'fetching' | 'success' | 'error'>('idle');
  const [paperTitle, setPaperTitle] = useState('');

  const handleFetch = useCallback(async () => {
    const id = arxivId.trim();
    if (!id) {
      onError('Please enter an arXiv ID');
      return;
    }

    setStatus('fetching');
    try {
      const resp = await fetch('/api/papers/arxiv', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ arxiv_id: id }),
      });

      if (!resp.ok) {
        const data = await resp.json();
        throw new Error(data.error || 'Failed to fetch paper');
      }

      const result = await resp.json();
      setPaperTitle(result.data?.title || '');
      setStatus('success');
      onPaperFetched(result);
    } catch (err: any) {
      setStatus('error');
      onError(err.message || 'Failed to fetch arXiv paper');
    }
  }, [arxivId, onPaperFetched, onError]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleFetch();
    }
  }, [handleFetch]);

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input
          type="text"
          value={arxivId}
          onChange={(e) => setArxivId(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="e.g., 2301.07041"
          className="flex-1 px-4 py-2 border rounded-lg bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={status === 'fetching'}
        />
        <button
          onClick={handleFetch}
          disabled={status === 'fetching' || !arxivId.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {status === 'fetching' ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <BookOpen className="w-4 h-4" />
          )}
          Fetch
        </button>
      </div>

      {status === 'success' && paperTitle && (
        <div className="flex items-start gap-2 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm text-green-700 dark:text-green-400 font-medium">
              Paper found
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              {paperTitle}
            </p>
          </div>
        </div>
      )}

      {status === 'error' && (
        <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
          <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
          <p className="text-sm text-red-700 dark:text-red-400">
            Failed to fetch paper. Check the arXiv ID and try again.
          </p>
        </div>
      )}
    </div>
  );
}
