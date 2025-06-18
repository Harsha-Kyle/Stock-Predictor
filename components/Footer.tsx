import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 mt-auto">
      <div className="container mx-auto px-4 md:px-8 py-6 text-center text-gray-500 dark:text-gray-400 max-w-6xl">
        <p>&copy; 2025 Stock Predictor. All rights reserved.</p>
        <p className="text-sm mt-1">
          Disclaimer: Predictions are for informational purposes only and not financial advice.
        </p>
      </div>
    </footer>
  );
};