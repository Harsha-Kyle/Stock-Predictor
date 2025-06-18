
import React from 'react';

interface ErrorDisplayProps {
  message: string;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ message }) => {
  return (
    <div role="alert" className="p-6 bg-red-50 dark:bg-red-900 border border-red-300 dark:border-red-700 rounded-xl shadow-lg my-8">
      <div className="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-6 h-6 text-red-500 dark:text-red-300 mr-3">
          <path fillRule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm-.707-4.293a1 1 0 0 0 1.414 0L12 12.414l1.293 1.293a1 1 0 0 0 1.414-1.414L13.414 11l1.293-1.293a1 1 0 0 0-1.414-1.414L12 9.586l-1.293-1.293a1 1 0 0 0-1.414 1.414L10.586 11l-1.293 1.293a1 1 0 0 0 0 1.414Z" clipRule="evenodd" />
        </svg>
        <div>
          <h3 className="text-lg font-semibold text-red-700 dark:text-red-200">Error</h3>
          <p className="text-sm text-red-600 dark:text-red-300">{message}</p>
        </div>
      </div>
    </div>
  );
};
