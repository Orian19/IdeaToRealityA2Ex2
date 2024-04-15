"use client";

import Image from "next/image";
import { useState } from "react";

export default function Home() {
  const [productName, setProductName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };  

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true); // Start loading
  
    setSearchHistory([productName, ...searchHistory].slice(0, 10)); // Save only the last 10 searches
  
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
      // Add the search term and results to the history
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
    <main className="flex min-h-screen items-center justify-center bg-gray-50 py-10 px-4">
      <div className="flex w-full max-w-6xl">
        {/* Search History Section */}
        <div className="hidden md:block w-1/4 mr-4 p-4 bg-white shadow overflow-hidden rounded-lg">
          <h2 className="font-bold text-lg text-gray-900 mb-4">Search History</h2>
          <ul className="text-sm text-gray-900">
            {searchHistory.map((historyItem, index) => (
              <li key={index} className="truncate cursor-pointer" onClick={() => handleSelectHistoryItem(historyItem)}>
                {historyItem.term}
              </li>
            ))}
          </ul>
        </div>

  
        {/* Main Content Area */}
        <div className="flex-grow">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Product Price Comparison</h1>
          <div className="my-8 w-full max-w-md">
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <input
                type="text"
                placeholder="Enter product name"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                className="w-full rounded-md border border-gray-300 p-2 text-lg text-gray-900"
              />
              <button type="submit" className="w-full rounded-md bg-blue-500 py-2 px-4 text-lg text-white hover:bg-blue-600">
                Search
              </button>
            </form>
          </div>
          {isLoading ? (
            <div className="text-lg font-semibold text-green-700">Fetching Results...</div>
          ) : results.length > 0 ? (
            <div className="my-8 w-full max-w-4xl overflow-x-auto">
              <table className="w-full border-collapse border border-gray-200">
                <thead className="bg-gray-200">
                  <tr>
                    <th className="border border-gray-300 px-4 py-2 text-left text-lg font-semibold text-gray-700">Site</th>
                    <th className="border border-gray-300 px-4 py-2 text-left text-lg font-semibold text-gray-700">Item</th>
                    <th className="border border-gray-300 px-4 py-2 text-left text-lg font-semibold text-gray-700">Price(USD)</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((result, index) => (
                    <tr key={index} className="even:bg-gray-50">
                      <td className="border border-gray-300 px-4 py-2 text-lg text-gray-900">{result.Site}</td>
                      <td className="border border-gray-300 px-4 py-2 text-lg text-blue-600 hover:text-blue-800">
                        <a href={result['Item URL']} target="_blank" rel="noopener noreferrer">
                          {result['Item Title Name']}
                        </a>
                      </td>
                      <td className="border border-gray-300 px-4 py-2 text-lg text-gray-900">{result['Price(USD)']}</td>
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
