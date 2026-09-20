import { useEffect, useState } from "react";
import "./App.css";

function App() {
  // ============================================================
  // Active Navigation Tab
  // ============================================================
  const [activeTab, setActiveTab] = useState("tutor"); // 'tutor' | 'quiz' | 'analytics' | 'materials'

  // ============================================================
  // Ask AI
  // ============================================================
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [copiedAnswer, setCopiedAnswer] = useState(false);

  // ============================================================
  // PDF Upload
  // ============================================================
  const [file, setFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploading, setUploading] = useState(false);

  // ============================================================
  // Quiz
  // ============================================================
  const [quiz, setQuiz] = useState([]);
  const [quizLoading, setQuizLoading] = useState(false);
  const [selectedAnswers, setSelectedAnswers] = useState({});

  // ============================================================
  // Performance & Insights
  // ============================================================
  const [performance, setPerformance] = useState(null);
  const [weakTopics, setWeakTopics] = useState([]);
  const [weakConcepts, setWeakConcepts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);

  // ============================================================
  // Study Materials
  // ============================================================
  const [selectedMaterial, setSelectedMaterial] = useState("");
  const [materials, setMaterials] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState("");

  // Quick prompt suggestions
  const suggestedPrompts = [
    "Summarize the key concepts in this material",
    "What are the most important exam questions?",
    "Explain the core terms and definitions simply",
    "Provide a quick revision cheat sheet",
  ];

  // ============================================================
  // Load Study Materials
  // ============================================================
  const loadMaterials = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/study-materials");
      const data = await response.json();

      if (data.status === "success") {
        setMaterials(data.materials);
        if (data.materials.length > 0 && !selectedMaterial) {
          const firstMaterial = data.materials[0];
          setSelectedMaterial(firstMaterial.filename);
          setSelectedSubject(firstMaterial.subject);
        }
      }
    } catch (error) {
      console.error("Could not load study materials:", error);
    }
  };

  // ============================================================
  // Load Previous Question History
  // ============================================================
  const loadQuestionHistory = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/question-history");
      const data = await response.json();

      if (data.status === "success") {
        const history = [...data.history].reverse();
        setChatHistory(
          history.map((item) => ({
            id: item.id,
            question: item.question,
            answer: item.answer,
            material: item.material,
            created_at: item.created_at,
          }))
        );
      }
    } catch (error) {
      console.error("Could not load question history:", error);
    }
  };

  useEffect(() => {
    loadMaterials();
    loadQuestionHistory();
  }, []);

  // ============================================================
  // Ask AI
  // ============================================================
  const askAI = async (overridePrompt) => {
    const promptToAsk = (typeof overridePrompt === "string" ? overridePrompt : question).trim();

    if (!promptToAsk) {
      alert("Please enter or select a question.");
      return;
    }

    if (!selectedMaterial) {
      alert("Please select a study material first from the top bar or Materials tab.");
      return;
    }

    setLoading(true);
    setAnswer("");
    setCopiedAnswer(false);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/ask-ai?question=${encodeURIComponent(
          promptToAsk
        )}&material=${encodeURIComponent(selectedMaterial)}`,
        { method: "POST" }
      );

      const data = await response.json();

      if (data.status === "success") {
        const newChat = {
          id: data.history_id || Date.now(),
          question: promptToAsk,
          answer: data.answer,
          material: selectedMaterial,
          created_at: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };

        setChatHistory((previousHistory) => [newChat, ...previousHistory]);
        setAnswer(data.answer);
        setQuestion("");
      } else {
        alert(data.detail || "Could not retrieve an answer.");
      }
    } catch (error) {
      console.error("Ask AI error:", error);
      alert("Could not connect to the backend. Please make sure FastAPI is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyAnswer = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedAnswer(true);
    setTimeout(() => setCopiedAnswer(false), 2000);
  };

  // ============================================================
  // Upload PDF
  // ============================================================
  const uploadPDF = async () => {
    if (!file) {
      setUploadMessage("Please choose a PDF file first.");
      return;
    }

    setUploading(true);
    setUploadMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload-material", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setUploadMessage(`Uploaded: ${data.filename} (${data.pages} pages)`);
        await loadMaterials();
        setSelectedMaterial(data.filename);
        if (data.subject) {
          setSelectedSubject(data.subject);
        }
        setFile(null);
      } else {
        setUploadMessage(data.detail || "Upload failed.");
      }
    } catch (error) {
      console.error("Upload error:", error);
      setUploadMessage("Connection error. Make sure the FastAPI backend is running.");
    } finally {
      setUploading(false);
    }
  };

  // ============================================================
  // Generate Quiz
  // ============================================================
  const generateQuiz = async () => {
    if (!selectedMaterial) {
      alert("Please select a study material first.");
      return;
    }

    setQuizLoading(true);
    setQuiz([]);
    setSelectedAnswers({});
    setPerformance(null);
    setWeakTopics([]);
    setWeakConcepts([]);
    setRecommendations([]);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/generate-quiz?material=${encodeURIComponent(
          selectedMaterial
        )}`,
        { method: "POST" }
      );

      const data = await response.json();

      if (data.status === "success") {
        setQuiz(data.questions);
        setSelectedSubject(data.subject);
      } else {
        alert(data.detail || "Could not generate quiz.");
      }
    } catch (error) {
      console.error("Quiz generation error:", error);
      alert("Could not connect to the backend. Make sure FastAPI is running.");
    } finally {
      setQuizLoading(false);
    }
  };

  const selectAnswer = (questionNumber, ans) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionNumber]: ans,
    }));
  };

  // ============================================================
  // Submit Quiz
  // ============================================================
  const submitQuiz = async () => {
    if (quiz.length === 0) return;

    const results = quiz.map((q) => ({
      topic: selectedSubject || "General",
      question: q.question,
      correct: selectedAnswers[q.question_number] === q.correct_answer,
    }));

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze-performance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(results),
      });

      const data = await response.json();

      if (data.status === "success") {
        setPerformance(data.performance);
        setWeakTopics(data.weak_topics || []);
        setRecommendations(data.recommendations || []);
        setWeakConcepts(data.weak_concepts || []);
        setActiveTab("analytics"); // Automatically navigate to results
      } else {
        alert(data.detail || "Could not analyze performance.");
      }
    } catch (error) {
      console.error("Submit quiz error:", error);
      alert("Could not connect to the backend. Make sure FastAPI is running.");
    }
  };

  const handleMaterialChange = (event) => {
    const filename = event.target.value;
    setSelectedMaterial(filename);
    const selected = materials.find((m) => m.filename === filename);
    if (selected) {
      setSelectedSubject(selected.subject);
    }
  };

  const answeredCount = Object.keys(selectedAnswers).length;

  return (
    <div className="app-container">
      {/* ======================================================
          Top Navigation Bar
      ====================================================== */}
      <header className="navbar">
        <div className="navbar-inner">
          <div className="brand-section">
            <div className="brand-icon">🎓</div>
            <div>
              <h1 className="brand-title">Agentic AI Student Assistant</h1>
              <span className="brand-badge">Intelligent Tutor & Practice</span>
            </div>
          </div>

          {/* Quick Context Switcher */}
          <div className="nav-material-pill">
            <span className="active-dot" title="Active Study Context"></span>
            <span>Document:</span>
            <select
              value={selectedMaterial}
              onChange={handleMaterialChange}
              title="Select active study document"
            >
              {materials.length === 0 && <option value="">No material uploaded</option>}
              {materials.map((m) => (
                <option key={m.filename} value={m.filename}>
                  {m.subject ? `${m.subject} — ` : ""}
                  {m.filename}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      {/* ======================================================
          Navigation Tabs Bar
      ====================================================== */}
      <nav className="tabs-bar">
        <div className="tabs-inner">
          <button
            className={`tab-btn ${activeTab === "tutor" ? "active" : ""}`}
            onClick={() => setActiveTab("tutor")}
          >
            💬 AI Tutor
          </button>
          <button
            className={`tab-btn ${activeTab === "quiz" ? "active" : ""}`}
            onClick={() => setActiveTab("quiz")}
          >
            📝 Practice Quiz
            {quiz.length > 0 && <span className="tab-badge">{quiz.length} Qs</span>}
          </button>
          <button
            className={`tab-btn ${activeTab === "analytics" ? "active" : ""}`}
            onClick={() => setActiveTab("analytics")}
          >
            📊 Performance & Insights
            {performance && (
              <span className="tab-badge">{performance.score_percentage}%</span>
            )}
          </button>
          <button
            className={`tab-btn ${activeTab === "materials" ? "active" : ""}`}
            onClick={() => setActiveTab("materials")}
          >
            📁 Study Materials
            <span className="tab-badge">{materials.length}</span>
          </button>
        </div>
      </nav>

      {/* ======================================================
          Main Content Container
      ====================================================== */}
      <main className="main-content">
        {/* ====================================================
            TAB 1: AI TUTOR
        ==================================================== */}
        {activeTab === "tutor" && (
          <div>
            <div className="view-header">
              <div>
                <h2>💬 AI Study Tutor</h2>
                <p>
                  Ask any question regarding your active study material:{" "}
                  <strong>{selectedMaterial || "No document selected"}</strong>
                </p>
              </div>
            </div>

            <div className="tutor-layout">
              {/* Left Column: Chat input & AI Answer */}
              <div className="chat-panel">
                <div className="input-box-wrapper">
                  <textarea
                    className="chat-textarea"
                    placeholder="Ask about concepts, definitions, summaries, or specific formulas..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        askAI();
                      }
                    }}
                  />

                  <div className="input-actions">
                    <span className="input-hint">Press Enter to send, Shift + Enter for newline</span>
                    <button
                      className="btn btn-primary"
                      onClick={() => askAI()}
                      disabled={loading || !question.trim()}
                    >
                      {loading ? (
                        <>
                          <span className="spinner"></span> Thinking...
                        </>
                      ) : (
                        "Ask AI"
                      )}
                    </button>
                  </div>
                </div>

                {/* Prompt Suggestions */}
                <div className="prompt-chips">
                  {suggestedPrompts.map((prompt, idx) => (
                    <button
                      key={idx}
                      className="chip"
                      onClick={() => {
                        setQuestion(prompt);
                        askAI(prompt);
                      }}
                    >
                      ⚡ {prompt}
                    </button>
                  ))}
                </div>

                {/* Current Answer Display */}
                {answer && (
                  <div className="ai-answer-card">
                    <div className="ai-answer-header">
                      <span className="ai-badge">✨ AI Response</span>
                      <button
                        className="btn-copy"
                        onClick={() => handleCopyAnswer(answer)}
                      >
                        {copiedAnswer ? "✓ Copied!" : "📋 Copy"}
                      </button>
                    </div>
                    <div className="ai-text">{answer}</div>
                  </div>
                )}
              </div>

              {/* Right Column: Question History */}
              <div className="history-panel">
                <div className="history-header">
                  <span>📚 Previous Questions</span>
                  <span className="badge badge-primary">{chatHistory.length}</span>
                </div>

                {chatHistory.length === 0 ? (
                  <div className="empty-state" style={{ padding: "30px 10px" }}>
                    <div className="empty-icon">💬</div>
                    <div className="empty-title">No questions yet</div>
                    <p className="empty-desc">
                      Your previous queries and AI answers will be stored here for easy revision.
                    </p>
                  </div>
                ) : (
                  <div className="history-list">
                    {chatHistory.map((item, idx) => (
                      <div className="history-item" key={item.id || idx}>
                        <div className="history-q">Q: {item.question}</div>
                        <div className="history-a">{item.answer}</div>
                        <div className="history-meta">
                          <span>{item.material ? `📄 ${item.material}` : ""}</span>
                          <span>{item.created_at || ""}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ====================================================
            TAB 2: PRACTICE QUIZ
        ==================================================== */}
        {activeTab === "quiz" && (
          <div className="quiz-container">
            <div className="view-header">
              <div>
                <h2>📝 Practice Quiz Generator</h2>
                <p>
                  Generate realistic multiple-choice questions from{" "}
                  <strong>{selectedMaterial || "selected material"}</strong>
                </p>
              </div>

              <button
                className="btn btn-primary"
                onClick={generateQuiz}
                disabled={quizLoading || !selectedMaterial}
              >
                {quizLoading ? (
                  <>
                    <span className="spinner"></span> Generating Questions...
                  </>
                ) : (
                  "✨ Generate New Quiz"
                )}
              </button>
            </div>

            {quiz.length === 0 && !quizLoading && (
              <div className="card-panel empty-state">
                <div className="empty-icon">📝</div>
                <div className="empty-title">No Active Quiz</div>
                <p className="empty-desc">
                  Select a study document and click <strong>Generate New Quiz</strong> to start practicing.
                </p>
                <button
                  className="btn btn-primary"
                  onClick={generateQuiz}
                  disabled={!selectedMaterial}
                >
                  Generate Quiz Now
                </button>
              </div>
            )}

            {quiz.length > 0 && (
              <div className="quiz-container">
                <div className="quiz-toolbar">
                  <div>
                    <strong>Subject:</strong> {selectedSubject || "General"} &bull;{" "}
                    <strong>Questions:</strong> {quiz.length}
                  </div>
                  <div>
                    <span className="badge badge-primary">
                      Answered: {answeredCount} / {quiz.length}
                    </span>
                  </div>
                </div>

                {quiz.map((q) => (
                  <div className="quiz-card" key={q.question_number}>
                    <div className="quiz-question-title">
                      <span className="q-num-badge">Q{q.question_number}</span>
                      <span>{q.question}</span>
                    </div>

                    <div className="options-grid">
                      {q.options.map((option, idx) => {
                        const isSelected =
                          selectedAnswers[q.question_number] === option;
                        return (
                          <label
                            className={`option-tile ${isSelected ? "selected" : ""}`}
                            key={idx}
                          >
                            <input
                              type="radio"
                              name={`question-${q.question_number}`}
                              value={option}
                              checked={isSelected}
                              onChange={() => selectAnswer(q.question_number, option)}
                            />
                            <span className="option-text">{option}</span>
                          </label>
                        );
                      })}
                    </div>
                  </div>
                ))}

                <div className="quiz-submit-bar">
                  <button
                    className="btn btn-primary"
                    onClick={submitQuiz}
                    disabled={answeredCount === 0}
                  >
                    Submit Quiz & Analyze Performance ({answeredCount}/{quiz.length})
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ====================================================
            TAB 3: PERFORMANCE & INSIGHTS
        ==================================================== */}
        {activeTab === "analytics" && (
          <div>
            <div className="view-header">
              <div>
                <h2>📊 Learning Insights & Performance</h2>
                <p>Track your accuracy, identify weak areas, and get personalized revision advice.</p>
              </div>
            </div>

            {!performance ? (
              <div className="card-panel empty-state">
                <div className="empty-icon">📈</div>
                <div className="empty-title">No Performance Data Yet</div>
                <p className="empty-desc">
                  Complete a practice quiz to unlock detailed performance analytics, weak topic detection, and custom study recommendations.
                </p>
                <button
                  className="btn btn-primary"
                  onClick={() => setActiveTab("quiz")}
                >
                  Go to Practice Quiz
                </button>
              </div>
            ) : (
              <div>
                {/* Stats Grid */}
                <div className="stats-grid">
                  <div className="stat-card primary">
                    <span className="stat-label">Total Questions</span>
                    <span className="stat-value">{performance.total_questions}</span>
                    <span className="stat-desc">Questions evaluated</span>
                  </div>

                  <div className="stat-card success">
                    <span className="stat-label">Correct Answers</span>
                    <span className="stat-value">{performance.correct_answers}</span>
                    <span className="stat-desc">Well understood</span>
                  </div>

                  <div className="stat-card danger">
                    <span className="stat-label">Incorrect Answers</span>
                    <span className="stat-value">{performance.incorrect_answers}</span>
                    <span className="stat-desc">Needs revision</span>
                  </div>

                  <div className="stat-card warning">
                    <span className="stat-label">Overall Score</span>
                    <span className="stat-value">{performance.score_percentage}%</span>
                    <span className="stat-desc">
                      {performance.score_percentage >= 75
                        ? "Great mastery!"
                        : performance.score_percentage >= 50
                        ? "Moderate progress"
                        : "Focus on weak areas"}
                    </span>
                  </div>
                </div>

                {/* Split Insights Layout */}
                <div className="analytics-layout">
                  {/* Left Box: Weak Topics */}
                  <div className="section-box">
                    <h3>⚠️ Topic Analysis</h3>
                    {weakTopics.length === 0 ? (
                      <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>
                        No specific weak topics detected. Great job!
                      </p>
                    ) : (
                      weakTopics.map((topic, idx) => (
                        <div className="topic-card" key={idx}>
                          <div className="topic-header">
                            <span className="topic-name">{topic.topic}</span>
                            <span
                              className={`badge ${
                                topic.score_percentage >= 70
                                  ? "badge-success"
                                  : topic.score_percentage >= 40
                                  ? "badge-warning"
                                  : "badge-danger"
                              }`}
                            >
                              {topic.status || `${topic.score_percentage}%`}
                            </span>
                          </div>
                          <div className="progress-track">
                            <div
                              className="progress-fill"
                              style={{
                                width: `${topic.score_percentage}%`,
                                backgroundColor:
                                  topic.score_percentage >= 70
                                    ? "var(--success)"
                                    : topic.score_percentage >= 40
                                    ? "var(--warning)"
                                    : "var(--danger)",
                              }}
                            ></div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>

                  {/* Right Box: Recommendations & Concepts */}
                  <div className="section-box">
                    <h3>💡 Actionable Study Recommendations</h3>
                    {recommendations.length === 0 ? (
                      <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>
                        No recommendations at this time. Keep practicing!
                      </p>
                    ) : (
                      recommendations.map((item, idx) => {
                        const priorityLower = (item.priority || "medium").toLowerCase();
                        return (
                          <div className={`rec-card ${priorityLower}`} key={idx}>
                            <div className="rec-title">
                              <span>{item.topic}</span>
                              <span
                                className={`badge ${
                                  priorityLower === "high"
                                    ? "badge-danger"
                                    : priorityLower === "medium"
                                    ? "badge-warning"
                                    : "badge-primary"
                                }`}
                              >
                                {item.priority} Priority
                              </span>
                            </div>
                            <div className="rec-text">{item.recommendation}</div>
                          </div>
                        );
                      })
                    )}

                    {/* Specific concepts to revise */}
                    {weakConcepts.length > 0 && (
                      <div style={{ marginTop: "24px" }}>
                        <h4 style={{ fontSize: "15px", marginBottom: "12px" }}>
                          🎯 Specific Questions to Review
                        </h4>
                        {weakConcepts.map((item, idx) => (
                          <div className="concept-card" key={idx}>
                            <div className="concept-q">
                              Q{idx + 1}: {item.question}
                            </div>
                            <span className="concept-status">⚠️ {item.status}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ====================================================
            TAB 4: STUDY MATERIALS
        ==================================================== */}
        {activeTab === "materials" && (
          <div>
            <div className="view-header">
              <div>
                <h2>📁 Study Materials Library</h2>
                <p>Upload PDF documents and switch active study context.</p>
              </div>
            </div>

            <div className="materials-layout">
              {/* Upload Card */}
              <div className="card-panel">
                <h3 style={{ fontSize: "16px", marginBottom: "12px", fontWeight: 700 }}>
                  Upload New Material
                </h3>

                <label className="upload-dropzone">
                  <div className="upload-icon">📄</div>
                  <div className="upload-title">Choose or drag a PDF</div>
                  <div className="upload-hint">Supports course notes, slides, syllabi (.pdf)</div>

                  <input
                    type="file"
                    accept=".pdf"
                    className="file-input-hidden"
                    onChange={(e) => setFile(e.target.files[0] || null)}
                  />

                  <span className="btn btn-secondary btn-sm">Browse File</span>
                </label>

                {file && (
                  <div className="selected-file-card">
                    <div className="selected-file-info">
                      <span className="file-badge-icon">📄</span>
                      <div>
                        <div className="selected-file-name">{file.name}</div>
                        <div className="selected-file-size">
                          {(file.size / (1024 * 1024)).toFixed(2)} MB
                        </div>
                      </div>
                    </div>
                    <button
                      type="button"
                      className="btn-clear-file"
                      onClick={(e) => {
                        e.stopPropagation();
                        setFile(null);
                      }}
                      title="Remove file"
                    >
                      ✕
                    </button>
                  </div>
                )}

                <button
                  className="btn btn-primary"
                  style={{ width: "100%" }}
                  onClick={uploadPDF}
                  disabled={uploading || !file}
                >
                  {uploading ? (
                    <>
                      <span className="spinner"></span> Uploading...
                    </>
                  ) : (
                    "Upload & Process PDF"
                  )}
                </button>

                {uploadMessage && (
                  <div
                    className={`alert ${
                      uploadMessage.includes("successfully") || uploadMessage.includes("Uploaded")
                        ? "alert-success"
                        : "alert-error"
                    }`}
                  >
                    {uploadMessage}
                  </div>
                )}
              </div>

              {/* Materials Grid */}
              <div>
                <h3 style={{ fontSize: "16px", marginBottom: "16px", fontWeight: 700 }}>
                  Available Documents ({materials.length})
                </h3>

                {materials.length === 0 ? (
                  <div className="card-panel empty-state">
                    <div className="empty-icon">📂</div>
                    <div className="empty-title">No Materials Uploaded</div>
                    <p className="empty-desc">
                      Upload your first syllabus, textbook chapter, or lecture notes to get started.
                    </p>
                  </div>
                ) : (
                  <div className="materials-grid">
                    {materials.map((m) => {
                      const isActive = selectedMaterial === m.filename;
                      return (
                        <div
                          className={`material-card ${isActive ? "active-material" : ""}`}
                          key={m.filename}
                        >
                          <div className="mat-top">
                            <div className="mat-icon">📑</div>
                            <div className="mat-info">
                              <div className="mat-name" title={m.filename}>
                                {m.filename}
                              </div>
                              <div className="mat-subject">
                                {m.subject ? `Subject: ${m.subject}` : "General Study"}
                              </div>
                            </div>
                          </div>

                          <div className="mat-bottom">
                            <span className="mat-pages">
                              {m.pages ? `${m.pages} pages` : "PDF"}
                            </span>

                            {isActive ? (
                              <span className="badge badge-success">✓ Active</span>
                            ) : (
                              <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => {
                                  setSelectedMaterial(m.filename);
                                  if (m.subject) setSelectedSubject(m.subject);
                                }}
                              >
                                Set Active
                              </button>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;