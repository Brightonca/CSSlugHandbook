import React, { useState } from 'react';
import Login from './login';
import Upload from './upload';
import CourseMap from './courseMap';

const App = () => {
  const [loggedIn, setLoggedIn] = useState(true);
  const [uploaded, setUploaded] = useState(true);

  if (!loggedIn) {
    return <Login onLogin={() => setLoggedIn(true)} />;
  }

  if (!uploaded) {
    return <Upload onUpload={() => setUploaded(true)} />;
  }

  return <>
    <div className="topnav">
      <CourseMap />
    </div>
  </>;
};

export default App;
