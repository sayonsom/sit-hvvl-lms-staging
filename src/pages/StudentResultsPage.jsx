import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeftIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";
import axios from "axios";
import AppLayout from "./AppLayout";
import Spinner from "../components/Spinner";
import { Alert } from "flowbite-react";
import { API_URL } from "../env";

const apiUrl = API_URL;

export default function StudentResultsPage() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedStudent, setExpandedStudent] = useState(null);
  const [expandedQuiz, setExpandedQuiz] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError("");
      try {
        const [courseRes, resultsRes] = await Promise.all([
          axios.get(`${apiUrl}/courses/${courseId}`),
          axios.get(`${apiUrl}/courses/${courseId}/student-results`),
        ]);
        setCourse(courseRes.data);
        setResults(resultsRes.data);
      } catch (err) {
        console.error("Error fetching results:", err);
        setError(
          err?.response?.status === 403
            ? "This teacher account is not assigned to view results for this course."
            : "Student scores and averages could not be loaded. Please retry or contact support."
        );
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [courseId]);

  const toggleStudent = (studentId) => {
    setExpandedStudent(expandedStudent === studentId ? null : studentId);
    setExpandedQuiz(null);
  };

  const toggleQuiz = (key) => {
    setExpandedQuiz(expandedQuiz === key ? null : key);
  };

  // Compute quiz-level stats
  const totalQuizzesTaken = results.reduce((sum, s) => sum + s.modules.length, 0);
  const totalQuestionsAnswered = results.reduce(
    (sum, student) => sum + student.modules.reduce((moduleSum, module) => moduleSum + module.total, 0),
    0
  );
  const totalCorrectAnswers = results.reduce(
    (sum, student) => sum + student.modules.reduce((moduleSum, module) => moduleSum + module.correct, 0),
    0
  );
  const avgScore = totalQuestionsAnswered > 0
    ? Math.round((totalCorrectAnswers / totalQuestionsAnswered) * 100)
    : 0;

  if (loading) {
    return (
      <AppLayout>
        <Spinner />
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="mx-auto w-full max-w-6xl px-6 py-10">
        {/* Header */}
        <div className="flex items-center gap-4 mb-2">
          <button
            onClick={() => navigate(-1)}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <ArrowLeftIcon className="h-5 w-5" />
          </button>
          <h2 className="text-2xl font-heading font-bold text-gray-900 dark:text-white">
            Student Quiz Results
          </h2>
        </div>
        {course && (
          <p className="text-gray-500 dark:text-gray-400 mb-8 ml-9">
            {course.title}
          </p>
        )}

        {error ? <Alert color="failure" className="mb-8">{error}</Alert> : null}

        {/* Summary Stats */}
        {!error ? <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5 text-center">
            <p className="text-3xl font-bold text-purple-600">{results.length}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Students</p>
          </div>
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5 text-center">
            <p className="text-3xl font-bold text-blue-600">{totalQuizzesTaken}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Quizzes Completed</p>
          </div>
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5 text-center">
            <p className={`text-3xl font-bold ${avgScore >= 70 ? "text-green-600" : avgScore >= 40 ? "text-yellow-600" : "text-red-600"}`}>
              {avgScore}%
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Average Score</p>
          </div>
        </div> : null}

        {/* Student Table */}
        {!error && results.length === 0 ? (
          <div className="text-center py-16 text-gray-500 dark:text-gray-400">
            <p className="text-lg">No quiz submissions yet.</p>
            <p className="text-sm mt-1">
              Students will appear here after they complete a quiz.
            </p>
          </div>
        ) : !error ? (
          <>
            {/* Table Header */}
            <div className="hidden md:grid grid-cols-12 gap-4 px-5 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              <div className="col-span-5">Student</div>
              <div className="col-span-3 text-center">Quizzes Completed</div>
              <div className="col-span-2 text-center">Avg Score</div>
              <div className="col-span-2 text-center">Status</div>
            </div>

            <div className="space-y-2">
              {results.map((student) => {
                const isExpanded = expandedStudent === student.student_id;
                const quizCount = student.modules.length;
                const studentAvg =
                  student.total_questions > 0
                    ? Math.round((student.correct_answers / student.total_questions) * 100)
                    : 0;

                return (
                  <div
                    key={student.student_id}
                    className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
                  >
                    {/* Student Row */}
                    <button
                      onClick={() => toggleStudent(student.student_id)}
                      className="w-full grid grid-cols-12 gap-4 items-center p-4 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors text-left"
                    >
                      <div className="col-span-12 md:col-span-5 flex items-center gap-3">
                        {isExpanded ? (
                          <ChevronDownIcon className="h-5 w-5 text-gray-400 flex-shrink-0" />
                        ) : (
                          <ChevronRightIcon className="h-5 w-5 text-gray-400 flex-shrink-0" />
                        )}
                        <div className="min-w-0">
                          <p className="font-semibold text-gray-900 dark:text-white truncate">
                            {student.student_name}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                            {student.student_email}
                          </p>
                        </div>
                      </div>
                      <div className="hidden md:block col-span-3 text-center">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          {quizCount}
                        </span>
                      </div>
                      <div className="hidden md:block col-span-2 text-center">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          {studentAvg}%
                        </span>
                      </div>
                      <div className="hidden md:flex col-span-2 justify-center">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            studentAvg >= 70
                              ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
                              : studentAvg >= 40
                              ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
                              : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
                          }`}
                        >
                          {studentAvg >= 70 ? "Good" : studentAvg >= 40 ? "Needs Work" : "At Risk"}
                        </span>
                      </div>
                    </button>

                    {/* Expanded: Quiz breakdown per module */}
                    {isExpanded && (
                      <div className="border-t border-gray-200 dark:border-gray-700 px-4 pb-4">
                        {/* Mobile summary */}
                        <div className="md:hidden flex gap-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                          <span>{quizCount} quiz{quizCount !== 1 ? "zes" : ""} completed</span>
                          <span>Avg: {studentAvg}%</span>
                        </div>

                        {student.modules.map((mod) => {
                          const quizKey = `${student.student_id}-${mod.module_title}`;
                          const isQuizExpanded = expandedQuiz === quizKey;
                          const quizPercent =
                            mod.total > 0 ? Math.round((mod.correct / mod.total) * 100) : 0;

                          return (
                            <div key={quizKey} className="mt-2">
                              <button
                                onClick={() => toggleQuiz(quizKey)}
                                className="w-full flex items-center justify-between py-3 px-3 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-left"
                              >
                                <div className="flex items-center gap-2">
                                  {isQuizExpanded ? (
                                    <ChevronDownIcon className="h-4 w-4 text-gray-400" />
                                  ) : (
                                    <ChevronRightIcon className="h-4 w-4 text-gray-400" />
                                  )}
                                  <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                                    {mod.module_title}
                                  </span>
                                </div>
                                <div className="flex items-center gap-3">
                                  <span className="text-xs text-gray-500 dark:text-gray-400">
                                    {mod.correct}/{mod.total} correct
                                  </span>
                                  <span
                                    className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                                      quizPercent >= 70
                                        ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
                                        : quizPercent >= 40
                                        ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
                                        : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
                                    }`}
                                  >
                                    {quizPercent}%
                                  </span>
                                </div>
                              </button>

                              {isQuizExpanded && (
                                <div className="ml-9 mt-2 space-y-2">
                                  {mod.questions.map((q, qi) => (
                                    <div
                                      key={qi}
                                      className="flex items-start gap-3 py-2 px-3 rounded bg-gray-50 dark:bg-gray-700"
                                    >
                                      {q.is_correct ? (
                                        <CheckCircleIcon className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                                      ) : (
                                        <XCircleIcon className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                                      )}
                                      <div className="flex-1 min-w-0">
                                        <p className="text-sm text-gray-800 dark:text-gray-200">
                                          {q.question_text}
                                        </p>
                                        <p className="text-xs mt-1">
                                          <span className="text-gray-500 dark:text-gray-400">
                                            Answer:{" "}
                                          </span>
                                          <span
                                            className={
                                              q.is_correct
                                                ? "text-green-600 dark:text-green-400"
                                                : "text-red-600 dark:text-red-400"
                                            }
                                          >
                                            {q.student_response || "(no response)"}
                                          </span>
                                        </p>
                                        {!q.is_correct && q.correct_answer && (
                                          <p className="text-xs mt-0.5">
                                            <span className="text-gray-500 dark:text-gray-400">
                                              Correct:{" "}
                                            </span>
                                            <span className="text-green-600 dark:text-green-400">
                                              {q.correct_answer}
                                            </span>
                                          </p>
                                        )}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </>
        ) : null}
      </div>
    </AppLayout>
  );
}
