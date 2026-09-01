import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

import { Alert, Button, Card, Spinner } from 'flowbite-react';
import { API_URL } from "../env";

const apiUrl = API_URL;

function CourseModulesColumn( { course }) {
    const [modules, setModules] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [reloadKey, setReloadKey] = useState(0);
    // check if student is enrolled in this course or not
    // const [isEnrolled, setIsEnrolled] = useState(false);
    // const [isLoading, setIsLoading] = useState(true);

    // // grab the email from the local storage
    // const email = sessionStorage.getItem('HVLABuserEmail');

    useEffect(() => {
        const fetchModules = async () => {
          setIsLoading(true);
          setError('');
          try {
            const response = await axios.get(`${apiUrl}/courses/${course.course_id}/modules`);
            setModules(response.data);

            
          } catch (error) {
            console.error('Error fetching modules', error);
            setError(
              error?.response?.status === 403
                ? 'Your account is not permitted to open experiments for this course.'
                : 'The experiment list could not be loaded.'
            );
          } finally {
            setIsLoading(false);
          }
        };
    
        fetchModules();
      }, [course.course_id, reloadKey]);

    return (
        <Card className="max-w-sm">
      <h5 className="font-heading mb-3 text-base font-semibold text-gray-900 dark:text-white lg:text-xl">Experiments</h5>
      <p className="font-sans text-sm font-normal text-gray-500 dark:text-gray-400">
        Learn by doing these interactive virtual experiments, which were designed by renowned experts and professors at Singapore Institute of Technology (SIT), to help you learn the concepts of the { course.title }.
      </p>
        {isLoading ? (
          <div className="my-8 flex items-center justify-center gap-3 text-sm text-gray-500">
            <Spinner size="sm" /> Loading experiments…
          </div>
        ) : null}
        {error ? (
          <Alert color="failure" className="my-4">
            <div className="flex flex-col items-start gap-3">
              <span>{error}</span>
              <Button size="xs" color="failure" onClick={() => setReloadKey((key) => key + 1)}>Retry</Button>
            </div>
          </Alert>
        ) : null}
        {!isLoading && !error && modules.length === 0 ? (
          <p className="my-6 text-sm text-gray-500">No published experiments are available for this course.</p>
        ) : null}
        {!isLoading && !error ? <ul className="my-4 space-y-3">
        {modules.map((module) => (
            <li key={module.module_id}>
            <Link
                            to={`/module/${module.module_id}`} // Use the Link component with the `to` prop
                            className="group flex items-center rounded-lg bg-gray-50 p-3 text-base font-bold text-gray-900 hover:bg-gray-100 hover:shadow dark:bg-gray-600 dark:text-white dark:hover:bg-gray-500"
                        >
                <span className="ml-3 flex-1">{module.title}</span>
                <span className="ml-3 inline-flex items-center justify-center rounded bg-gray-200 px-2 py-0.5 text-xs font-medium text-gray-500 dark:bg-gray-700 dark:text-gray-400">
              AI enabled
            </span>
            </Link>
            </li>
        ))}
        </ul> : null}
      <div>
        <a
          href="#"
          className="inline-flex items-center text-xs font-normal text-gray-500 hover:underline dark:text-gray-400"
        >
          <svg
            className="mr-2 h-3 w-3"
            aria-hidden="true"
            focusable="false"
            data-prefix="far"
            data-icon="question-circle"
            role="img"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 512 512"
          >
            <path
              fill="currentColor"
              d="M256 8C119.043 8 8 119.083 8 256c0 136.997 111.043 248 248 248s248-111.003 248-248C504 119.083 392.957 8 256 8zm0 448c-110.532 0-200-89.431-200-200 0-110.495 89.472-200 200-200 110.491 0 200 89.471 200 200 0 110.53-89.431 200-200 200zm107.244-255.2c0 67.052-72.421 68.084-72.421 92.863V300c0 6.627-5.373 12-12 12h-45.647c-6.627 0-12-5.373-12-12v-8.659c0-35.745 27.1-50.034 47.579-61.516 17.561-9.845 28.324-16.541 28.324-29.579 0-17.246-21.999-28.693-39.784-28.693-23.189 0-33.894 10.977-48.942 29.969-4.057 5.12-11.46 6.071-16.666 2.124l-27.824-21.098c-5.107-3.872-6.251-11.066-2.644-16.363C184.846 131.491 214.94 112 261.794 112c49.071 0 101.45 38.304 101.45 88.8zM298 368c0 23.159-18.841 42-42 42s-42-18.841-42-42 18.841-42 42-42 42 18.841 42 42z"
            />
          </svg>
          Academic data privacy statement
        </a>
      </div>
        </Card>
    );

}

export default CourseModulesColumn;
