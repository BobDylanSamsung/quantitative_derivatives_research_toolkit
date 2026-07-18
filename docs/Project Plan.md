# Project Plan
## Numerical Methods for Derivative Pricing

> **Project Type:** Quantitative Research Portfolio Project  
> **Status:** Planning  
> **Duration:** 6–8 Weeks (Part-Time)  
> **Estimated Effort:** 60–90 Hours  
> **Primary Language:** Python  
> **Methodology:** Agile (1-week sprints)

---

# Overview

This document describes the execution plan for the **Numerical Methods for Derivative Pricing** project.

Unlike a traditional software project, this project combines:

- Mathematical learning
- Scientific research
- Software engineering
- Performance analysis
- Technical communication

The objective is to produce a portfolio-quality quantitative research project that demonstrates the workflow of a quantitative researcher.

Each sprint is designed to deliver a mathematically complete milestone rather than simply more code.

---

# Success Criteria

By project completion I should be able to:

- Explain the mathematics behind derivative pricing.
- Implement multiple pricing algorithms from first principles.
- Compare competing numerical methods experimentally.
- Evaluate computational performance and convergence.
- Produce research-quality documentation.
- Confidently discuss every implementation and design decision during interviews.

---

# Project Timeline

| Sprint | Theme |
|---------|---------|
| Sprint 1 | Foundations & Black-Scholes |
| Sprint 2 | Binomial Trees |
| Sprint 3 | Monte Carlo Simulation |
| Sprint 4 | Experimental Research |
| Sprint 5 | Library Engineering |

---

# Sprint 1 — Financial Foundations & Black-Scholes

## Goal

Develop sufficient financial and mathematical understanding to correctly implement the Black-Scholes analytical pricing model.

## Deliverables

- Financial derivatives study notes
- Repository scaffold
- Black-Scholes implementation
- Greeks implementation
- Unit tests
- Documentation

---

### Tickets

## QR-1 Research Financial Derivatives

### Description

Develop foundational knowledge of options and derivative pricing.

Topics

- Calls vs Puts
- European vs American Options
- Arbitrage
- Risk-neutral pricing
- Volatility
- Greeks

Estimated Time

**4 hours**

---

## QR-2 Create Repository Architecture

### Description

Initialise the repository and establish the software architecture.

Deliverables

- Python project
- Ruff
- Pytest
- Mypy
- CI
- Documentation structure

Estimated Time

**2 hours**

---

## QR-3 Implement Black-Scholes

### Description

Implement analytical pricing for European call and put options.

Deliverables

- Pricing functions
- Unit tests
- Validation against reference values

Estimated Time

**5 hours**

---

## QR-4 Implement Greeks

### Description

Calculate

- Delta
- Gamma
- Vega
- Theta
- Rho

Estimated Time

**3 hours**

---

## QR-5 Documentation

### Description

Document:

- Assumptions
- Mathematical derivation
- API usage

Estimated Time

**2 hours**

---

# Sprint 2 — Binomial Tree Pricing

## Goal

Implement the first numerical pricing method and compare it with the analytical solution.

## Deliverables

- Binomial Tree implementation
- Convergence study
- Runtime benchmarks

---

### Tickets

## QR-6 Implement Cox-Ross-Rubinstein Tree

Estimated Time

**6 hours**

---

## QR-7 Convergence Investigation

Research Questions

- How quickly does the tree converge?
- How many steps are required?
- Does convergence differ between calls and puts?

Deliverables

Plots

- Error
- Convergence

Estimated Time

**3 hours**

---

## QR-8 Runtime Benchmarking

Compare runtime across varying tree depths.

Deliverables

Benchmark report

Estimated Time

**2 hours**

---

# Sprint 3 — Monte Carlo Pricing

## Goal

Implement stochastic simulation for option pricing.

## Deliverables

- Monte Carlo pricer
- Statistical validation
- Performance comparison

---

### Tickets

## QR-9 Monte Carlo Pricing Engine

Estimated Time

**6 hours**

---

## QR-10 Variance Investigation

Research Questions

- How many simulations are required?
- How does variance decrease?

Deliverables

- Confidence intervals
- Convergence plots

Estimated Time

**3 hours**

---

## QR-11 Compare Pricing Methods

Compare

- Black-Scholes
- Binomial
- Monte Carlo

Estimated Time

**2 hours**

---

# Sprint 4 — Quantitative Research

## Goal

Apply the pricing toolkit to real market data by recovering implied volatilities, constructing a volatility smile or surface, and investigating deviations from the constant-volatility Black–Scholes model.
---

## Deliverables

- Real option-chain data ingestion
- Robust implied-volatility solver
- Volatility smile plots
- Optional volatility surface
- Liquidity and no-arbitrage filtering
- Short market-calibration report

---

# Sprint 5 — Software Engineering

## Goal

Transform research code into a reusable Python library.

---

### Tickets

## QR-17 Refactor Library

Estimated Time

**3 hours**

---

## QR-18 Improve Testing

Target

>90% coverage

Estimated Time

**2 hours**

---

## QR-19 Performance Optimisation

Profile

Optimise

Document

Estimated Time

**2 hours**

---

## QR-20 Package Library

Prepare

- Installation
- Distribution
- Versioning

Estimated Time

**2 hours**

---

# Sprint 6 — Documentation & Publication

## Goal

Publish a polished portfolio-quality project.

---

### Tickets

## QR-21 Technical Report

Sections

- Background
- Mathematics
- Methodology
- Results
- Discussion

Estimated Time

**4 hours**

---

## QR-22 Documentation

Improve

- README
- Examples
- API

Estimated Time

**2 hours**

---

## QR-23 Repository Polish

Complete

- Diagrams
- Badges
- Examples
- Screenshots

Estimated Time

**1 hour**

---

## QR-24 Resume Integration

Produce

- Resume bullet
- LinkedIn summary
- GitHub description

Estimated Time

**1 hour**

---

# Stretch Goals

These tasks should only begin once all primary objectives have been completed.

| Ticket | Feature | Estimated Hours |
|---------|---------|----------------:|
| QR-25 | American Options | 6 |
| QR-26 | Variance Reduction Techniques | 4 |
| QR-27 | Implied Volatility Solver | 4 |
| QR-28 | Heston Model | 10 |
| QR-29 | GPU Monte Carlo | 8 |
| QR-30 | Parallel Simulation | 6 |

---

# Definition of Done

A ticket is only considered complete when all of the following conditions are satisfied.

## Mathematical

- Mathematical concepts understood.
- Assumptions documented.
- Results validated.

---

## Engineering

- Implementation complete.
- Ruff passes.
- Mypy passes.
- Unit tests pass.

---

## Research

- Experimental results reproduced.
- Findings documented.
- Figures generated.

---

## Documentation

- README updated.
- Code documented.
- Notebook completed.

---

# Risks

| Risk | Mitigation |
|------|------------|
| Lack of finance knowledge | Prioritise conceptual understanding before implementation. |
| Overly complex mathematics | Begin with European options and analytical pricing before progressing to numerical methods. |
| Scope creep | Restrict scope to European vanilla options for the initial release. |
| Premature optimisation | Focus on correctness before performance improvements. |

---

# Expected Outcomes

By the completion of this project I should have:

- A production-quality Python library
- A quantitative finance research portfolio project
- A strong understanding of derivative pricing
- Practical experience implementing numerical algorithms
- A portfolio piece suitable for quantitative research interviews
- The ability to confidently discuss both the mathematics and engineering behind modern option pricing techniques

---

# Guiding Philosophy

This project is **not** about building another software application.

It is about thinking like a quantitative researcher.

Every implementation should begin with understanding the underlying mathematics, continue through careful engineering, and conclude with rigorous experimentation and evidence-based analysis.

The final repository should demonstrate not only the ability to write code, but also the ability to formulate hypotheses, design experiments, evaluate competing methods, and communicate technical findings clearly.