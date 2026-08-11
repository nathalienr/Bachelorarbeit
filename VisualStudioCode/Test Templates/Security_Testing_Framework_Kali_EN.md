# ifm Security Testing Framework (Kali Linux)

## Purpose

A Kali Linux toolset for verifying countermeasures CM-001 to CM-010.

## 1. Purpose and Context

This document adds ready-to-run test instructions for each countermeasure (CM) to the "ifm Cybersecurity Test Process".

Process:

SUC → Threat / Vulnerability / Risk → Risk Mitigation → Countermeasure → Security Test Module (STM) → Review

Every countermeasure labeled "security-func" requires a technical check through its Security Test Module (STM) at the required Security Test Grade (STG).

## 2. Test Environment and Safety Rules

- Run tests only in approved test environments.
- Use Kali Linux (current rolling release).
- Obtain written approval before each test.
- Monitor actively intrusive tools.
- Store tool output as evidence.

## 3. Tool Assignment Overview

| CM | Title | Tool |
|----|--------|------|
| CM-001 | Network Exposure vs. Architecture | Nmap |
| CM-002 | Network Segmentation | Nmap |
| CM-003 | Default / Weak Credentials | Hydra |
| CM-004 | RBAC / Privilege Escalation | OWASP ZAP |
| CM-005 | TLS Configuration | SSLscan |
| CM-006 | Hardening Validation | Lynis |
| CM-007 | Debug / Service Interface Exposure | Nikto |
| CM-008 | Patch Level / Known CVEs | OpenVAS |
| CM-009 | Load Behavior & Logging | Siege |
| CM-010 | Fuzzing / Robustness | boofuzz |

## 4. Test Instructions

### CM-001 – Network Exposure vs. Architecture

**Tool:** Nmap

**Goal:** Verify accessible services match approved architecture.

```bash
sudo nmap -sS -sV -p- -T3 -oA cm001_<target> <Target-IP>
sudo nmap -sU --top-ports 200 -oA cm001_<target>_udp <Target-IP>