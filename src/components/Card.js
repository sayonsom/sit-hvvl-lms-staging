import React from 'react';

function Card({ cardName }) {

  return (
    <div className="m-8 p-8 bg-white rounded-md shadow-xl">
      <h2> {cardName} </h2>
      {/* Your content here */}
    </div>
  );
}

export default Card;
