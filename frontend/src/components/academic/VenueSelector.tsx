import React from 'react';
import { GraduationCap, Mic, Users, BookOpen } from 'lucide-react';
import { useT } from '@/hooks/useT';

const venueI18n = {
  zh: {
    conference: { name: '学术会议', description: 'NeurIPS, ICML, ICLR, ACL, KDD' },
    thesis: { name: '学位答辩', description: '博士/硕士学位答辩' },
    meeting: { name: '组会报告', description: '实验室组会、进展汇报' },
    lecture: { name: '课程讲座', description: '教学、Tutorial、Workshop' },
  },
  en: {
    conference: { name: 'Conference Talk', description: 'NeurIPS, ICML, ICLR, ACL, KDD' },
    thesis: { name: 'Thesis Defense', description: 'PhD/Master defense presentation' },
    meeting: { name: 'Group Meeting', description: 'Lab meeting, progress update' },
    lecture: { name: 'Lecture', description: 'Teaching, tutorial, workshop' },
  },
};

interface Venue {
  id: string;
  icon: React.ReactNode;
}

const VENUES: Venue[] = [
  { id: 'conference', icon: <Mic className="w-4 h-4" /> },
  { id: 'thesis', icon: <GraduationCap className="w-4 h-4" /> },
  { id: 'meeting', icon: <Users className="w-4 h-4" /> },
  { id: 'lecture', icon: <BookOpen className="w-4 h-4" /> },
];

interface VenueSelectorProps {
  value: string;
  onChange: (venue: string) => void;
}

export function VenueSelector({ value, onChange }: VenueSelectorProps) {
  const t = useT(venueI18n);

  return (
    <div className="grid grid-cols-2 gap-2">
      {VENUES.map((venue) => (
        <button
          key={venue.id}
          onClick={() => onChange(venue.id)}
          className={`flex items-start gap-3 p-3 rounded-lg border text-left transition-colors ${
            value === venue.id
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
          }`}
        >
          <div className={`mt-0.5 ${value === venue.id ? 'text-blue-600 dark:text-blue-400' : 'text-gray-400'}`}>
            {venue.icon}
          </div>
          <div>
            <p className={`text-sm font-medium ${value === venue.id ? 'text-blue-700 dark:text-blue-300' : 'text-gray-700 dark:text-gray-300'}`}>
              {t(`${venue.id}.name`)}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              {t(`${venue.id}.description`)}
            </p>
          </div>
        </button>
      ))}
    </div>
  );
}
