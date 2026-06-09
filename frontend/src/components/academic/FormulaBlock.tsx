import React, { useEffect, useRef } from 'react';

// KaTeX will be loaded dynamically
let katexPromise: Promise<any> | null = null;

function loadKatex(): Promise<any> {
  if (katexPromise) return katexPromise;

  katexPromise = new Promise((resolve, reject) => {
    // Check if already loaded
    if (typeof (window as any).katex !== 'undefined') {
      resolve((window as any).katex);
      return;
    }

    // Load CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css';
    document.head.appendChild(link);

    // Load JS
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js';
    script.onload = () => resolve((window as any).katex);
    script.onerror = reject;
    document.head.appendChild(script);
  });

  return katexPromise;
}

interface FormulaBlockProps {
  formula: string;
  display?: boolean;
  className?: string;
}

export function FormulaBlock({ formula, display = false, className = '' }: FormulaBlockProps) {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!ref.current || !formula) return;

    loadKatex().then((katex) => {
      try {
        katex.render(formula, ref.current!, {
          displayMode: display,
          throwOnError: false,
          trust: true,
        });
      } catch (err) {
        if (ref.current) {
          ref.current.textContent = formula;
        }
      }
    }).catch(() => {
      if (ref.current) {
        ref.current.textContent = formula;
      }
    });
  }, [formula, display]);

  return (
    <span
      ref={ref}
      className={`formula-block ${display ? 'block text-center my-4' : 'inline'} ${className}`}
    >
      {formula}
    </span>
  );
}

/**
 * Process markdown text and render LaTeX formulas.
 * Supports $...$ for inline and $$...$$ for display math.
 */
export function renderMathInText(text: string): React.ReactNode {
  if (!text) return null;

  const parts: React.ReactNode[] = [];
  let remaining = text;
  let key = 0;

  while (remaining.length > 0) {
    // Look for display math first: $$...$$
    const displayMatch = remaining.match(/\$\$(.+?)\$\$/s);
    // Look for inline math: $...$
    const inlineMatch = remaining.match(/\$(.+?)\$/);

    // Find the earliest match
    let earliestMatch: { type: 'display' | 'inline'; index: number; content: string } | null = null;

    if (displayMatch && displayMatch.index !== undefined) {
      earliestMatch = { type: 'display', index: displayMatch.index, content: displayMatch[1] };
    }
    if (inlineMatch && inlineMatch.index !== undefined) {
      if (!earliestMatch || inlineMatch.index < earliestMatch.index) {
        earliestMatch = { type: 'inline', index: inlineMatch.index, content: inlineMatch[1] };
      }
    }

    if (!earliestMatch) {
      parts.push(<span key={key++}>{remaining}</span>);
      break;
    }

    // Add text before the match
    if (earliestMatch.index > 0) {
      parts.push(<span key={key++}>{remaining.slice(0, earliestMatch.index)}</span>);
    }

    // Add the formula
    parts.push(
      <FormulaBlock
        key={key++}
        formula={earliestMatch.content}
        display={earliestMatch.type === 'display'}
      />
    );

    // Move past the match
    const matchLength = earliestMatch.type === 'display'
      ? earliestMatch.content.length + 4  // $$ + content + $$
      : earliestMatch.content.length + 2; // $ + content + $
    remaining = remaining.slice(earliestMatch.index + matchLength);
  }

  return parts.length === 1 ? parts[0] : <>{parts}</>;
}
