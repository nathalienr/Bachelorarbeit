1\. Introduction

&#x09;Background and Motivation

&#x09;	Digitalisierung von Industrieanlagen

&#x09;	IT/OT-Konvergenz

&#x09;	Industrielle Gateways als kritische Schnittstellen

&#x09;	Wandel von Safety zu Security

&#x09;	Neue Anforderungen durch die Machinery Regulation 2023/1230

&#x09;Problem Statement

&#x09;	Klassische funktionale Tests fokussieren Kommunikation, Performance und Zuverlässigkeit

&#x09;	Fehlende systematische Verifikation von Security-Funktionen

&#x09;	Gap zwischen regulatorischen Anforderungen und bestehender Testpraxis

&#x09;Objectives and Scope

&#x09;	Entwicklung einer Security-Testmethodik

&#x09;	Nachweis der Wirksamkeit technischer Gegenmaßnahmen

&#x09;	Integration in bestehende Testprozesse



&#x09;	Beispielsweise:



&#x09;	RQ1: Welche regulatorischen und normativen Anforderungen müssen durch funktionale Security-Tests 		für industrielle Gateways berücksichtigt werden?



&#x09;	RQ2: Wie können Security-Anforderungen aus Bedrohungen und Risiken systematisch in Testfälle 			überführt werden?



&#x09;	RQ3: Wie wirksam ist die entwickelte Testmethodik bei der Verifikation bestehender Security-			Maßnahmen?



&#x09;	Fokus auf industrielle Gateways (physische/digitale Schnittstellen)

&#x09;	Fokus auf funktionales Security Testing

&#x09;	Keine vollständige Produktzertifizierung

&#x09;	Keine tiefgehenden Penetration-Tests

&#x09;Structure of the Thesis

&#x09;	Kurze Beschreibung der Kapitel.



2\. Fundamentals

&#x09;2.1 Industrial Gateways in IT/OT Environments

&#x09;	2.1.1 Role as Critical Interface Component

&#x09;		Definition of Industrial Gateways

&#x09;		Gateway Functions

&#x09;		Protocol Translation

&#x09;		Data Aggregation

&#x09;		Remote Access

&#x09;		Gateway as Security Enforcement Point

&#x09;		Gateway as Trust Boundary

&#x09;	2.1.2 IT/OT Interfaces

&#x09;		Characteristics of IT Systems

&#x09;		Characteristics of OT Systems

&#x09;		IT/OT Convergence

&#x09;		Security Requirements at IT/OT Boundaries

&#x09;		Different Security Priorities in IT and OT	

&#x09;	2.1.3 Attack Surface of Industrial Gateways

&#x09;		Assets within Industrial Gateways

&#x09;		Communication Interfaces

&#x09;		User Interfaces

&#x09;		Maintenance Interfaces

&#x09;		Firmware and Update Mechanisms

&#x09;		Security Relevant Assets

&#x09;		Typical Attack Vectors



&#x09;~~2.2 Regulatory and Standardization Framework~~

&#x09;	~~2.2.1 EU Machinery Regulation (EU) 2023/1230~~

&#x09;		~~Cybersecurity Requirements~~

&#x09;		~~Essential Health and Safety Requirements~~

&#x09;		~~Annex III~~

&#x09;		~~Protection against Corruption~~

&#x09;		~~Secure Communication~~

&#x09;		~~Traceability~~

&#x09;	~~2.2.2 prEN 50742~~

&#x09;		~~Relationship to Machinery Regulation~~

&#x09;		~~Guidance for Cybersecurity Verification~~

&#x09;	~~2.2.3 IEC 62443 Series~~

&#x20;			~~Overview of the Standard Series~~

&#x09;			~~- IEC 62443- 4-1 Risk Assessment Concepts~~

&#x09;			~~- IEC 62443-3-3 Foundational Requirements~~

&#x09;			~~- IEC 62443-4-2 Technical Security Requirements~~



&#x09;2.3 Cybersecurity Fundamentals

&#x09;	2.3.1 Security Goals

&#x09;		Confidentiality

&#x09;		Integrity

&#x09;		Availability

&#x09;		Authenticity

&#x09;		Accountability

&#x09;	2.3.2 Threats, Vulnerabilities and Attack Vectors

&#x09;		Threat Sources

&#x09;		Vulnerability Concepts

&#x09;		Exploitation Pathways

&#x09;	2.3.3 Security Controls and Mitigation Measures

&#x09;		Authentication

&#x09;		Authorization

&#x09;		Secure Configuration

&#x09;		Secure Communication

&#x09;		Logging

&#x09;		Firmware Integrity Protection



&#x09;2.4 Risk-Based Security Engineering

&#x09;	2.4.1 Threat Analysis and Risk Assessment (TARA)

&#x09;		Asset-Centric Analysis

&#x09;		Threat Identification

&#x09;		Risk Determination

&#x09;	2.4.2 STRIDE Methodology

&#x09;		Threat Categories (Spoofing, Tampering, Repudiation, Information disclosure, Denial of Service, Elevation of privilege)

&#x09;			--> Associated with security control (Authentication, Integrity, Non-repudiation, Confidentiality, Availability, Authorization)

&#x09;	2.4.3 Risk Evaluation 

&#x09;		Impact

&#x09;		Likelihood

&#x09;		Risk Matrix

&#x09;		Mitigation Strategies

&#x09;	2.4.4 Risk Treatment Strategies

&#x09;		Avoid

&#x09;		Mitigate

&#x09;		Transfer

&#x09;		Accept

&#x09;2.5 Security Testing Approaches

&#x09;	2.5.1 Threat Mitigation Testing

&#x09;	2.5.2 Vulnerability Testing --> begründen, warum klassische Vulnerability-Tests und funktionale Security-Tests unterschiedliche Ziele verfolgen 

&#x09;											(Vulnerability Databases, Fuzzing, Vulnerability Scanning))

&#x09;	2.5.3 Penetration Testing

&#x09;		Attacker Perspective

&#x09;		Goal-Oriented Testing

&#x09;	2.5.4 Functional Security Testing

&#x09;		Verification of Security Functions

&#x09;		Requirement-based Security Testing

&#x09;		Testing of Mitigation Measures





3\. Methodology



(Herleitung Anforderungen: IEC 62443-3-2)

&#x09;3.1 Research Approach

&#x09;	Design Science Research

&#x09;	Methodology Development

&#x09;	Validation Strategy

&#x09;3.2 Analysis of the Gateway Security Context

&#x09;	 Asset Identification

&#x09;	 Interface Analysis

&#x09;		Netzwerkinterfaces

&#x09;		Konfigurationsschnittstellen

&#x09;		Update-Schnittstellen

&#x09;		Diagnosezugänge

&#x09;	 Threat Identification

&#x09;	 Risk Assessment

&#x09;3.3 Derivation of Security Requirements

&#x09;	Ableitung aus:

&#x09;		Machinery Regulation

&#x09;		IEC 62443

&#x09;		TARA

&#x09;3.4 Development of the Functional Security Testing Methodology

&#x09;	3.4.1 Testing Framework Concept

&#x09;		Test Matrix Structure: 

&#x09;			Requirement --> Threat -->  Risk --> Countermeasure --> Test Category --> Test Case --> Evidence

&#x09;	3.4.2 Security Test Categories

&#x09;		Interface Exposure

&#x09;		Authentication

&#x09;		Authorization --> Firewall, Whitelisting, Zone Separation

&#x09;		Communication Security

&#x09;		Configuration Protection

&#x09;		Firmware and Update Security

&#x09;		Logging and Traceability

&#x09;		Robustness / Negative Testing

&#x09;		Principles: Completeness, and Abstraction

&#x09;	3.4.3 Test Case Structure

&#x09;		Beispielsweise:

&#x09;			Requirement

&#x09;			Threat

&#x09;			Objective

&#x09;			Preconditions

&#x09;			Procedure

&#x09;			Expected Result

&#x09;			Evidence

&#x09;	3.4.4 Roles and Responsibilities in Verification

&#x09;		Organizational Roles and RACI Matrix in Verification

&#x09;3.5 Evaluation Criteria

&#x09;	PASS / FAIL / PARTIAL / NOT APPLICABLE





4\. Implementation and Results



&#x09;4.1 Test Environment

&#x09;	4.1.1 Test Object

&#x09;		Beschreibung des Gateways.

&#x09;	4.1.2 Test Setup

&#x09;		Netzwerkaufbau.

&#x09;	4.1.3 Toolchain

&#x09;		Scanner

&#x09;		Fuzzer

&#x09;		Testskripte

&#x09;		Logging Tools

&#x09;4.2 Application of the Testing Methodology

&#x09;	4.2.1 Authentication Tests

&#x09;		Beispiele:

&#x09;			Passwortprüfung

&#x09;			Fehlgeschlagene Logins

&#x09;	4.2.2 Authorization Tests

&#x09;		Rollenmodell

&#x09;		Rechteeskalation

&#x09;	4.2.3 Configuration Manipulation Tests

&#x09;		Unautorisierte Änderungen

&#x09;		Import/Export-Manipulation

&#x09;	4.2.4 Firmware and Update Protection Tests

&#x09;		Signaturprüfung

&#x09;		Downgrade-Schutz

&#x09;	4.2.5 Logging and Traceability Tests

&#x09;		Nachvollziehbarkeit

&#x09;		Manipulationsschutz

&#x09;	4.2.6 Communication Security Tests

&#x09;		Verschlüsselung

&#x09;		Zertifikate

&#x09;4.3 Results

&#x09;	4.3.1 Test Results Overview

&#x09;		Matrix:



&#x09;		Test Case	Requirement	ResultTC-01	Authentifizierung	PASS

&#x09;		TC-02	Firmware Integrity	FAIL

&#x09;	4.3.2 Evaluation of Mitigation Effectiveness

&#x09;		Reduziert die Gegenmaßnahme tatsächlich das ursprünglich identifizierte Risiko?

&#x09;		Stärken der Methodik

&#x09;		Grenzen

&#x09;		Übertragbarkeit auf andere Produkte



5\. Summary

&#x09;5.1 Summary of Findings

&#x09;		Forschungsfragen beantworten

&#x09;	Contributions

&#x09;		Entwickelte Testmethodik

&#x09;		Testframework

&#x09;		Traceability-Konzept

&#x09; 	Limitations

&#x09;		Einzelnes Gateway

&#x09;		Begrenzte Testzeit

&#x09;		Keine vollständige Security-Zertifizierung

&#x09;5.4 Future Work

&#x09;	Automatisierung

&#x09;	Continuous Security Testing

&#x09;	Integration in SDLC

&#x09;	Erweiterung auf weitere OT-Produkte

&#x09;	KI

&#x09;	Neue Standards



Anhang Secure Development Lifecycle

