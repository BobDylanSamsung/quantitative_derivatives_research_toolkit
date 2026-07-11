# Quantitative Derivatives Research Toolkit

> A research-driven investigation into analytical and numerical methods for pricing financial derivatives.

---

# Executive Summary

The purpose of this project is to investigate the mathematical models used to determine the fair value of financial derivatives. Rather than building a simple options calculator, the project aims to develop a reusable Python library implementing multiple pricing algorithms while systematically evaluating their mathematical accuracy, computational efficiency and practical trade-offs.

The project is intentionally research-oriented. Each pricing method will be implemented from first principles before being validated against established analytical solutions. Controlled experiments will then compare competing numerical methods across accuracy, convergence rate, runtime performance and sensitivity to changing market conditions.

The resulting library will serve as both a learning resource for quantitative finance and a demonstration of software engineering, numerical computing and quantitative research skills.

---

# Motivation

My academic and professional experience has centred around mathematics, machine learning, software engineering and production data systems. However, I have limited formal exposure to quantitative finance.

This project bridges that gap.

Rather than attempting to build profitable trading strategies, the objective is to understand the mathematical foundations that underpin modern quantitative trading firms such as Optiver, Jane Street, IMC and SIG.

By implementing the underlying pricing models from scratch and analysing their behaviour, I aim to develop a deeper understanding of:

- Probability
- Stochastic processes
- Numerical methods
- Scientific computing
- Quantitative modelling
- Financial derivatives

The emphasis throughout the project is on learning, experimentation and mathematical reasoning rather than financial speculation.

---

# Project Objectives

The project has four primary objectives.

## 1. Mathematical Understanding

Develop a rigorous understanding of the mathematical principles underlying derivative pricing.

Topics include:

- Risk-neutral pricing
- Brownian motion
- Geometric Brownian Motion
- Stochastic differential equations
- Arbitrage-free pricing
- Numerical approximation

---

## 2. Software Engineering

Develop a reusable, well-tested Python library implementing multiple pricing algorithms.

The library should demonstrate:

- Clean architecture
- Modularity
- Testing
- Documentation
- Performance awareness
- Extensibility

---

## 3. Quantitative Research

Design controlled experiments comparing competing pricing methodologies.

The project should answer questions such as:

- Which algorithms converge fastest?
- Which algorithms are computationally efficient?
- How does numerical error change with increasing resolution?
- How sensitive are pricing models to volatility?
- Under what circumstances should one model be preferred over another?

---

## 4. Scientific Communication

Produce clear documentation explaining:

- Mathematical assumptions
- Implementation details
- Experimental methodology
- Results
- Conclusions

---

# Background

Financial derivatives derive their value from another financial asset.

One of the most common derivatives is an **option**, which provides the holder with the right—but not the obligation—to buy or sell an underlying asset at a predetermined price before or at a specified date.

Determining the fair value of an option is one of the foundational problems in quantitative finance.

Several mathematical approaches exist.

### Analytical

Closed-form equations.

Example:

- Black-Scholes

---

### Numerical

Discrete approximations.

Examples:

- Binomial Tree
- Finite Difference Methods

---

### Stochastic

Simulation-based methods.

Examples:

- Monte Carlo Simulation

Each method introduces different assumptions, computational costs and implementation challenges.

This project compares these approaches.

---

# Scope

## Included

European Call Options

European Put Options

Black-Scholes pricing

Binomial Tree pricing

Monte Carlo pricing

Greeks

Implied volatility

Benchmarking

Statistical analysis

Visualisation

Technical documentation

---

## Excluded

Live trading

Trading strategies

Algorithmic execution

Market prediction

Portfolio optimisation

Deep learning

Alternative asset classes

High-frequency trading infrastructure

Exotic derivatives (initially)

American options (initially)

---

# Research Questions

This project seeks to answer the following questions.

## Accuracy

How closely do numerical methods approximate analytical pricing models?

---

## Convergence

How quickly do numerical algorithms converge towards the theoretical solution?

---

## Performance

How does runtime scale as computational complexity increases?

---

## Stability

How sensitive are pricing algorithms to changes in:

- Volatility
- Interest rate
- Time to expiry
- Strike price

---

## Engineering

Which implementation techniques produce the cleanest, fastest and most reusable software?

---

# Project Deliverables

## Python Library

A modular pricing library implementing multiple pricing algorithms.

---

## Research Report

A technical report documenting:

- Background
- Mathematical derivations
- Experimental methodology
- Results
- Discussion

---

## Experimental Notebooks

Reproducible Jupyter notebooks containing:

- Benchmarks
- Plots
- Statistical analysis

---

## Documentation

Comprehensive documentation including:

- Installation
- API
- Examples
- Mathematical notes

---

# Repository Structure

```
quantitative-derivatives-research/

│
├── pricing/
│   ├── black_scholes.py
│   ├── binomial_tree.py
│   └── monte_carlo.py
│
├── greeks/
│   ├── delta.py
│   ├── gamma.py
│   ├── theta.py
│   ├── vega.py
│   └── rho.py
│
├── volatility/
│   └── implied_volatility.py
│
├── experiments/
│   ├── convergence.ipynb
│   ├── runtime.ipynb
│   ├── sensitivity.ipynb
│   └── benchmarking.ipynb
│
├── tests/
│
├── docs/
│
├── report/
│
└── README.md
```

---

# Success Criteria

The project will be considered successful if it:

- Correctly implements multiple pricing algorithms.
- Produces reproducible experimental results.
- Demonstrates rigorous software engineering practices.
- Clearly explains the underlying mathematics.
- Provides quantitative comparisons between competing methods.
- Serves as a portfolio-quality research project.

---

# Future Extensions

Possible future work includes:

- American Options
- Barrier Options
- Asian Options
- Finite Difference Methods
- Longstaff-Schwartz
- Variance Reduction
- GPU Monte Carlo
- Parallel Simulation
- Heston Model
- SABR Model

---

# Guiding Principles

Throughout this project, every design decision should align with the following principles.

## Learn before implementing

The objective is not simply to write code.

Every implementation should be preceded by understanding the mathematics that motivates it.

---

## Prefer understanding over optimisation

A clear implementation is preferable to an overly optimised one until correctness has been established.

---

## Validate everything

Every implementation should be compared against known analytical solutions or published reference values.

---

## Measure rather than assume

Performance claims should be supported through controlled benchmarking and reproducible experiments.

---

## Build research software

This repository should resemble the output of a quantitative researcher rather than a software engineer.

Code exists to support experimentation, analysis and reproducibility.

---

# Intended Audience

This repository is written for:

- Quantitative trading recruiters
- Quantitative researchers
- Software engineers
- Students learning quantitative finance
- Future collaborators
- Future versions of ChatGPT assisting with the project

The documentation assumes a strong mathematical and programming background but does not assume prior knowledge of quantitative finance.

---

# Long-Term Vision

The ultimate goal is to build a portfolio-quality quantitative research project that demonstrates:

- Mathematical maturity
- Scientific thinking
- Numerical computing
- Software engineering
- Performance analysis
- Technical communication

By the completion of the project, I should not simply know **how** to price an option—I should understand **why** different pricing methods exist, **when** each should be used and **what** mathematical assumptions underpin them.