import React, { useEffect, useState } from "react";
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import AppLayout from "./AppLayout";
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/20/solid'
import { WrenchScrewdriverIcon } from '@heroicons/react/24/outline';
import CourseDetailsColumn from "../components/CourseDetailsColumn";
import CourseModulesColumn from "../components/CourseModulesColumn";
import Spinner from "../components/Spinner";
import { useLTI } from "../contexts/LTIContext";
import { API_URL } from "../env";

const apiUrl = API_URL;

export default function CourseDetailsPage() {
    const { courseShortCode } = useParams();
  const [course, setCourse] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);
  const { authMethod } = useLTI();
  const isStaff = authMethod === 'staff';

  useEffect(() => {
    const fetchCourseDetails = async () => {
      try {
        const response = await axios.get(`${apiUrl}/courses/${courseShortCode}`);
        setCourse(response.data);
        console.log("Course details")
        console.log(response.data)
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching course details', error);
        const detail = error?.response?.data?.detail || error?.message || "Unknown error";
        const status = error?.response?.status;
        setErrorMessage(
          status ? `Could not load course ${courseShortCode} (${status}): ${detail}` : `Could not load course ${courseShortCode}: ${detail}`
        );
        setIsLoading(false);
      }
    };

    fetchCourseDetails();
  }, [courseShortCode]);



    if (isLoading) {
        return (
            <AppLayout>
                <div className="max-w-md w-full space-y-8">
                    <div className="flex flex-col items-center">
                        <Spinner />
                    </div>
                </div>
            </AppLayout>
        )
    }

    if (errorMessage) {
        return (
            <AppLayout>
                <div className="mx-auto max-w-3xl px-6 py-10">
                    <div className="rounded-lg border border-red-200 bg-red-50 p-5 text-red-800">
                        <h1 className="text-lg font-semibold">Course could not be loaded</h1>
                        <p className="mt-2 text-sm">{errorMessage}</p>
                        <Link to="/home" className="mt-4 inline-block text-sm font-semibold text-red-900 underline">
                            Back to courses
                        </Link>
                    </div>
                </div>
            </AppLayout>
        )
    }

    return ( 
        <> 
        <AppLayout>
            {/* PAGE HEADING */}
            <div className="min-h-full"> 

            {/* div to show the title of the course */}
            <div className="px-4 py-10 sm:px-6 lg:px-8 lg:py-6">
                <div className="flex items-center justify-between">
                    <h1 className="font-heading text-4xl text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight dark:text-white">{course.title} </h1>
                    {isStaff && (
                        <Link
                            to={`/manage/course/${course.course_id}`}
                            className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors"
                        >
                            <WrenchScrewdriverIcon className="h-4 w-4" />
                            Manage Course
                        </Link>
                    )}
                </div>
                <div className="font-sans mt-4 max-w-4xl text-xl text-gray-700 dark:text-gray-400">
                    <p>{course.description}</p>
                </div>
            </div>

                <div className="flex flex-col md:flex-row"> {/* Stack on small screens, side by side on medium screens and up */}
                    <div className="md:w-1/3 bg-white dark:bg-gray-900 px-4 py-6"> {/* This is the first column */}
                        <CourseModulesColumn course={course} />
                    </div>
                    <div className="md:w-2/3 bg-white dark:bg-gray-700 px-4 py-6"> {/* This is the second column */}
                        <CourseDetailsColumn course={course} />
                    </div>
                </div>

            </div>
        </AppLayout>
        </>
    )
}
