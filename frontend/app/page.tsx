"use client";

import { useState } from "react";
import { Container, Row, Col, Card, Form, Button, Alert, ProgressBar } from "react-bootstrap";

interface PredictionResult {
  approved: number;
  default_probability: number;
  approval_threshold: number;
}

export default function Home() {
  const [formData, setFormData] = useState({
    person_age: "",
    person_income: "",
    person_home_ownership: "RENT",
    person_emp_length: "",
    loan_intent: "PERSONAL",
    loan_grade: "D",
    loan_amnt: "",
    loan_int_rate: "",
    loan_percent_income: "",
    cb_person_default_on_file: "N",
    cb_person_cred_hist_length: ""
  });

  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      // Convert string values to appropriate types
      const payload = {
        person_age: parseInt(formData.person_age),
        person_income: parseInt(formData.person_income),
        person_home_ownership: formData.person_home_ownership,
        person_emp_length: parseFloat(formData.person_emp_length),
        loan_intent: formData.loan_intent,
        loan_grade: formData.loan_grade,
        loan_amnt: parseInt(formData.loan_amnt),
        loan_int_rate: parseFloat(formData.loan_int_rate),
        loan_percent_income: parseFloat(formData.loan_percent_income),
        cb_person_default_on_file: formData.cb_person_default_on_file,
        cb_person_cred_hist_length: parseInt(formData.cb_person_cred_hist_length)
      };

      const response = await fetch("/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Prediction failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container fluid className="py-5" style={{ backgroundColor: "#f8f9fa", minHeight: "100vh" }}>
      <Container style={{ maxWidth: "900px" }}>
        <Row className="mb-4">
          <Col xs={12}>
            <h1 className="mb-2">Credit Approval Assessment</h1>
            <p className="text-muted">
              Our machine learning model analyzes your financial profile and loan details to
              calculate your credit approval rating. Based on multiple factors including your
              income, credit history, and loan characteristics, we determine the likelihood of
              approval and provide a comprehensive risk assessment.
            </p>
          </Col>
        </Row>

        <Row>
          <Col lg={8}>
            <Card className="shadow-sm">
              <Card.Body>
                <Form onSubmit={handleSubmit}>
                  {/* Applicant Profile Section */}
                  <Card.Title className="mb-3">Applicant Profile</Card.Title>
                  <Row className="mb-3">
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Age</Form.Label>
                        <Form.Control
                          type="number"
                          name="person_age"
                          value={formData.person_age}
                          onChange={(e) => handleChange(e)}
                          required
                          min="18"
                          max="100"
                        />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Annual Income ($)</Form.Label>
                        <Form.Control
                          type="number"
                          name="person_income"
                          value={formData.person_income}
                          onChange={(e) => handleChange(e)}
                          required
                          min="0"
                        />
                      </Form.Group>
                    </Col>
                  </Row>

                  <Row className="mb-3">
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Home Ownership</Form.Label>
                        <Form.Select
                          name="person_home_ownership"
                          value={formData.person_home_ownership}
                          onChange={handleChange}
                          required
                        >
                          <option value="RENT">Rent</option>
                          <option value="OWN">Own</option>
                          <option value="MORTGAGE">Mortgage</option>
                          <option value="OTHER">Other</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Employment Length (months)</Form.Label>
                        <Form.Control
                          type="number"
                          name="person_emp_length"
                          value={formData.person_emp_length}
                          onChange={(e) => handleChange(e)}
                          required
                          min="0"
                        />
                      </Form.Group>
                    </Col>
                  </Row>

                  <hr className="my-4" />

                  {/* Loan Request Details Section */}
                  <Card.Title className="mb-3">Loan Request Details</Card.Title>
                  <Row className="mb-3">
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Loan Intent</Form.Label>
                        <Form.Select
                          name="loan_intent"
                          value={formData.loan_intent}
                          onChange={handleChange}
                          required
                        >
                          <option value="PERSONAL">Personal</option>
                          <option value="EDUCATION">Education</option>
                          <option value="MEDICAL">Medical</option>
                          <option value="VENTURE">Venture</option>
                          <option value="HOMEIMPROVEMENT">Home Improvement</option>
                          <option value="DEBTCONSOLIDATION">Debt Consolidation</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Loan Amount ($)</Form.Label>
                        <Form.Control
                          type="number"
                          name="loan_amnt"
                          value={formData.loan_amnt}
                          onChange={(e) => handleChange(e)}
                          required
                          min="0"
                        />
                      </Form.Group>
                    </Col>
                  </Row>

                  <Row className="mb-3">
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Interest Rate (%)</Form.Label>
                        <Form.Control
                          type="number"
                          step="0.01"
                          name="loan_int_rate"
                          value={formData.loan_int_rate}
                          onChange={(e) => handleChange(e)}
                          min="0"
                        />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Loan Percent of Income (%)</Form.Label>
                        <Form.Control
                          type="number"
                          step="0.01"
                          name="loan_percent_income"
                          value={formData.loan_percent_income}
                          onChange={(e) => handleChange(e)}
                          min="0"
                          max="100"
                        />
                      </Form.Group>
                    </Col>
                  </Row>

                  <Row className="mb-3">
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Loan Grade</Form.Label>
                        <Form.Select
                          name="loan_grade"
                          value={formData.loan_grade}
                          onChange={handleChange}
                          required
                        >
                          <option value="A">A</option>
                          <option value="B">B</option>
                          <option value="C">C</option>
                          <option value="D">D</option>
                          <option value="E">E</option>
                          <option value="F">F</option>
                          <option value="G">G</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                  </Row>

                  <hr className="my-4" />

                  {/* Credit History Section */}
                  <Card.Title className="mb-3">Credit History</Card.Title>
                  <Row className="mb-3">
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Default on File</Form.Label>
                        <Form.Select
                          name="cb_person_default_on_file"
                          value={formData.cb_person_default_on_file}
                          onChange={handleChange}
                          required
                        >
                          <option value="N">No</option>
                          <option value="Y">Yes</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Credit History Length (years)</Form.Label>
                        <Form.Control
                          type="number"
                          name="cb_person_cred_hist_length"
                          value={formData.cb_person_cred_hist_length}
                          onChange={(e) => handleChange(e)}
                          required
                          min="0"
                        />
                      </Form.Group>
                    </Col>
                  </Row>

                  {/* Error Message */}
                  {error && (
                    <Alert
                      variant="danger"
                      dismissible
                      onClose={() => setError("")}
                      className="mb-3"
                    >
                      {error}
                    </Alert>
                  )}

                  {/* Submit Button */}
                  <div className="mt-4">
                    <Button
                      variant="primary"
                      size="lg"
                      type="submit"
                      disabled={loading}
                      className="w-100"
                    >
                      {loading ? "Processing..." : "Get Approval Decision"}
                    </Button>
                  </div>
                </Form>
              </Card.Body>
            </Card>
          </Col>

          {/* Results Section */}
          <Col lg={4}>
            {result && (
              <Card className="shadow-sm sticky-top" style={{ top: "20px" }}>
                <Card.Header
                  style={{
                    backgroundColor: result.approved === 1 ? "#28a745" : "#dc3545",
                    color: "white"
                  }}
                >
                  <h5 className="mb-0">{result.approved === 1 ? "✓ APPROVED" : "✗ DENIED"}</h5>
                </Card.Header>
                <Card.Body>
                  <div className="mb-3">
                    <p className="text-muted mb-1">Approval Rating</p>
                    <h2 className="mb-0">{((1 - result.default_probability) * 100).toFixed(1)}%</h2>
                  </div>

                  <hr />

                  <div className="mb-3">
                    <p className="text-muted mb-1">Default Risk Score</p>
                    <p className="mb-0">{(result.default_probability * 100).toFixed(2)}%</p>
                  </div>

                  <div className="mb-0">
                    <p className="text-muted mb-1">Approval Threshold</p>
                    <p className="mb-0">{(result.approval_threshold * 100).toFixed(2)}%</p>
                  </div>

                  {/* Progress Bar */}
                  <div className="mt-4">
                    <ProgressBar
                      now={(1 - result.default_probability) * 100}
                      variant={result.approved === 1 ? "success" : "danger"}
                      style={{ height: "30px" }}
                      label={`${((1 - result.default_probability) * 100).toFixed(0)}%`}
                    />
                    <small className="text-muted d-block mt-2">Approval Score</small>
                  </div>
                </Card.Body>
              </Card>
            )}
          </Col>
        </Row>
      </Container>
    </Container>
  );
}
