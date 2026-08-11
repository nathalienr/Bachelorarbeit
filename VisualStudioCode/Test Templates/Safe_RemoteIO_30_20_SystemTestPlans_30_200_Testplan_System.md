# Type and System Test Plan

## Project

153829 Remote_IO_Safe_DIDO_PROFIsafe

## Products

- AL400S
- AL401S

## Status

In Review

## Author

Dragana Topalovic

---

## 2. Scope

This document describes planning activities for product-level and system-level testing.

### 2.1 Applicable Documents

| Ref | Document |
|------|------|
| [1] | General test strategy |
| [2] | Product requirements |
| [3] | System requirements |
| [4] | Verification & Validation Plan |
| [5] | FSM Plan |
| [6] | PROFIsafe Guideline |
| [7] | Environmental Test Specification |
| [8] | EMC Product Test |

---

## 2.3 Test Mission

- [x] New Device
- [x] Safety Device
- [x] Development from Scratch
- [x] Safety Related Functions

### Quality Targets

- [x] Robustness
- [x] Function
- [x] Documentation
- [x] IOP

### Safety Targets

Verification target:

- SIL 3 according to IEC 62061
- SIL 3 according to IEC 61508
- Performance Level e (Category 4)
- ISO 13849 Validation
- IEC 61131-2 EMC compliance

---

## 2.4 Test Object

Products:

- AL400S PROFIsafe 6x2 F-DI 2x2 F-DO IP67
- AL401S PROFIsafe 6x2 F-DI 2x2 F-DO IP69K

### Components

| Component | HW | SW | Documentation |
|------------|----|----|----|
| HW Version 1.4.0.2 | x | | |
| Update Container | | x | |
| µC3 Bootloader | | x | |
| SCPU Bootloader | | x | |
| EEPROM Images | | | x |

---

## 3. Creation, Rework and Review of Test Cases

### Rules

- Use template test case.
- Store TIA projects in SVN.
- Automation scripts must be version controlled.
- Device granular passivation uses tag:

#DeviceGranularPassivation

...