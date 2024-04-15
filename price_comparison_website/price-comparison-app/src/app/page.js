"use client";

import React, { useState, useEffect } from 'react';

export default function Home() {
  const [productName, setProductName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);
  const [darkMode, setDarkMode] = useState(false);

  const handleButtonClick = () => {
    setDarkMode(prevDarkMode => !prevDarkMode);
  };

  useEffect(() => {
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    setDarkMode(isDarkMode);
  }, []);

  useEffect(() => {
    localStorage.setItem('darkMode', darkMode.toString());
    document.body.classList.toggle('dark', darkMode);
  }, [darkMode]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
  
    setSearchHistory([productName, ...searchHistory].slice(0, 10));

    const response = await fetch('http://127.0.0.1:8001/scrape/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ productName: productName }),
    });
  
    if (response.ok) {
      const data = await response.json();
      setResults(data);
      setSearchHistory(history => [{ term: productName, data }, ...history]);
    } else {
      console.error("Failed to fetch data");
      setResults([]);
    }
    setIsLoading(false); // Stop loading
  };    

  const handleSelectHistoryItem = (historyItem) => {
    setProductName(historyItem.term);
    setResults(historyItem.data);
  };
  
  return (
    <main className={`flex min-h-screen items-center justify-center ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-black'}`}>
      <div>
        <button 
          className={`fixed top-5 right-5 bg-blue-500 dark:bg-blue-700 text-white p-2 rounded ${darkMode ? 'dark:bg-blue-700' : 'bg-blue-500'}`}
          onClick={handleButtonClick}>
            {darkMode ? 'Light Mode' : 'Dark Mode'}
        </button>
      </div>
      <div className="flex w-full max-w-6xl">
        {/* Search History Section */}
        <div className={`hidden md:block w-1/4 mr-4 p-4 ${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-black'} shadow overflow-hidden rounded-lg`}>
          <h2 className="font-bold text-lg mb-4">Search History</h2>
          <ul className="text-sm">
            {searchHistory.map((historyItem, index) => (
              <li key={index} className="truncate cursor-pointer" onClick={() => handleSelectHistoryItem(historyItem)}>
                {historyItem.term}
              </li>
            ))}
          </ul>
        </div>

        {/* Main Content Area */}
        <div className="flex-grow">
          <h1 className={`text-3xl font-bold mb-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>Product Price Comparison</h1>
          <div className="my-8 w-full max-w-md">
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <input
                type="text"
                placeholder="Enter product name"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                className={`w-full rounded-md border p-2 text-lg ${darkMode ? 'bg-gray-800 border-gray-600 text-gray-300' : 'border-gray-300 text-gray-900'}`}
              />
              <button type="submit" className={`w-full rounded-md py-2 px-4 text-lg text-white ${darkMode ? 'bg-gray-600 hover:bg-gray-700' : 'bg-blue-500 hover:bg-blue-600'}`}>
                Search
              </button>
            </form>
          </div>
          {isLoading ? (
            <div className="text-lg font-semibold text-green-700">Fetching Results...</div>
          ) : results.length > 0 ? (
            <div className="my-8 w-full max-w-4xl overflow-x-auto">
              <table className={`w-full border-collapse border ${darkMode ? 'bg-gray-800 text-gray-300' : 'bg-white text-gray-900'}`}>
                <thead className="bg-gray-200">
                  <tr>
                    <th className="border px-4 py-2 text-lg font-semibold">Site</th>
                    <th className="border px-4 py-2 text-lg font-semibold">Item</th>
                    <th className="border px-4 py-2 text-lg font-semibold">Price(USD)</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((result, index) => (
                    <tr key={index} className={`${index % 2 === 0 ? 'bg-gray-100' : ''}`}>
                      <td className="border px-4 py-2 text-lg">{result.Site}</td>
                      <td className="border px-4 py-2 text-lg">
                        <a href={result['Item URL']} target="_blank" rel="noopener noreferrer" className={`hover:text-blue-600 ${darkMode ? 'text-blue-400' : 'text-blue-700'}`}>
                          {result['Item Title Name']}
                        </a>
                      </td>
                      <td className="border px-4 py-2 text-lg">{result['Price(USD)']}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-lg font-semibold">No results found.</div>
          )}
        </div>
      </div>
    </main>
  );
}

