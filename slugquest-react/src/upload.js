import React from 'react';

const Upload = ({ onUpload }) => (
  <div className="flex justify-center items-center h-screen bg-green-200">
    <form
      className="bg-white p-6 rounded shadow-md"
      onSubmit={(e) => {
        e.preventDefault();
        onUpload();
      }}
    >
      <h2 className="text-xl mb-4">Upload Transcript</h2>
      <input type="file" required className="mb-4" />
      <button type="submit" className="bg-green-500 text-white px-4 py-2 rounded">Upload</button>
    </form>
  </div>
);

export default Upload;
