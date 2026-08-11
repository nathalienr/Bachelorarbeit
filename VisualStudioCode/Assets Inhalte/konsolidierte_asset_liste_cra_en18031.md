# Consolidated Asset List for CRA / EN 18031-1

Created from the sources and findings discussed in the Copilot conversation. Sources are listed per row.

## Physical Assets

| Asset | Asset Type | Protection Goal | Rationale / Use in TARA | Suggested Granularity |
|---------|---------|---------|---------|---------|
| Physical Device | Physical | Integrity; Availability | The physical device as one protected object. Useful to avoid modeling every sensor housing, PCB, screw, and component separately. | Usually one asset per product or device family |
| Hardware Components | Physical | Integrity; Availability | Physical modules and internal components that influence correct device behavior. | Use only when separately relevant for risk or mitigation |
| Internal Storage (Flash, EEPROM, eMMC, SD) | Physical / Logical | Confidentiality; Integrity; Availability | Storage can contain firmware, configuration, logs, secrets, keys, and persistent customer or device data. | Separate when storage media have different access paths or safeguards |
| Debug Interfaces (JTAG, UART, SWD) | Physical / Interface | Confidentiality; Integrity | Debug access can expose firmware, keys, configuration, or allow manipulation. | Separate from normal service interfaces |
| Service Interfaces (USB etc.) | Physical / Interface | Confidentiality; Integrity | Service interfaces can affect firmware, configuration, logs, and device behavior. | Separate if externally accessible or used during service |
| Power Supply / Battery | Physical | Availability | Loss or manipulation of supply can affect availability or safe behavior. | Use only if relevant to product capability or safety context |

---

## Firmware and Software Assets

| Asset | Asset Type | Protection Goal | Rationale / Use in TARA | Suggested Granularity |
|---------|---------|---------|---------|---------|
| Device Firmware | Logical | Integrity | Loss of firmware integrity can lead to malfunctioning device behavior. | One asset per main firmware image unless components have separate update or trust boundaries |
| Bootloader | Logical / Security | Integrity | Bootloader controls startup and can influence firmware integrity and update behavior. | Separate from firmware when it has separate update or security role |
| Recovery System | Logical / Security | Integrity | Recovery functions influence update and restoration behavior. | Separate if recovery image or recovery mode exists |
| Operating System / RTOS | Logical | Integrity | Base software layer that influences device behavior and attack surface. | Usually grouped with firmware unless separately maintained |
| Application Software | Logical | Integrity | Main application logic that implements product functionality. | Usually grouped with firmware unless app layer is separately updated |
| Software Libraries | Logical | Integrity | Libraries influence device behavior and vulnerability exposure. | Group by function unless a library is security-critical |
| Cryptographic Library | Security / Logical | Integrity | Crypto library implements security mechanisms such as TLS, certificates, and key handling. | Separate security asset when used for trust or cryptographic enforcement |
| Webserver Software | Network / Logical | Integrity | Exposed webserver logic can provide access to network or security assets. | Separate if exposed externally or via service interface |
| MQTT Client / Broker Component | Network / Logical | Integrity | MQTT communication logic can affect cloud or device communication. | Separate if MQTT is a relevant external interface or update path |
| HTTP Client | Network / Logical | Integrity | HTTP client can be used for update or cloud communication. | Separate if it handles update, provisioning, or sensitive communication |
| NTP Client | Network / Logical | Integrity | Time source can influence certificates, logging, and protocol behavior. | Separate if time is security-relevant |
| DHCP Client | Network / Logical | Integrity | DHCP controls network addressing and can influence reachability and routing. | Separate if network configuration is in scope |
| DNS Client | Network / Logical | Integrity | DNS resolution influences where the device connects. | Separate if name resolution is used for cloud, update, or management communication |
| BLE Stack | Network / Logical | Integrity | Bluetooth stack provides a network interface and can expose device functions. | Separate when BLE is externally accessible |
| LTE Stack | Network / Logical | Integrity | LTE stack enables cellular communication and modem access. | Separate for devices with cellular modem |
| IO-Link Stack | Network / Logical | Integrity | IO-Link stack provides interface functionality and parameter access. | Separate when IO-Link access is in scope |

---

## Configuration Assets

| Asset | Asset Type | Protection Goal |
|---------|---------|---------|
| Device Parameters | Network / Operational | Integrity |
| Network Configuration | Network | Integrity |
| IP Configuration | Network | Integrity |
| DHCP Configuration | Network | Integrity |
| DNS Configuration | Network | Integrity |
| NTP Configuration | Network / Security | Integrity |
| WLAN / BLE Configuration | Network | Integrity |
| RF Configuration | Network / Physical | Integrity |
| LTE Modem Configuration | Network | Integrity |
| APN Configuration | Network | Integrity |
| SSH Configuration | Network / Security | Integrity |
| Webserver Configuration | Network | Integrity |
| Cloud Endpoint Configuration | Network / Security | Integrity |
| Update Configuration | Security / Operational | Integrity |

---

## Cryptographic Assets

| Asset | Protection Goal |
|---------|---------|
| Device Private Keys | Confidentiality; Integrity |
| Birth Certificate Private Keys | Confidentiality; Integrity |
| Device Certificates | Integrity |
| Root CA Certificates | Integrity |
| Firmware Verification Keys | Integrity |
| TLS Keys | Confidentiality; Integrity |
| LTE Access Keys (SIM/eSIM) | Confidentiality; Integrity |
| Symmetric Keys | Confidentiality; Integrity |
| Session Keys | Confidentiality; Integrity |
| Trust Anchor Store | Integrity |

---

## Authentication Assets

| Asset | Protection Goal |
|---------|---------|
| User Credentials | Confidentiality; Integrity |
| Administrator Credentials | Confidentiality; Integrity |
| Cloud Credentials | Confidentiality; Integrity |
| Bootstrap Credentials | Confidentiality; Integrity |
| Service Credentials | Confidentiality; Integrity |
| API Tokens | Confidentiality; Integrity |
| BLE Bonding Keys (LTK) | Confidentiality; Integrity |
| OAuth Tokens | Confidentiality; Integrity |

---

## Communication and Network Assets

| Asset | Protection Goal |
|---------|---------|
| Ethernet Stack | Integrity |
| TCP/IP Stack | Integrity |
| Bluetooth Stack | Integrity |
| LTE Communication Stack | Integrity |
| MQTT Communication Channel | Integrity |
| Web API | Integrity |
| REST Interface | Integrity |
| Cloud Connectivity Information | Integrity |
| Remote Management Interface | Integrity |
| Update Interface | Integrity |

---

## Operational and Function Assets

| Asset | Protection Goal |
|---------|---------|
| Measurement Values | Integrity |
| Process Data | Confidentiality; Integrity |
| Generated Data | Confidentiality; Integrity |
| Event Data | Integrity |
| Alarm Data | Integrity |
| Device State | Integrity |
| Device Time | Integrity |
| Logs | Integrity |
| Audit Logs | Integrity |
| Update Packages | Integrity |

---

## Intellectual Property Assets

| Asset | Protection Goal |
|---------|---------|
| Firmware Intellectual Property | Confidentiality |
| Hardware Design | Confidentiality |
| PCB Design | Confidentiality |
| Algorithms | Confidentiality |
| Manufacturing Know-how | Confidentiality |
| Process Know-how | Confidentiality |

---

# Recommended Minimal List for Typical Embedded / Industrial Devices

| ID | Asset | Category | Protection Goal |
|---------|---------|---------|---------|
| M-01 | Physical Device | Physical Assets | Integrity; Availability |
| M-02 | Firmware | Firmware and Software Assets | Integrity |
| M-03 | Bootloader | Firmware and Software Assets | Integrity |
| M-04 | Device Parameters | Configuration Assets | Integrity |
| M-05 | Measurement Values | Operational and Function Assets | Integrity |
| M-06 | Logs | Operational and Function Assets | Integrity |
| M-07 | TCP/IP or Communication Stack | Communication and Network Assets | Integrity |
| M-08 | Webserver / API | Communication and Network Assets | Integrity |
| M-09 | Device Credentials | Authentication Assets | Confidentiality; Integrity |
| M-10 | Device Certificate + Private Key | Cryptographic Assets | Confidentiality; Integrity |
| M-11 | Root Certificates | Cryptographic Assets | Integrity |
| M-12 | Firmware Verification Key | Cryptographic Assets | Integrity |
| M-13 | Update Mechanism | Communication and Network Assets | Integrity |
| M-14 | Cloud Connectivity Configuration | Configuration Assets | Integrity |
| M-15 | Intellectual Property | Intellectual Property Assets | Confidentiality |

---

# Source Notes

| Source File | Reference | Relevant Content Used |
|---------|---------|---------|
| assets.xlsx | turn2search83 | Main source for asset categories, network assets, security assets, physical device, firmware, parameters, cryptographic material, credentials, modules such as STM32/SARA/NINA, external flash and EEPROM. |
| en18031-1_requirements_template.docx | turn1search27 | Source for EN 18031-1 oriented security and network assets, including protocol stacks, configurations, certificates, private keys, root certificates, credentials, and crypto libraries. |
| CS_Template_Customer_Req-Infos_18031-1_v06.xlsx | turn2search49 | Template source for an Assets sheet and relation to EN 18031-1 test information, software update components, and asset classification. |
| ifm Template Risk Assessment.xlsx | turn2search60 | Risk assessment source with examples such as User Credential, Password, Database, Network Configuration, and interface-based TARA structure. |
| TARA_Template_EN_v1.0.xlsx | turn2search61 | TARA template source defining assets as data, functions and components worth protecting, and an interface-based workflow. |
| Template Risk Assessment with vectors - guidance.xlsx | turn2search68 | Source for physical device asset, physical threat scenarios, storage, debug/service interfaces, firmware, configuration, keys, and IP-related concerns. |