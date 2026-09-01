'use client';

import React, { useState, useEffect } from 'react';

import { Rating } from 'flowbite-react';

function CourseDetailsColumn({ course }) {

    // const [ title, offering_institute, description, course_image, session_end_date ] = course;
    // check if student is enrolled in this course or not
    // const [isEnrolled, setIsEnrolled] = useState(false);
    // const [isLoading, setIsLoading] = useState(true);

    // // grab the email from the local storage
    // const email = sessionStorage.getItem('HVLABuserEmail');

    // useEffect(() => {
    //     const fetchCourses = async () => {
    //         try {
    //             const response = await axios.get(`${apiUrl}/students/${email}/courses`);
    //             setCourses(response.data);
    //             setIsLoading(false);
    //         } catch (error) {
    //             console.error('Error fetching courses', error);
    //             setIsLoading(false);
    //         }
    //     };

    return (
        <div className="">
          <div className="">
            <div className="px-4 py-10 sm:px-6 lg:px-8 lg:py-6">
                {/* <h1 className="font-heading text-4xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight dark:text-white">{course.title} </h1> */}
                {/* <Badge color="pink">{offering_institute}</Badge> */}
                {/* Description */}
                <Rating className='font-sans pt-4'>
                    <Rating.Star />
                    <p className="ml-2 text-sm font-bold text-gray-900 dark:text-white">5.0</p>
                    <span className="mx-1.5 h-1 w-1 rounded-full bg-gray-500 dark:bg-gray-400" />
                        <a href="#" className="text-sm font-medium text-gray-900 underline hover:no-underline dark:text-white">
                            1 reviews
                        </a>
                 </Rating>
                {/* <div className="font-sans mt-4 max-w-4xl text-xl text-gray-700 dark:text-gray-400">
                    <p>{course.description}</p>
                </div> */}

                {/* Offered by */}

                <div className="mt-6">
                    <h2 className="font-heading text- font-light leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight dark:text-white">Offered by</h2>
                    <div className="mt-4 max-w-4xl text-base text-gray-700 dark:text-gray-400">
                        <p>{course.offering_institute}</p>
                    </div>
                </div>
                
                {/* Instructor */}
                <div className="mt-6">
                    <h2 className="font-heading text- font-light leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight dark:text-white">Instructor</h2>
                    <div className="mt-4 max-w-4xl text-base text-gray-700 dark:text-gray-400">
                        <p>{course.instructor_id}</p>
                    </div>
                </div>

                 {/* Enrollment */}

                <div className="mt-6">
                    <h2 className="font-heading text- font-light leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight dark:text-white">Enrollment</h2>
                    <span className="inline-flex items-center rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700 ring-1 ring-inset ring-red-600/10">
                        {course.enrollment_status}
                    </span>
                    <div className="mt-4 max-w-4xl text-base text-gray-700 dark:text-gray-400">
                        <p>Next enrollment begins {course.enrollment_begin_date} to {course.enrollment_end_date}</p>
                    </div>
                </div>

                {/* Official Webpage */}

                <div className="mt-6">
                    <h2 className="font-heading text- font-light leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight dark:text-white">Official Webpage</h2>
                    <div className="mt-4 max-w-4xl text-base text-gray-700 dark:text-gray-400">
                        <a href={course.course_webpage} className="text-sm font--sanstext-gray-900 underline hover:no-underline dark:text-white">
                            Visit Official Webpage from {course.offering_institute}
                        </a>
                    </div>
                </div>

                {/* Syllabus  */}

                <div className="mt-6">
                    <h2 className="font-heading text- font-light leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight dark:text-white">Syllabus</h2>
                    <div className="mt-4 max-w-4xl text-base text-gray-700 dark:text-gray-400">
                        
                        <a href={course.syllabus_pdf_link} className="text-sm font-sans text-gray-900 underline hover:no-underline dark:text-white">
                            Click to download
                        </a>
                    </div>
                </div>

                

            </div>
          </div>
        </div>
    );

}

export default CourseDetailsColumn;