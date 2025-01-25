import React, { useState } from "react";
import UploadIcon from "../../assets/images/upload-file.png";
import "./Fileupload.css";
const FileUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState("");
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
      setFileName(event.target.files[0]?.name || "");
    }
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (file) {
      // Handle file upload logic here
      console.log("File submitted:", file);
    }
  };

  return (
    <div className="file-upload-container">
      <h1>File Analyzer App</h1>
      <p>Please upload the file you have questions about.</p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="file-upload"
            className="flex flex-col items-center cursor-pointer"
          >
            <div className="mb-3">
              <img src={UploadIcon} alt="Upload" height={400}/>
            </div>
          </label>
          <input
            id="file-upload"
            type="file"
            onChange={handleFileChange}
            className="hidden-input"
          />
        </div>

        <button
          type="submit"
          className="submit-button"
          disabled={!fileName}
        >
          Upload File
        </button>
      </form>
    </div>
  );
};

export default FileUpload;
