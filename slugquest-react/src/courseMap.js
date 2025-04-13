import React, { useState, useEffect } from 'react';
import './App.css';

const courses = [
  { name: 'MATH 19A MATH 20A', x: 500, y: 600 },
  { name: 'MATH 19B MATH 20B', x: 500, y: 900 },
  { name: 'CSE 16', x: 400, y: 1200 },
  { name: 'MATH 21 AM 10', x: 150, y: 900 },
  { name: 'AM 30', x: 200, y: 1200 },
  { name: 'MATH 23A', x: 270, y: 1200 },
  { name: 'ECE 30', x: 532, y: 1200 },
  { name: 'CSE 101', x: 700, y: 1500 },
  { name: 'CSE 101M', x: 600, y: 1800 },
  { name: 'CSE 102 CSE 103', x: 1000, y: 1800 },
  { name: 'CSE 130', x: 400, y: 1800 },
  { name: 'CSE 107 STATS 131', x: 300, y: 1500 },
  { name: 'CSE 114A', x: 800, y: 1800 },
  { name: 'CSE 20', x: 1000, y: 625 },
  { name: 'CSE 12', x: 1100, y: 900 },
  { name: 'CSE 30', x: 900, y: 900 },
  { name: 'CSE 40', x: 760, y: 1200 },
  { name: 'CSE 13S', x: 1100, y: 1200 },
  { name: 'CSE 120', x: 1100, y: 1500 },
  { name: 'Upper Elective', x: 305, y: 2030 },
  { name: 'Upper Elective', x: 200, y: 2030 },
  { name: 'Upper Elective', x: 200, y: 2100 },
  { name: 'Upper Elective', x: 305, y: 2100 },
  { name: 'CSE 115A CSE 185 CSE 195', x: 1100, y: 2100 },
  { name: 'Capstone', x: 700, y: 2200 },
];

// const connections = [
//   ['MATH 19A', 'MATH 19B'],
//   ['MATH 19A', 'CSE 16'],
//   ['MATH 19B', 'AM 30'],
//   ['MATH 19B', 'CSE 101'],
//   ['CSE 20', 'CSE 12'],
//   ['CSE 20', 'CSE 30'],
//   ['CSE 12', 'CSE 13S'],
//   ['CSE 13S', 'CSE 120'],
//   ['CSE 13S', 'CSE 101'],
//   ['AM 30', 'CSE 101'],
//   ['MATH 23A', 'CSE 101'],
//   ['CSE 101', 'CSE 102'],
//   ['CSE 101', 'CSE 130'],
//   ['CSE 16', 'CSE 107'],
//   ['MATH 23A', 'CSE 107'],
//   ['AM 30', 'CSE 107'],
// ];

const CourseMap = () => {

  const [isBright, setIsBright] = useState([0]);
  const [isHovered, setIsHovered] = useState();

  useEffect( () => {
    setTimeout(() => {
      setIsBright((isBright) => {

        if (isBright === 0) return 1;
        else return 0;
      });
    }, 500);
  }, [isBright]);

  const hoverCheck = (id, color) => {
    if (id !== isHovered) {
      if (isBright) return `lighter${color}`;
      else return `darker${color}`;
    }
  }

  return <div className="bg-gradient-to-b from-blue-300 to-green-600 mapContainer">
    <div className="mapImage"></div>
      {/*}
      <svg className="absolute top-0 left-0 w-full h-full z-0">
        {connections.map(([from, to], index) => {
          const courseFrom = courses.find(c => c.name === from);
          const courseTo = courses.find(c => c.name === to);
          const x1 = courseFrom.x + 75;
          const y1 = courseFrom.y + 25;
          const x2 = courseTo.x + 75;
          const y2 = courseTo.y + 25;

          const midX = (x1 + x2) / 2;
          const midY = (y1 + y2) / 2;

          // Adjust curve based on relative positions
          const curveX = x1 === x2 ? 0 : (x2 - x1) * 0.25;
          const curveY = y1 === y2 ? 0 : (y2 - y1) * 0.25;

          return (
            <g key={index}>
              {/* Shadow Path *//*}
              <path
                d={`M${x1},${y1} Q${midX + curveX},${midY + curveY} ${x2},${y2}`}
                stroke="rgba(0,0,0,0.3)"
                strokeWidth="6"
                fill="none"
              />
              {/* Yellow Main Path *//*}
              <path
                d={`M${x1},${y1} Q${midX + curveX},${midY + curveY} ${x2},${y2}`}
                stroke="#FFDD57"
                strokeWidth="3"
                fill="none"
              />
              {/* Endpoints *//*}
              <circle cx={x1} cy={y1} r="4" fill="#fff" stroke="#333" strokeWidth="1" />
              <circle cx={x2} cy={y2} r="4" fill="#fff" stroke="#333" strokeWidth="1" />
            </g>
          );
        })}
      </svg>*/}

      {courses.map((course, index) => (
        <div
          key={index}
          onMouseEnter={() => setIsHovered(index)}
          onMouseLeave={() => setIsHovered(-1)}
          className={`${hoverCheck(index, 'Yellow')} absolute border-2 border-white shadow-md text-black px-3 py-2 rounded-xl cursor-pointer z-10 classNode`}
          style={{top: course.y, left: course.x}}
        >
          {course.name}
        </div>
      ))}
    {/* </div> */}
  </div>
};

export default CourseMap;
