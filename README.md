
# QA Automation Framework | Python & Playwright

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Playwright](https://img.shields.io/badge/Playwright-UI%20Testing-green)
![Pytest](https://img.shields.io/badge/Pytest-Test%20Framework-blue)
![REST API](https://img.shields.io/badge/REST%20API-Testing-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Docker](https://img.shields.io/badge/Docker-Environment-blue)
![Allure](https://img.shields.io/badge/Allure-Reporting-purple)
![Tests](https://img.shields.io/badge/Latest%20Run-41%2F41%20Passed-brightgreen)

## Project Overview

A Python-based QA Automation Framework designed to demonstrate practical software testing and test automation skills across API, UI, and database layers.

The project combines automated testing of two independent applications:

- **Banking REST API** — authentication, user management, financial transactions, credit operations, and database validation.
- **SauceDemo Web Application** — authentication, product catalog, shopping cart, and checkout workflows.

The framework was developed as part of practical QA Automation training and subsequently refined for portfolio presentation, maintainability, configuration security, and test failure diagnostics.

## Project Objectives

- Build a structured and maintainable test automation framework.
- Validate critical business workflows.
- Implement positive and negative test scenarios.
- Verify REST API responses and HTTP status codes.
- Validate backend data using PostgreSQL.
- Apply the Page Object Model design pattern.
- Ensure test isolation through Pytest fixtures.
- Generate detailed test execution reports.
- Investigate intermittent failures using Playwright Trace Viewer.
- Separate sensitive configuration from source code.

## Latest Test Execution Results

| Test Suite | Total | Passed | Failed |
|------------|------:|-------:|-------:|
| API Tests | 22 | 22 | 0 |
| UI Tests | 19 | 19 | 0 |
| **Total** | **41** | **41** | **0** |

- **Latest execution pass rate:** 100%
- **Execution time:** 105.01 seconds
- **Execution date:** November 25, 2026
- **Execution environment:** Windows, local Docker environment, Chromium

These results represent the latest successful full regression execution.

### Allure Report — Overview

![Allure Overview](docs/allure-overview.png)

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Primary programming language |
| Pytest | Test execution and fixture management |
| Playwright | Browser automation and UI testing |
| Requests | REST API testing |
| Pydantic | API request and response models |
| SQLAlchemy | Database connectivity |
| PostgreSQL | Backend data validation |
| Psycopg2 | PostgreSQL database driver |
| Docker | Local banking test environment |
| Allure Report | Test reporting and visualization |
| Playwright Trace Viewer | UI test failure investigation |
| Git | Version control |

## Framework Architecture

The framework follows a layered architecture that separates test scenarios, business actions, technical implementation, and test configuration.

### UI Testing Architecture

```text
Test Cases
    |
    v
Steps Layer
    |
    v
Page Object Model
    |
    v
Playwright
    |
    v
Web Application
```

### API Testing Architecture

```text
Test Cases
    |
    v
Steps / Request Layer
    |
    v
Request Specifications & Data Models
    |
    v
REST API
    |
    v
Database Validation (where applicable)
```

### Architectural Principles

- Separation of concerns
- Reusable test components
- Centralized configuration
- Independent browser contexts
- Structured API request and response models
- Reusable business-level test steps
- Maintainable UI locators
- Explicit assertions
- Detailed execution reporting

## Project Structure

```text
Test-Bank-Junior/
|
|-- docs/
|   |-- allure-overview.png
|   |-- allure-suites.png
|   |-- allure-test-details.png
|
|-- resources/
|   |-- urls.properties.example
|
|-- src/
|   |-- main/
|       |-- api/
|       |   |-- classes/
|       |   |-- configs/
|       |   |-- db/
|       |   |-- fixtures/
|       |   |-- foundation/
|       |   |-- models/
|       |   |-- requests/
|       |   |-- specs/
|       |   |-- steps/
|       |   |-- tests/
|       |
|       |-- ui/
|           |-- fixtures/
|           |-- pages/
|           |-- steps/
|           |-- tests/
|
|-- .gitignore
|-- conftest.py
|-- pytest.ini
|-- requirements.txt
|-- README.md
```

## Test Coverage

### API Testing — 22 Test Cases

The API test suite focuses on critical banking operations, authorization, input validation, and business rules.

| Feature | Test Cases |
|---------|-----------:|
| Administrator Authentication | 5 |
| User Authentication | 2 |
| User Creation | 4 |
| Bank Account Creation | 2 |
| Account Deposit | 3 |
| Money Transfer | 2 |
| Credit Request | 2 |
| Credit Repayment | 2 |
| **Total** | **22** |

### API Validation Areas

- Successful and unsuccessful authentication
- Invalid credentials
- Empty required fields
- JWT-based authorization
- Unauthorized requests
- Role-based access restrictions
- User creation validation
- Bank account creation
- Financial transactions
- Credit business rules
- HTTP status code validation
- Response data validation
- Database verification where applicable

### UI Testing — 19 Test Cases

The UI test suite covers key user journeys in the SauceDemo e-commerce application.

| Feature | Test Cases |
|---------|-----------:|
| Authentication | 4 |
| Shopping Cart | 4 |
| Product Catalog | 9 |
| Checkout | 2 |
| **Total** | **19** |

### UI Validation Areas

- Successful login
- Logout functionality
- Locked-out user validation
- Product catalog verification
- Product quantity validation
- Product sorting by name
- Product sorting by price
- Product details verification
- Adding products to the shopping cart
- Removing products from the shopping cart
- Cart quantity verification
- Checkout workflow
- Required checkout field validation

### Allure Report — Test Suites

![Allure Test Suites](docs/allure-suites.png)

## Test Design Techniques

The test suite includes practical applications of the following testing approaches:

- Functional testing
- Positive testing
- Negative testing
- Integration testing
- Regression testing
- End-to-end UI testing
- API response validation
- Authorization testing
- Business rule validation
- Data consistency verification

## Installation and Setup

### Prerequisites

- Python 3.14 (version used for the latest successful execution)
- Git
- Docker for the banking API environment
- PostgreSQL access for database-related tests
- Allure Commandline for interactive reporting
- Java runtime compatible with Allure Commandline

### 1. Create a Virtual Environment

From the project root:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Install Playwright Chromium

```bash
python -m playwright install chromium
```

### 4. Configure the Test Environment

Create a local configuration file using the provided template.

Windows PowerShell:

```powershell
Copy-Item resources/urls.properties.example resources/urls.properties
```

Linux or macOS:

```bash
cp resources/urls.properties.example resources/urls.properties
```

Update the configuration with your local environment values.

```properties
backendUrl=http://localhost:4111/api
dataBaseUrl=postgresql+psycopg2://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/YOUR_DATABASE
adminUsername=YOUR_ADMIN_USERNAME
adminPassword=YOUR_ADMIN_PASSWORD
```

The actual configuration file is excluded from version control.

### 5. Start the Banking Environment

The API tests require a running banking backend and PostgreSQL database.

The banking application is an external training environment and is not distributed as part of this automation framework.

Before executing API tests, ensure that:

- The banking backend is running.
- PostgreSQL is available.
- The configured API endpoint is accessible.
- Database credentials are valid.
- Administrator credentials are configured.

The UI tests target the publicly available SauceDemo application:

https://www.saucedemo.com/

## Running Tests

Execute the commands from the project root.

### Run All Tests

```bash
python -m pytest -v
```

### Run API Tests Only

```bash
python -m pytest src/main/api/tests -v
```

### Run UI Tests Only

```bash
python -m pytest src/main/ui/tests -v
```

### Run Authentication Tests

```bash
python -m pytest src/main/ui/tests/test_auth.py -v
```

### Run a Specific Test

```bash
python -m pytest src/main/ui/tests/test_auth.py::TestAuth::test_auth_logout_standard_user -v
```

## Allure Reporting

Allure Report provides structured and interactive test execution results.

Reporting includes:

- Test execution status
- Test suite statistics
- Execution duration
- Detailed test steps
- Assertion results
- Failure information
- Test execution timeline

### Generate Allure Results

```bash
python -m pytest -v --alluredir=allure-results --clean-alluredir
```

### Open the Interactive Report

```bash
allure serve allure-results
```

### Generate a Static Report

```bash
allure generate allure-results -o allure-report --clean
```

### Open the Generated Report

```bash
allure open allure-report
```

### Allure Report — Detailed Test Execution

![Allure Test Details](docs/allure-test-details.png)

## Playwright Trace Viewer

Playwright tracing is integrated into the browser page fixture to support UI test investigation.

Trace files capture:

- Browser actions
- DOM snapshots
- Screenshots
- Action execution details
- Network activity
- Source information

Each UI test generates a trace archive in the local `traces/` directory.

### Open a Trace File

```bash
python -m playwright show-trace traces/test_auth_logout_standard_user.zip
```

Trace files are excluded from version control because they may contain browser session information and application data.

## Troubleshooting and Failure Investigation

During framework refinement, several test execution issues were identified and investigated.

### AUTO-001 — Intermittent Logout Failure

**Observed behavior**

The Logout element was present in the DOM but intermittently remained invisible after opening the sidebar menu.

**Investigation**

- Analyzed Playwright timeout logs.
- Inspected the element using browser Developer Tools.
- Reviewed accessible roles and DOM attributes.
- Replaced the role-based locator with a unique element ID.
- Added an explicit visibility check.
- Reviewed browser context isolation.
- Integrated Playwright tracing for further investigation.

**Current status**

The latest full regression execution completed successfully.

However, the underlying cause of the intermittent menu visibility issue has not been conclusively established.

The issue remains documented as a known test reliability risk.

### ENV-001 — Database Connection Failure

**Observed behavior**

API tests failed when the local PostgreSQL database was unavailable.

**Investigation**

- Reviewed database connection exceptions.
- Identified connection refusal on the configured PostgreSQL port.
- Started the local Docker environment.
- Re-executed the API test suite.

**Result**

All 22 API tests passed after the environment became available.

This investigation demonstrated the importance of distinguishing environment failures from application defects.

### API-001 — Intermittent JWT Authorization Failure

**Observed behavior**

A credit repayment scenario failed during test setup because a credit creation request returned HTTP 401 instead of the expected HTTP 201.

**Investigation**

- Reviewed the API response and assertion failure.
- Identified an invalid JWT token response.
- Re-executed the affected test independently.
- Re-executed the full regression suite.

**Current status**

The isolated test and subsequent full regression execution passed without code changes.

The underlying cause remains unconfirmed and is documented as a known intermittent issue.

## Test Isolation and Fixture Management

Pytest fixtures are used to manage test resources and execution lifecycle.

The UI framework uses:

- Session-scoped Playwright initialization.
- Session-scoped browser initialization.
- Function-scoped browser contexts.
- Independent browser pages for individual tests.
- Browser context cleanup after execution.
- Reusable authentication fixtures.
- Automated trace collection.

This approach reduces cross-test dependencies and supports independent UI test execution.

## Security and Configuration Management

The project separates environment-specific configuration from source code.

Security-related practices include:

- Externalized administrator credentials.
- Externalized database connection settings.
- Configuration templates without real credentials.
- Dynamic JWT token retrieval.
- Exclusion of local configuration files from Git.
- Exclusion of virtual environments and cache files.
- Exclusion of generated Allure results.
- Exclusion of Playwright trace archives.

Public SauceDemo test credentials are used only for the demonstration web application.

Only reviewed reporting screenshots are intended for publication.

## Quality Engineering Approach

This project demonstrates an approach to automation that goes beyond test execution.

The focus includes:

- Understanding business workflows.
- Identifying critical validation points.
- Designing meaningful assertions.
- Covering positive and negative scenarios.
- Investigating failures using technical evidence.
- Distinguishing environment issues from application defects.
- Improving test maintainability.
- Documenting known risks and limitations.
- Communicating test results through structured reports.

## Future Improvements

Potential framework enhancements include:

- GitHub Actions CI/CD integration.
- Automated environment readiness checks.
- Configurable headless browser execution.
- Cross-browser testing.
- Parallel test execution.
- Expanded API boundary value coverage.
- Automated screenshot attachments on failure.
- Trace collection for failed tests only.
- Improved test data management.
- Additional investigation of intermittent failures.
- Automated test execution history and trend reporting.

## Project Limitations

- API tests depend on an external banking training environment.
- UI tests depend on the availability and behavior of SauceDemo.
- The latest successful execution does not guarantee that all intermittent failures have been eliminated.
- Cross-browser execution has not yet been validated.
- CI/CD integration is planned but not currently implemented.
- Installation in a completely clean environment has not yet been independently verified.

## About the Author

**Valeria Spektor**

QA Engineer | ISTQB Certified Tester | API Testing | UI Automation | AI/LLM Testing

Professional interests:

- Software Quality Engineering
- Test Automation
- Risk-Based Testing
- API and Integration Testing
- Database Validation
- AI and LLM Testing
- Test Failure Investigation
- Continuous Quality Improvement

## Acknowledgments

This project originated from practical Python and Playwright QA Automation training and was further refined for professional portfolio presentation.

SauceDemo is used as a public demonstration application for UI automation practice.

---

**Quality is not just about passing tests. It is about understanding what we test, why we test it, and what the results actually mean.**
