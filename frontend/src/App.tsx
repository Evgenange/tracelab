import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Plot from "react-plotly.js";

import {
  createDataset,
  getDatasets,
  getDatasetVersions,
  getProjects,
  getProvenance,
  getQualityReport,
  uploadDatasetVersion,
  type Dataset,
  type DatasetVersion,
  type Project,
  type Provenance,
  type QualityReport,
} from "./api/client";

import "./App.css";

function App() {
  const [project, setProject] =
    useState<Project | null>(null);

  const [datasets, setDatasets] = useState<Dataset[]>(
    [],
  );

  const [selectedDataset, setSelectedDataset] =
    useState<Dataset | null>(null);

  const [versions, setVersions] = useState<
    DatasetVersion[]
  >([]);

  const [selectedVersion, setSelectedVersion] =
    useState<DatasetVersion | null>(null);

  const [report, setReport] =
    useState<QualityReport | null>(null);

  const [provenance, setProvenance] =
    useState<Provenance | null>(null);

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [creatingDataset, setCreatingDataset] =
    useState(false);

  const [error, setError] = useState<string | null>(
    null,
  );

  const loadDatasets = useCallback(
    async (projectId: string) => {
      const data = await getDatasets(projectId);

      const ordered = [...data].sort(
        (a, b) =>
          new Date(b.created_at).getTime() -
          new Date(a.created_at).getTime(),
      );

      setDatasets(ordered);

      return ordered;
    },
    [],
  );

  const loadVersions = useCallback(
    async (datasetId: string) => {
      const data =
        await getDatasetVersions(datasetId);

      const ordered = [...data].sort(
        (a, b) =>
          b.version_number - a.version_number,
      );

      setVersions(ordered);

      return ordered;
    },
    [],
  );

  const selectVersion = useCallback(
    async (version: DatasetVersion) => {
      setSelectedVersion(version);
      setReport(null);
      setProvenance(null);
      setError(null);

      if (version.status !== "completed") {
        return;
      }

      try {
        const [quality, provenanceData] =
          await Promise.all([
            getQualityReport(version.id),
            getProvenance(version.id),
          ]);

        setReport(quality);
        setProvenance(provenanceData);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load version information",
        );
      }
    },
    [],
  );

  const selectDataset = useCallback(
    async (dataset: Dataset) => {
      setSelectedDataset(dataset);
      setSelectedVersion(null);
      setReport(null);
      setProvenance(null);
      setVersions([]);
      setError(null);

      try {
        const data = await loadVersions(dataset.id);

        const latestCompleted = data.find(
          (version) =>
            version.status === "completed",
        );

        if (latestCompleted) {
          await selectVersion(latestCompleted);
        } else if (data.length > 0) {
          setSelectedVersion(data[0]);
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load dataset versions",
        );
      }
    },
    [loadVersions, selectVersion],
  );

  useEffect(() => {
    async function initialise() {
      try {
        const projects = await getProjects();

        if (projects.length === 0) {
          setError(
            "No TraceLab project exists yet.",
          );

          return;
        }

        const activeProject = projects[0];

        setProject(activeProject);

        const projectDatasets =
          await loadDatasets(activeProject.id);

        if (projectDatasets.length > 0) {
          await selectDataset(projectDatasets[0]);
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to initialise TraceLab",
        );
      } finally {
        setLoading(false);
      }
    }

    void initialise();
  }, [loadDatasets, selectDataset]);

  async function handleCreateDataset() {
    if (!project) {
      return;
    }

    const name = window.prompt(
      "Dataset name",
      "European Sustainability Data",
    );

    if (!name?.trim()) {
      return;
    }

    const description = window.prompt(
      "Dataset description (optional)",
      "",
    );

    setCreatingDataset(true);
    setError(null);

    try {
      const dataset = await createDataset(
        project.id,
        name.trim(),
        description?.trim() || null,
      );

      await loadDatasets(project.id);
      await selectDataset(dataset);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to create dataset",
      );
    } finally {
      setCreatingDataset(false);
    }
  }

  async function handleUpload(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    if (!file || !selectedDataset) {
      event.target.value = "";
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const version = await uploadDatasetVersion(
        selectedDataset.id,
        file,
      );

      setSelectedVersion(version);
      setReport(null);
      setProvenance(null);

      let attempts = 0;

      const poll = window.setInterval(async () => {
        attempts += 1;

        try {
          const updatedVersions =
            await loadVersions(
              selectedDataset.id,
            );

          const updated = updatedVersions.find(
            (item) => item.id === version.id,
          );

          if (!updated) {
            return;
          }

          setSelectedVersion(updated);

          if (updated.status === "completed") {
            window.clearInterval(poll);
            setUploading(false);

            const [quality, provenanceData] =
              await Promise.all([
                getQualityReport(updated.id),
                getProvenance(updated.id),
              ]);

            setReport(quality);
            setProvenance(provenanceData);

            return;
          }

          if (
            updated.status === "failed" ||
            attempts >= 30
          ) {
            window.clearInterval(poll);
            setUploading(false);

            if (updated.status === "failed") {
              setError(
                "Dataset processing failed.",
              );
            } else {
              setError(
                "Processing is taking longer than expected. Refresh to check again.",
              );
            }
          }
        } catch (err) {
          window.clearInterval(poll);
          setUploading(false);

          setError(
            err instanceof Error
              ? err.message
              : "Unable to check processing status",
          );
        }
      }, 1000);
    } catch (err) {
      setUploading(false);

      setError(
        err instanceof Error
          ? err.message
          : "Upload failed",
      );
    } finally {
      event.target.value = "";
    }
  }

  if (loading) {
    return (
      <main className="page">
        Loading TraceLab...
      </main>
    );
  }

  return (
    <main className="page">
      <header className="header">
        <div>
          <p className="eyebrow">
            TraceLab
          </p>

          <h1>
            Dataset Reproducibility Platform
          </h1>

          <p className="subtitle">
            Version datasets, profile data quality
            asynchronously and preserve reproducible
            provenance metadata.
          </p>
        </div>

        <div className="header-actions">
          <button
            className="secondary-button"
            onClick={() =>
              void handleCreateDataset()
            }
            disabled={
              creatingDataset || !project
            }
          >
            {creatingDataset
              ? "Creating..."
              : "+ New Dataset"}
          </button>

          <label
            className={`upload-button ${
              !selectedDataset
                ? "disabled"
                : ""
            }`}
          >
            {uploading
              ? "Processing..."
              : "Upload New Version"}

            <input
              type="file"
              accept=".csv,text/csv"
              onChange={handleUpload}
              disabled={
                uploading || !selectedDataset
              }
            />
          </label>
        </div>
      </header>

      {project && (
        <div className="project-context">
          <span>Project</span>
          <strong>{project.name}</strong>
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <section className="dataset-layout">
        <aside className="datasets-panel">
          <div className="section-heading">
            <h2>Datasets</h2>
            <span>{datasets.length}</span>
          </div>

          {datasets.length === 0 ? (
            <div className="sidebar-empty">
              No datasets yet.
            </div>
          ) : (
            <div className="dataset-list">
              {datasets.map((dataset) => (
                <button
                  key={dataset.id}
                  className={`dataset-item ${
                    selectedDataset?.id ===
                    dataset.id
                      ? "selected"
                      : ""
                  }`}
                  onClick={() =>
                    void selectDataset(dataset)
                  }
                >
                  <strong>
                    {dataset.name}
                  </strong>

                  <small>
                    {dataset.description ||
                      "No description"}
                  </small>
                </button>
              ))}
            </div>
          )}
        </aside>

        <section className="workspace">
          <aside className="versions-panel">
            <div className="section-heading">
              <div>
                <h2>Versions</h2>

                {selectedDataset && (
                  <small>
                    {selectedDataset.name}
                  </small>
                )}
              </div>

              <span>{versions.length}</span>
            </div>

            {!selectedDataset ? (
              <div className="sidebar-empty">
                Select a dataset.
              </div>
            ) : versions.length === 0 ? (
              <div className="sidebar-empty">
                No versions yet. Upload a CSV.
              </div>
            ) : (
              <div className="version-list">
                {versions.map((version) => (
                  <button
                    className={`version-item ${
                      selectedVersion?.id ===
                      version.id
                        ? "selected"
                        : ""
                    }`}
                    key={version.id}
                    onClick={() =>
                      void selectVersion(version)
                    }
                  >
                    <div>
                      <strong>
                        Version{" "}
                        {version.version_number}
                      </strong>

                      <small>
                        {
                          version.original_filename
                        }
                      </small>
                    </div>

                    <span
                      className={`version-status ${version.status}`}
                    >
                      {version.status}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </aside>

          <section className="content">
            {!selectedDataset && (
              <section className="panel empty-state">
                <h3>
                  Select or create a dataset
                </h3>

                <p>
                  Each dataset maintains its own
                  immutable version history.
                </p>
              </section>
            )}

            {selectedDataset &&
              !selectedVersion && (
                <section className="panel empty-state">
                  <h3>
                    {selectedDataset.name}
                  </h3>

                  <p>
                    Upload the first CSV version of
                    this dataset.
                  </p>
                </section>
              )}

            {selectedVersion && (
              <>
                <section className="version-header panel">
                  <div>
                    <p className="eyebrow">
                      {selectedDataset?.name}
                    </p>

                    <h2>
                      Version{" "}
                      {
                        selectedVersion.version_number
                      }{" "}
                      ·{" "}
                      {
                        selectedVersion.original_filename
                      }
                    </h2>

                    <p className="version-id">
                      {selectedVersion.id}
                    </p>
                  </div>

                  <span
                    className={`version-status ${selectedVersion.status}`}
                  >
                    {selectedVersion.status}
                  </span>
                </section>

                {selectedVersion.status !==
                  "completed" && (
                  <section className="panel empty-state">
                    <h3>
                      {selectedVersion.status ===
                      "uploaded"
                        ? "Waiting for processing"
                        : "Processing dataset"}
                    </h3>

                    <p>
                      TraceLab is profiling this
                      immutable dataset version in
                      the background.
                    </p>
                  </section>
                )}

                {report && (
                  <>
                    <QualityDashboard
                      report={report}
                    />

                    {provenance && (
                      <ProvenancePanel
                        provenance={provenance}
                      />
                    )}
                  </>
                )}
              </>
            )}
          </section>
        </section>
      </section>
    </main>
  );
}

function QualityDashboard({
  report,
}: {
  report: QualityReport;
}) {
  return (
    <>
      <section className="metrics">
        <MetricCard
          label="Rows"
          value={report.row_count}
        />

        <MetricCard
          label="Columns"
          value={report.column_count}
        />

        <MetricCard
          label="Null values"
          value={report.null_count}
        />

        <MetricCard
          label="Duplicate rows"
          value={report.duplicate_row_count}
        />
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>
              Null values by column
            </h2>

            <p>
              Missing values detected during
              dataset profiling.
            </p>
          </div>
        </div>

        <Plot
          data={[
            {
              type: "bar",
              x: Object.keys(
                report.null_counts_json,
              ),
              y: Object.values(
                report.null_counts_json,
              ),
            },
          ]}
          layout={{
            autosize: true,
            height: 330,
            margin: {
              l: 50,
              r: 20,
              t: 20,
              b: 50,
            },
            paper_bgcolor: "transparent",
            plot_bgcolor: "transparent",
            yaxis: {
              title: {
                text: "Null values",
              },
              rangemode: "tozero",
            },
          }}
          useResizeHandler
          style={{ width: "100%" }}
          config={{
            displayModeBar: false,
            responsive: true,
          }}
        />
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Schema</h2>

            <p>
              Inferred schema for this immutable
              version.
            </p>
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Column</th>
                <th>Data type</th>
                <th>Null values</th>
              </tr>
            </thead>

            <tbody>
              {Object.entries(
                report.column_schema,
              ).map(
                ([column, dataType]) => (
                  <tr key={column}>
                    <td className="column-name">
                      {column}
                    </td>

                    <td>
                      <span className="data-type">
                        {dataType}
                      </span>
                    </td>

                    <td>
                      {report.null_counts_json[
                        column
                      ] ?? 0}
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function ProvenancePanel({
  provenance,
}: {
  provenance: Provenance;
}) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>
            Reproducibility & Provenance
          </h2>

          <p>
            Metadata identifying the source dataset
            and processing run.
          </p>
        </div>
      </div>

      <div className="provenance-grid">
        <ProvenanceItem
          label="Pipeline"
          value={`${provenance.pipeline_name} v${provenance.pipeline_version}`}
        />

        <ProvenanceItem
          label="Source file"
          value={
            provenance.original_filename
          }
        />

        <ProvenanceItem
          label="Dataset version"
          value={`Version ${provenance.version_number}`}
        />

        <ProvenanceItem
          label="Processing status"
          value={
            provenance.processing_status ??
            "Not processed"
          }
        />

        <ProvenanceItem
          label="SHA-256"
          value={provenance.sha256}
          mono
        />

        <ProvenanceItem
          label="Processing job"
          value={
            provenance.processing_job_id ??
            "None"
          }
          mono
        />

        <ProvenanceItem
          label="Created"
          value={new Date(
            provenance.version_created_at,
          ).toLocaleString()}
        />

        <ProvenanceItem
          label="Completed"
          value={
            provenance.processing_completed_at
              ? new Date(
                  provenance.processing_completed_at,
                ).toLocaleString()
              : "Not completed"
          }
        />
      </div>
    </section>
  );
}

function ProvenanceItem({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="provenance-item">
      <span>{label}</span>

      <strong
        className={
          mono ? "mono" : undefined
        }
      >
        {value}
      </strong>
    </div>
  );
}

function MetricCard({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <article className="metric-card">
      <p>{label}</p>

      <strong>
        {value.toLocaleString()}
      </strong>
    </article>
  );
}

export default App;