import React from 'react';
import { Button } from 'flowbite-react';
import { SparklesIcon } from '@heroicons/react/20/solid';

const QuizResultsTable = ({ modules }) => {
  return (
    <div className="bg-white shadow-lg rounded-lg px-8 pt-6 pb-8 mb-4">
      {modules.map((module, moduleIndex) => (
        <div key={moduleIndex} className='mb-6'>
          <h2 className="text-xl font-heading mb-6">{module.module_title}</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full border-collapse">
              <thead>
                <tr>
                  <th className="border-b font-sans text-gray-800 text-left">Question</th>
                  <th className="border-b font-sans p-4 text-gray-800 text-left">My Answer</th>
                  <th className="border-b font-sans p-4 text-gray-800 text-left">Correct Answer</th>
                  {/* <th className="border-b font-sans p-4 text-gray-800 text-left">Actions</th> */}
                </tr>
              </thead>
              <tbody>
                {module.assignments.map((assignment, index) => (
                  <tr key={index} className="border-b">
                    <td className="font-sans text-sm text-gray-700">{assignment.question_text}</td>
                    <td className="font-sans p-4 text-sm text-gray-700">{assignment.student_response}</td>
                    <td className="font-sans p-4 text-sm text-gray-700">{assignment.correct_answer_text}</td>
                    {/* <td className="font-sans p-4 text-sm">
                    <Button size="xs" gradientDuoTone="purpleToPink" onClick={() => alert("Not yet enabled.")}>
                                <SparklesIcon className="mr-1 h-3 w-3" />
                                AI
                     </Button>
                    </td> */}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-6">
            <Button
              
              onClick={() => alert("This feature will be activated by June 30, 2024. Thanks for waiting.")}
            >
              Retake this quiz
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default QuizResultsTable;
