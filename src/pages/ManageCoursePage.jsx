import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button, Modal } from "flowbite-react";
import {
  PencilSquareIcon,
  TrashIcon,
  PlusIcon,
  ArrowLeftIcon,
  ChartBarIcon,
} from "@heroicons/react/24/outline";
import axios from "axios";
import AppLayout from "./AppLayout";
import ModuleEditor from "../components/ModuleEditor";
import Spinner from "../components/Spinner";
import { API_URL } from "../env";

const apiUrl = API_URL;

export default function ManageCoursePage() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingModule, setEditingModule] = useState(null); // null=list, "new"=create, module obj=edit
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [courseRes, modulesRes] = await Promise.all([
        axios.get(`${apiUrl}/courses/${courseId}`),
        axios.get(`${apiUrl}/courses/${courseId}/modules`),
      ]);
      setCourse(courseRes.data);
      setModules(modulesRes.data);
    } catch (err) {
      console.error("Error fetching course data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [courseId]);

  const handleSave = () => {
    setEditingModule(null);
    fetchData();
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await axios.delete(`${apiUrl}/modules/${deleteTarget.module_id}`);
      setDeleteTarget(null);
      fetchData();
    } catch (err) {
      console.error("Error deleting module:", err);
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <Spinner />
      </AppLayout>
    );
  }

  // Show module editor
  if (editingModule !== null) {
    return (
      <AppLayout>
        <div className="mx-auto w-full max-w-4xl px-6 py-10">
          <ModuleEditor
            module={editingModule === "new" ? null : editingModule}
            courseId={courseId}
            onSave={handleSave}
            onCancel={() => setEditingModule(null)}
          />
        </div>
      </AppLayout>
    );
  }

  // Module list view
  return (
    <AppLayout>
      <div className="mx-auto w-full max-w-5xl px-6 py-10">
        {/* Header */}
        <div className="flex items-center gap-4 mb-2">
          <button
            onClick={() => navigate(`/courses/${courseId}`)}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <ArrowLeftIcon className="h-5 w-5" />
          </button>
          <h2 className="text-2xl font-heading font-bold text-gray-900 dark:text-white">
            Manage Course
          </h2>
        </div>
        {course && (
          <p className="text-gray-500 dark:text-gray-400 mb-8 ml-9">
            {course.title}
          </p>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end gap-3 mb-6">
          <Button
            color="gray"
            onClick={() => navigate(`/manage/course/${courseId}/results`)}
          >
            <ChartBarIcon className="h-5 w-5 mr-2" />
            View Student Results
          </Button>
          <Button
            gradientDuoTone="purpleToPink"
            onClick={() => setEditingModule("new")}
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add New Module
          </Button>
        </div>

        {/* Modules List */}
        {modules.length === 0 ? (
          <div className="text-center py-16 text-gray-500 dark:text-gray-400">
            <p className="text-lg">No modules yet.</p>
            <p className="text-sm mt-1">
              Click "Add New Module" to create your first module.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {modules.map((mod, index) => (
              <div
                key={mod.module_id}
                className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5 flex items-start justify-between"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3">
                    <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 text-sm font-bold">
                      {index + 1}
                    </span>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
                      {mod.title}
                    </h3>
                  </div>
                  {mod.description && (
                    <p className="mt-2 ml-11 text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
                      {mod.description}
                    </p>
                  )}
                  <div className="mt-2 ml-11 flex flex-wrap gap-2">
                    {mod.theory && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                        Theory
                      </span>
                    )}
                    {mod.plottingexperimentconfig && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                        Experiment
                      </span>
                    )}
                    {mod.interactive_file && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300">
                        3D Model
                      </span>
                    )}
                    {mod.video_link_1 && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300">
                        Video
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex gap-2 ml-4 flex-shrink-0">
                  <Button
                    size="sm"
                    color="gray"
                    onClick={() => setEditingModule(mod)}
                  >
                    <PencilSquareIcon className="h-4 w-4 mr-1" />
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    color="failure"
                    onClick={() => setDeleteTarget(mod)}
                  >
                    <TrashIcon className="h-4 w-4 mr-1" />
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      <Modal show={!!deleteTarget} onClose={() => setDeleteTarget(null)} size="md">
        <Modal.Header>Delete Module</Modal.Header>
        <Modal.Body>
          <p className="text-gray-600 dark:text-gray-300">
            Are you sure you want to delete{" "}
            <strong>{deleteTarget?.title}</strong>? This will also remove all
            associated assignments and quiz questions. This action cannot be
            undone.
          </p>
        </Modal.Body>
        <Modal.Footer>
          <Button color="failure" onClick={handleDelete} disabled={deleting}>
            {deleting ? "Deleting..." : "Delete"}
          </Button>
          <Button color="gray" onClick={() => setDeleteTarget(null)} disabled={deleting}>
            Cancel
          </Button>
        </Modal.Footer>
      </Modal>
    </AppLayout>
  );
}
