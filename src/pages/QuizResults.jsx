import React, { useEffect, useState } from 'react';
import AppLayout from './AppLayout';
import { useLTI } from "../contexts/LTIContext";
import QuizResultsTable from "../components/QuizResultsTable";
import axios from "axios";
import { API_URL } from "../env";

export default function QuizResults() {

    const apiUrl = API_URL;

    const [modulesData, setModulesData] = useState([]);

    const { user } = useLTI();

    const studentId = sessionStorage.getItem("StudentID");

    const getQuizData = async (id) => {
      const response = await axios.get(`${apiUrl}/students/${id}/assignments/responses`);
      return response.data;
    };

    useEffect(() => {
      if (studentId) {
        getQuizData(studentId).then((data) => {
          setModulesData(data);
        }).catch((error) => {
          console.error("Failed to fetch quiz data:", error);
        });
      }
    }, [studentId]);
  

    return (
        <>
            <AppLayout>
                <div className="min-h-full">   
                    <div className="mx-auto w-full max-w-7xl px-6 pb-16 pt-10 sm:pb-24 lg:px-8">
                        {/* Page Header */}
                        <div className="md:flex md:items-center md:justify-between">
                            <div className="min-w-0 flex-1">
                                <h2 className="text-2xl font-heading font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight dark:text-white">
                                    Quiz Results
                                </h2>
                            </div>
                        </div>

                        
                        {/* Pass the quiz data to the QuizResultsTable component */}
                        <div className="mt-8">
                            <p>
                                
                                {modulesData ? (
                                    <QuizResultsTable modules={modulesData} />
                                ) : (
                                    "Loading..."
                                )}
                            </p>
                        </div>
                    </div>
                </div>
            </AppLayout>
        </>
    );
}
