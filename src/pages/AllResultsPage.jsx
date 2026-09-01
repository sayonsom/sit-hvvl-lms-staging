import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ChartBarIcon,
  ArrowLeftIcon,
} from "@heroicons/react/24/outline";
import axios from "axios";
import AppLayout from "./AppLayout";
import Spinner from "../components/Spinner";
import { Alert } from "flowbite-react";
import { API_URL } from "../env";

const apiUrl = API_URL;

export default function AllResultsPage() {
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setError("");
        const response = await axios.get(`${apiUrl}/courses`);
        setCourses(response.data);
      } catch (err) {
        console.error("Error fetching courses:", err);
        setError(
          err?.response?.status === 403
            ? "Your teacher account is not assigned to a course results scope."
            : "Course results could not be loaded. Please retry or contact support."
        );
      } finally {
        setLoading(false);
      }
    };
    fetchCourses();
  }, []);

  if (loading) {
    return (
      <AppLayout>
        <Spinner />
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="mx-auto w-full max-w-5xl px-6 py-10">
        <div className="flex items-center gap-4 mb-2">
          <button
            onClick={() => navigate("/home")}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <ArrowLeftIcon className="h-5 w-5" />
          </button>
          <h2 className="text-2xl font-heading font-bold text-gray-900 dark:text-white">
            Student Results
          </h2>
        </div>
        <p className="text-gray-500 dark:text-gray-400 mb-8 ml-9">
          Select a course to view student quiz results.
        </p>

        {error ? <Alert color="failure" className="mb-6">{error}</Alert> : null}

        {!error && courses.length === 0 ? (
          <div className="text-center py-16 text-gray-500 dark:text-gray-400">
            <p className="text-lg">No courses found.</p>
          </div>
        ) : !error ? (
          <div className="space-y-3">
            {courses.map((course) => (
              <button
                key={course.course_id}
                onClick={() => navigate(`/manage/course/${course.course_id}/results`)}
                className="w-full flex items-center justify-between p-5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-purple-300 dark:hover:border-purple-600 hover:shadow-sm transition-all text-left"
              >
                <div className="flex items-center gap-4">
                  <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                    <ChartBarIcon className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {course.title}
                    </p>
                    {course.description && (
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-1">
                        {course.description}
                      </p>
                    )}
                  </div>
                </div>
                <span className="text-sm text-purple-600 dark:text-purple-400 font-medium">
                  View Results →
                </span>
              </button>
            ))}
          </div>
        ) : null}
      </div>
    </AppLayout>
  );
}
