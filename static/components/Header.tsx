
import React, { useState, useEffect, useRef } from 'react';

export const Header: React.FC = () => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const toggleDropdown = () => setIsDropdownOpen(!isDropdownOpen);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropdownOpen]);

  return (
    <header className="w-full bg-white dark:bg-gray-900 shadow-md sticky top-0 z-50">
      <div className="container mx-auto px-4 md:px-8 py-4 flex items-center justify-between max-w-6xl">
        <div className="flex items-center space-x-2">
           <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8 text-primary">
            <path d="M10.561 3.439a8.25 8.25 0 0 0-8.25 8.25c0 1.637.483 3.156 1.334 4.495A8.223 8.223 0 0 0 1.5 20.25a.75.75 0 0 0 .75.75H10.5a.75.75 0 0 0 .75-.75v-3a.75.75 0 0 0-.75-.75H7.531A6.726 6.726 0 0 1 3.75 11.69c0-3.692 2.972-6.694 6.64-6.748a.75.75 0 0 0 .17-1.493ZM17.25 10.5a.75.75 0 0 0-.75.75v5.018A6.726 6.726 0 0 1 20.25 12c0-3.692-2.972-6.694-6.64-6.748a.75.75 0 0 0 .17-1.493A8.25 8.25 0 0 0 17.25 10.5Z" />
            <path d="M21.666 16.205A8.25 8.25 0 0 0 22.5 11.69a8.204 8.204 0 0 0-1.439-4.703.75.75 0 0 0-1.218.86A6.704 6.704 0 0 1 21 11.69c0 1.611-.466 3.104-1.278 4.422a.75.75 0 0 0 .844 1.153Z" />
          </svg>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-800 dark:text-white">
            Stock Predictor
          </h1>
        </div>
        
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={toggleDropdown}
            className="p-2 rounded-full text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100 dark:focus:ring-offset-gray-800 focus:ring-primary"
            aria-label="User menu"
            aria-expanded={isDropdownOpen}
            aria-haspopup="true"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
              <path fillRule="evenodd" d="M18.685 19.097A9.723 9.723 0 0 0 21.75 12c0-5.385-4.365-9.75-9.75-9.75S2.25 6.615 2.25 12a9.723 9.723 0 0 0 3.065 7.097A9.716 9.716 0 0 0 12 21.75a9.716 9.716 0 0 0 6.685-2.653Zm-12.54-1.285A7.486 7.486 0 0 1 12 15a7.486 7.486 0 0 1 5.855 2.812A8.224 8.224 0 0 1 12 20.25a8.224 8.224 0 0 1-5.855-2.438ZM15.75 9a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z" clipRule="evenodd" />
            </svg>
          </button>
          {isDropdownOpen && (
            <div 
              className="absolute right-0 mt-2 w-56 origin-top-right bg-white dark:bg-gray-800 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none py-1"
              role="menu" 
              aria-orientation="vertical" 
              aria-labelledby="user-menu-button" 
              tabIndex={-1}
            >
              <div className="px-4 py-2 text-sm text-gray-700 dark:text-gray-200" role="menuitem" tabIndex={-1}>
                Done by Harsha Kyle
              </div>
              <div className="px-4 py-2 text-sm text-gray-700 dark:text-gray-200" role="menuitem" tabIndex={-1}>
                College: Saveetha
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
