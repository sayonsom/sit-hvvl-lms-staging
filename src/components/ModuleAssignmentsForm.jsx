import React, { useState, useEffect } from 'react';
import { Button } from 'flowbite-react';
import {  Legend, Field, FieldGroup, Fieldset, Label } from './fieldset';
import { Input } from './input';
import { Textarea } from './textarea';
import {  Text } from './text';
import { Radio, RadioField } from './radio';
import { API_URL } from "../env";

const apiUrl = API_URL;

const authHeaders = () => {
  const token = sessionStorage.getItem('vhvl_api_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export default function ModuleAssignmentsForm ( {moduleID} ){
  const [moduleAssignments, setModuleAssignments] = useState(null);
  const [responses, setResponses] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [anyError, setAnyError] = useState(false);

  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${apiUrl}/modules/${moduleID}/assignments`, {
          headers: authHeaders(),
        });
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setModuleAssignments(data);  // This assumes data is an array from the API response
      } catch (error) {
        console.error('There was a problem fetching module assignments:', error);
      }
    };
  
    fetchData();

    // Initialize responses state after fetching module assignments
  if (moduleAssignments) {
    const initialResponses = {};
    for (const assignment of moduleAssignments) {
      initialResponses[assignment.assignment_id] = {};
      for (const question of assignment.questions) {
        initialResponses[assignment.assignment_id][question.question_id] = '';
      }
    }
    setResponses(initialResponses);
  }

  }, [moduleID]); 

  const handleInputChange = (assignmentId, questionId, value) => {
    setResponses({
      ...responses,
      [assignmentId]: {
        ...responses[assignmentId],
        [questionId]: value
      }
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    // Check if all questions have been attempted
    const allQuestionsAttempted = moduleAssignments.every((assignment) =>
      assignment.questions.every((question) =>
        responses[assignment.assignment_id]?.hasOwnProperty(question.question_id)
      )
    );

    if (!allQuestionsAttempted) {
      alert('Please answer all questions before submitting.');
      return;
    }

    setIsSubmitting(true);
    setAnyError(false);

    const studentId = parseInt(sessionStorage.getItem('StudentID'), 10);
    if (!studentId || isNaN(studentId)) {
      alert('Unable to identify student. Please reload the page and try again.');
      setIsSubmitting(false);
      return;
    }

    let hadError = false;

    for (const [assignmentId, questions] of Object.entries(responses)) {
        for (const [questionId, responseValue] of Object.entries(questions)) {
            try {
                const response = await fetch(`${apiUrl}/modules/${moduleID}/assignments/${assignmentId}/questions/${questionId}/responses`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...authHeaders()
                    },
                    body: JSON.stringify({
                        student_id: studentId,
                        response_text: String(responseValue)
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

            } catch (error) {
                console.error('There was a problem saving the response:', error);
                hadError = true;
            }
        }
    }

    setIsSubmitting(false);

    if (hadError) {
        setAnyError(true);
        alert('Some responses could not be saved. Please try again.');
    } else {
        alert('Your responses have been submitted successfully! Thank you.');
    }
};

  // Return early if data is not yet fetched
  if (!moduleAssignments) {
    return <div>Loading...</div>;
  }

  return (
    <>
      {isSubmitting && (
        <div className="overlay">
          <div className="spinner"></div>
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-8 divide-y divide-gray-200">
      {moduleAssignments && moduleAssignments.map((assignment) => ( // Check if moduleAssignments is truthy and map over it directly
        <div key={assignment.assignment_id} className="space-y-8 divide-y divide-gray-200">
          <div>
            {/* <h3 className="text-lg leading-6 font-medium text-gray-900">{assignment.title}</h3> */}
            <p className="mt-1 text-sm text-gray-500">{assignment.description}</p>
          </div>

          <div className="mt-6">
          {assignment.questions && assignment.questions.map((question) => ( // Check if questions is truthy before mapping
              <Fieldset key={question.question_id} className="space-y-5">
                <Field>
                    <Legend className="text-base my-4">{question.question_text}</Legend>
                    {/* <Text>{question.question_text}</Text> */}

                    {question.question_type === 'long_text' && (
                    <Textarea
                        id={`question-${question.question_id}`}
                        name={`question-${question.question_id}`}
                        rows={4}
                        // className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        defaultValue={responses[assignment.assignment_id]?.[question.question_id] || ''}
                        onChange={(e) => handleInputChange(assignment.assignment_id, question.question_id, e.target.value)}
                    />
                    )}

                    {question.question_type === 'multiple_choice' && question.options.map((option) => (
                    <div key={option.option_id} className="flex items-center">
                        <input
                        id={`option-${option.option_id}`}
                        name={`question-${question.question_id}`}
                        type="radio"
                        className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300"
                        value={option.option_id}
                        checked={responses[assignment.assignment_id]?.[question.question_id] === option.option_id}
                        onChange={(e) => handleInputChange(assignment.assignment_id, question.question_id, option.option_id)}
                        />
                        <label htmlFor={`option-${option.option_id}`} className="ml-3 block text-sm font-medium text-gray-700">
                        {option.option_text}
                        </label>
                    </div>
                    ))}
                    </Field>
              </Fieldset>
            ))}
          </div>
        </div>
      ))}

      <div className="pt-5">
        <div className="flex">

            <Button outline gradientDuoTone="pinkToOrange" onClick={handleSubmit}>
            Submit my answers
            </Button>

        </div>
      </div>
    </form>

    </>
    
  );
};
