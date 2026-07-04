import { useState } from "react";
import { useToast } from "../hooks/useToast";
import { ticketApi } from "../api/client";
import { ImportSummary } from "../types";
import "./BulkImport.css";

interface BulkImportProps {
  onSuccess?: () => void;
}

export function BulkImport({ onSuccess }: BulkImportProps) {
  const { addToast } = useToast();
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [summary, setSummary] = useState<ImportSummary | null>(null);

  const handleFile = async (file: File) => {
    const validTypes = [
      "text/csv",
      "application/json",
      "application/xml",
      "text/xml",
    ];
    const validExtensions = [".csv", ".json", ".xml"];

    const isValidType = validTypes.includes(file.type);
    const hasValidExtension = validExtensions.some((ext) =>
      file.name.toLowerCase().endsWith(ext)
    );

    if (!isValidType && !hasValidExtension) {
      addToast("Please upload a CSV, JSON, or XML file", "error");
      return;
    }

    setUploading(true);
    try {
      const result = await ticketApi.importFile(file);
      setSummary(result);

      if (result.failed === 0) {
        addToast(
          `Successfully imported ${result.successful} ticket(s)!`,
          "success"
        );
      } else {
        addToast(
          `Imported ${result.successful} ticket(s) with ${result.failed} error(s)`,
          "info"
        );
      }

      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      addToast(
        err instanceof Error ? err.message : "Failed to import file",
        "error"
      );
    } finally {
      setUploading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const clearSummary = () => setSummary(null);

  return (
    <div className="bulk-import-container">
      {!summary ? (
        <>
          <h2>Bulk Import Tickets</h2>
          <p>Import multiple tickets from CSV, JSON, or XML files</p>

          <div
            className={`import-dropzone ${isDragging ? "dragging" : ""}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <svg
              className="upload-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            <p>Drag and drop your file here or click to browse</p>
            <input
              type="file"
              accept=".csv,.json,.xml"
              onChange={handleInputChange}
              disabled={uploading}
              style={{ display: "none" }}
              id="import-file-input"
            />
            <label htmlFor="import-file-input" className="btn btn-primary">
              {uploading ? "Uploading..." : "Select File"}
            </label>
          </div>

          <div className="import-info">
            <h3>Supported Formats</h3>
            <ul>
              <li>CSV (.csv)</li>
              <li>JSON (.json)</li>
              <li>XML (.xml)</li>
            </ul>
            <p className="text-muted">
              Each record is validated independently. Invalid records will be reported
              with error messages while valid ones are imported.
            </p>
          </div>
        </>
      ) : (
        <div className="import-summary">
          <h2>Import Summary</h2>

          <div className="summary-stats">
            <div className="stat">
              <span className="stat-label">Total Records</span>
              <span className="stat-value">{summary.total}</span>
            </div>
            <div className="stat success">
              <span className="stat-label">Successful</span>
              <span className="stat-value">{summary.successful}</span>
            </div>
            <div className="stat error">
              <span className="stat-label">Failed</span>
              <span className="stat-value">{summary.failed}</span>
            </div>
          </div>

          {summary.errors.length > 0 && (
            <div className="error-list">
              <h3>Errors</h3>
              <div className="errors">
                {summary.errors.map((error, idx) => (
                  <div key={idx} className="error-item">
                    <span className="error-record">Record {error.record_index}</span>
                    <span className="error-message">{error.message}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {summary.created_ticket_ids.length > 0 && (
            <div className="created-list">
              <h3>Created Tickets ({summary.created_ticket_ids.length})</h3>
              <ul className="ticket-ids">
                {summary.created_ticket_ids.slice(0, 10).map((id) => (
                  <li key={id}>{id}</li>
                ))}
                {summary.created_ticket_ids.length > 10 && (
                  <li className="more">
                    +{summary.created_ticket_ids.length - 10} more
                  </li>
                )}
              </ul>
            </div>
          )}

          <button onClick={clearSummary} className="btn btn-primary">
            Import Another File
          </button>
        </div>
      )}
    </div>
  );
}
