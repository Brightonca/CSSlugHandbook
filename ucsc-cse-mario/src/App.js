import React, { useState } from 'react';
import Login from './login';
import Upload from './upload';
import CourseMap from './courseMap';

const App = () => {
  const [loggedIn, setLoggedIn] = useState(false);
  const [uploaded, setUploaded] = useState(false);

  if (!loggedIn) {
    return <Login onLogin={() => setLoggedIn(true)} />;
  }

  if (!uploaded) {
    return <Upload onUpload={() => setUploaded(true)} />;
  }

  return <CourseMap />;
};

export default App;
