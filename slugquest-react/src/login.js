import React from 'react';

const Login = ({ onLogin }) => (
  <div className="flex justify-center items-center h-screen bg-blue-200">
    <form
      className="bg-white p-6 rounded shadow-md"
      onSubmit={(e) => {
        e.preventDefault();
        onLogin();
      }}
    >
      <h2 className="text-xl mb-4">Login</h2>
      <input type="text" placeholder="Username" required className="mb-2 p-2 border border-gray-300 rounded w-full" />
      <input type="password" placeholder="Password" required className="mb-4 p-2 border border-gray-300 rounded w-full" />
      <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">Login</button>
    </form>
  </div>
);

export default Login;
