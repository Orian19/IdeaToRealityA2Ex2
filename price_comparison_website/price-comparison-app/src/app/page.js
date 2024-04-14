"use client";

import Image from "next/image";
import { useState } from "react";

export default function Home() {
  const [productName, setProductName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true); // Start loading
    const response = await fetch('http://127.0.0.1:8001/scrape/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({productName: productName}),
    });

    if (response.ok) {
      const data = await response.json();
      setResults(data);
    } else {
      console.error("Failed to fetch data");
      setResults([]);
    }
    setIsLoading(false); // Stop loading
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-50 py-10 px-4">
      <h1 className="text-3xl font-bold text-gray-900">Product Price Comparison</h1>
      <div className="my-8 w-full max-w-md">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="text"
            placeholder="Enter product name"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            className="w-full rounded-md border border-gray-300 p-2 text-lg text-gray-900"
          />
          <button type="submit" className="rounded-md bg-blue-500 py-2 px-4 text-lg text-white hover:bg-blue-600">Search</button>
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
                    {/* Update href to use result['Item URL'] */}
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
    </main>
  );
}
