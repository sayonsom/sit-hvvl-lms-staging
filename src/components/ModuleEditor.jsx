import React, { useState, useEffect } from "react";
import { Button, Label, TextInput, Textarea, FileInput } from "flowbite-react";
import axios from "axios";
import { API_URL } from "../env";

const apiUrl = API_URL;

const ModuleEditor = ({ module, courseId, onSave, onCancel }) => {
  const isEditing = !!module;

  const [form, setForm] = useState({
    title: "",
    description: "",
    concept: "",
    fun_fact: "",
    video_link_1: "",
    video_link_2: "",
    theory: "",
    plottingexperimentconfig: "",
    interactive_file: "",
    InteractiveConfig: "",
    attachment_1_link: "",
    attachment_2_link: "",
    attachment_3_link: "",
  });

  const [theoryFile, setTheoryFile] = useState(null);
  const [configFile, setConfigFile] = useState(null);
  const [modelFile, setModelFile] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (module) {
      setForm({
        title: module.title || "",
        description: module.description || "",
        concept: module.concept || "",
        fun_fact: module.fun_fact || "",
        video_link_1: module.video_link_1 || "",
        video_link_2: module.video_link_2 || "",
        theory: module.theory || "",
        plottingexperimentconfig: module.plottingexperimentconfig || "",
        interactive_file: module.interactive_file || "",
        InteractiveConfig: module.InteractiveConfig || "",
        attachment_1_link: module.attachment_1_link || "",
        attachment_2_link: module.attachment_2_link || "",
        attachment_3_link: module.attachment_3_link || "",
      });
    }
  }, [module]);

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const uploadFile = async (file, folder) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("folder", folder);
    const response = await axios.post(`${apiUrl}/upload-content/`, formData);
    return response.data.path;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      // Generate a folder name from the title
      const folder = form.title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "_")
        .replace(/^_|_$/g, "");

      const updatedForm = { ...form };

      // Upload files if selected
      if (theoryFile) {
        updatedForm.theory = await uploadFile(theoryFile, folder);
      }
      if (configFile) {
        updatedForm.plottingexperimentconfig = await uploadFile(configFile, folder);
      }
      if (modelFile) {
        updatedForm.interactive_file = await uploadFile(modelFile, folder);
      }

      // Build the module payload
      const payload = {
        course_id: parseInt(courseId),
        ...updatedForm,
      };

      if (isEditing) {
        await axios.put(`${apiUrl}/modules/${module.module_id}`, payload);
      } else {
        await axios.post(`${apiUrl}/modules/?course_id=${courseId}`, payload);
      }

      onSave();
    } catch (err) {
      console.error("Error saving module:", err);
      setError(err.response?.data?.detail || "Failed to save module");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
        {isEditing ? "Edit Module" : "Create New Module"}
      </h3>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title */}
        <div>
          <Label htmlFor="title" value="Module Title *" />
          <TextInput
            id="title"
            value={form.title}
            onChange={(e) => handleChange("title", e.target.value)}
            required
            placeholder="e.g., Ferranti Effect"
          />
        </div>

        {/* Description */}
        <div>
          <Label htmlFor="description" value="Description" />
          <Textarea
            id="description"
            value={form.description}
            onChange={(e) => handleChange("description", e.target.value)}
            rows={3}
            placeholder="Brief description of the module"
          />
        </div>

        {/* Concept */}
        <div>
          <Label htmlFor="concept" value="Key Concept" />
          <Textarea
            id="concept"
            value={form.concept}
            onChange={(e) => handleChange("concept", e.target.value)}
            rows={3}
            placeholder="Core concept explanation for students"
          />
        </div>

        {/* Fun Fact */}
        <div>
          <Label htmlFor="fun_fact" value="Fun Fact" />
          <Textarea
            id="fun_fact"
            value={form.fun_fact}
            onChange={(e) => handleChange("fun_fact", e.target.value)}
            rows={2}
            placeholder="An interesting fact about this topic"
          />
        </div>

        <hr className="border-gray-200 dark:border-gray-700" />

        {/* File Uploads */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="theoryFile" value="Theory Content (.md)" />
            <FileInput
              id="theoryFile"
              accept=".md"
              onChange={(e) => setTheoryFile(e.target.files[0])}
              helperText={form.theory ? `Current: ${form.theory}` : "Upload a Markdown file"}
            />
          </div>

          <div>
            <Label htmlFor="configFile" value="Experiment Config (.json)" />
            <FileInput
              id="configFile"
              accept=".json"
              onChange={(e) => setConfigFile(e.target.files[0])}
              helperText={form.plottingexperimentconfig ? `Current: ${form.plottingexperimentconfig}` : "Upload a JSON config"}
            />
          </div>

          <div>
            <Label htmlFor="modelFile" value="3D Model (.glb / .gltf)" />
            <FileInput
              id="modelFile"
              accept=".glb,.gltf"
              onChange={(e) => setModelFile(e.target.files[0])}
              helperText={form.interactive_file ? `Current: ${form.interactive_file}` : "Upload a 3D model file"}
            />
          </div>
        </div>

        <hr className="border-gray-200 dark:border-gray-700" />

        {/* Video Links */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="video_link_1" value="Video Link 1" />
            <TextInput
              id="video_link_1"
              value={form.video_link_1}
              onChange={(e) => handleChange("video_link_1", e.target.value)}
              placeholder="https://youtu.be/..."
            />
          </div>
          <div>
            <Label htmlFor="video_link_2" value="Video Link 2" />
            <TextInput
              id="video_link_2"
              value={form.video_link_2}
              onChange={(e) => handleChange("video_link_2", e.target.value)}
              placeholder="https://youtu.be/..."
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4">
          <Button type="submit" gradientDuoTone="purpleToPink" disabled={saving}>
            {saving ? "Saving..." : isEditing ? "Update Module" : "Create Module"}
          </Button>
          <Button color="gray" onClick={onCancel} disabled={saving}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ModuleEditor;
