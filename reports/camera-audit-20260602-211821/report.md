# Network Camera Audit Report

- Timestamp: 2026-06-02 21:28 MDT
- Host: MGMT-XPS
- Scope: Read-only discovery, service fingerprinting, and traffic analysis on `192.168.1.0/24`
- Constraints honored: no exploitation, no system modification, no data deletion

## Executive Summary

I did not confirm any unauthorized IP cameras, NVRs, DVRs, RTSP services, ONVIF services, or MJPEG streams on the LAN.

What I did find:

- No camera-relevant TCP service was confirmed open on `554`, `8554`, `37777`, `8000`, `8080`, `8443`, `80`, or `443` on the discovered hosts.
- Two devices exposed UPnP/media behavior:
  - `192.168.1.154` answered UPnP as a Linux/Mediabolic media device and continuously multicasted SSDP.
  - `192.168.1.230` answered as a Roku-class device with AirPlay-related service advertising.
- One unknown device, `192.168.1.16`, remains the strongest follow-up candidate:
  - AzureWave MAC/OUI.
  - Repeated gateway-originated probes to camera-like ports `554`, `8554`, and `37777`, plus `8000`, `8080`, `8443`, `1935`, `10000`, `7000`, `38080`, `2020`, `2121`, `22`, `23`.
  - Persistent TCP traffic to `64.233.181.188:5228`, which is consistent with Google push / Android-style connectivity.
  - No confirmed open camera service from this audit.
- One multicast-heavy device, `192.168.1.183`, now looks like a smart TV / streaming endpoint rather than a camera:
  - `8001/udp` payload was `{"type":"discover"}`.
  - SSDP searches targeted `roku:ecp`, DIAL, LG webOS second-screen, Sony ScalarWebAPI, and UPnP MediaRenderer.
  - `8001/udp` was identified by Nmap as `vcom-tunnel`.
  - This is consistent with a consumer media device, not a hidden camera.

Bottom line:

- No confirmed hidden camera was found.
- One ambiguous device (`192.168.1.16`) remains worth physical/asset follow-up.
- `192.168.1.183` is better treated as an unmanaged consumer media device unless a local label proves otherwise.

## Method

- Collected local interface, route, DNS, and neighbor-table state.
- Ran ARP-based discovery against `192.168.1.0/24`.
- Ran targeted TCP service scans on camera-relevant ports.
- Ran UDP discovery scans for UPnP, WS-Discovery, and mDNS.
- Captured 10 minutes of `enp3s0` traffic and reviewed packet patterns.

## Local Network State

- Local IP: `192.168.1.221`
- Subnet: `192.168.1.0/24`
- Gateway: `192.168.1.1`
- DNS: `192.168.1.1`, `2600:6c67:8940:ebe:21b:21ff:fece:cd30`
- Active interfaces:
  - `enp3s0`
  - `docker0`
  - `tailscale0`
  - `wlp4s0` down

## Inventory

### Known / Identified Devices

| IP | MAC | Vendor / OUI | Host / Role | Notes |
|---|---|---|---|---|
| `192.168.1.1` | `00:1b:21:ce:cd:30` | Intel | Gateway / pfSense.home.arpa | No camera service confirmed. |
| `192.168.1.2` | `2c:27:d7:f0:fc:bf` | Hewlett | Unraid | mDNS/SSDP only; no camera ports confirmed. |
| `192.168.1.4` | `d8:5e:d3:00:58:33` | Giga-byte | Proxmox host | No camera service confirmed. |
| `192.168.1.19` | `bc:24:11:b1:94:a4` | Unknown | orchestrator | Known infra; no camera service confirmed. |
| `192.168.1.36` | `bc:24:11:32:07:83` | Unknown | de-edge-01 | Known infra; no camera service confirmed. |
| `192.168.1.48` | `bc:24:11:20:08:07` | Unknown | de-pubmachine-01 | Known infra; no camera service confirmed. |
| `192.168.1.55` | `bc:24:11:39:0d:c1` | Unknown | affiliate-engine-01 | Known infra; no camera service confirmed. |
| `192.168.1.58` | `48:a2:e6:93:98:c5` | Resideo | Smart home / security class device | No camera service confirmed. |
| `192.168.1.71` | `00:15:99:b5:7a:3d` | Samsung | Media / appliance class device | No camera service confirmed. |
| `192.168.1.73` | `10:ce:02:87:fa:c7` | Amazon | Amazon device | No camera service confirmed. |
| `192.168.1.106` | `bc:24:11:2f:a0:c0` | Unknown | de-truenas-01 | mDNS `truenas.local`; no camera service confirmed. |
| `192.168.1.107` | `bc:24:11:87:e9:19` | Unknown | de-librarian-01 | No camera service confirmed. |
| `192.168.1.108` | `bc:24:11:56:99:c4` | Unknown | de-gateway-01 | No camera service confirmed. |
| `192.168.1.136` | `bc:24:11:31:3b:42` | Unknown | pop-ollama | mDNS activity present; no camera service confirmed. |
| `192.168.1.150` | `00:15:99:b5:7a:3d` | Samsung | Media / appliance class device | No camera service confirmed. |
| `192.168.1.152` | `bc:24:11:79:43:dd` | Unknown | Home Assistant host | mDNS `homeassistant`; no camera service confirmed. |
| `192.168.1.154` | `00:09:b0:d4:7a:04` | Onkyo | AV / media receiver | UPnP/Mediabolic media descriptor on `1900/udp`; no camera service confirmed. |
| `192.168.1.157` | `48:a2:e6:93:98:c5` | Resideo | Smart home / security class device | No camera service confirmed. |
| `192.168.1.162` | `10:ce:02:87:fa:c7` | Amazon | Amazon device | No camera service confirmed. |
| `192.168.1.178` | `10:ce:02:87:fa:c7` | Amazon | Amazon device | No camera service confirmed. |
| `192.168.1.186` | `10:ce:02:87:fa:c7` | Amazon | Amazon device | No camera service confirmed. |
| `192.168.1.188` | `00:f6:20:a4:65:89` | Google | Google Home Mini | mDNS `googlecast` / `googlezone`; no camera service confirmed. |
| `192.168.1.196` | `40:99:22:51:2d:95` | AzureWave | Unknown consumer device | No camera service confirmed. |
| `192.168.1.230` | `08:05:81:78:80:01` | Roku | Streaming device | UPnP responder with AirPlay-style service name; no camera service confirmed. |

### Ambiguous / Unknown Devices

| IP | MAC | Vendor / OUI | Observed Behavior | Camera Relevance |
|---|---|---|---|---|
| `192.168.1.16` | `14:13:33:ba:9f:31` | AzureWave | Repeated gateway SYNs to `554`, `8554`, `37777`, `8000`, `8080`, `8443`, `1935`, `10000`, `7000`, `38080`, `2020`, `2121`, `22`, `23`; persistent Google push traffic | Highest follow-up priority |
| `192.168.1.183` | `aa:ad:c0:49:a5:e5` | Unknown | `8001/udp` discovery and SSDP bursts for Roku/DIAL/webOS/Sony/UPnP MediaRenderer | Likely smart TV / media device |
| `192.168.1.188` | `00:f6:20:a4:65:89` | Google | Google Home Mini mDNS advertising and multicast chatter | Low camera relevance |
| `192.168.1.100` | `00:00:00:00:00:00` | Xerox | Stale / unusable ARP artifact | No conclusion |
| `192.168.1.103` | `00:00:00:00:00:00` | Xerox | Stale / unusable ARP artifact | No conclusion |

## Camera Detection Results

### Known Camera Vendors

I did not confirm any of the following vendors on the LAN during this audit:

- Hikvision
- Dahua
- Reolink
- Amcrest
- Axis
- Ubiquiti Protect
- Wyze
- Foscam
- TP-Link Tapo
- Ring
- Blink
- Arlo
- Eufy

### Camera-Relevant Ports

No host exposed a confirmed open listener on:

- `554`
- `8554`
- `37777`
- `8000`
- `8080`
- `8443`
- `80`
- `443`

In this capture, those ports were either filtered or only appeared as scan targets, not as confirmed services.

### RTSP / ONVIF / MJPEG

- No confirmed RTSP service.
- No confirmed ONVIF service.
- No confirmed MJPEG stream.
- No confirmed DVR/NVR web UI.

## Traffic Analysis

### High-Activity Devices

| Rank | IP | Why it stands out | Suspicion |
|---|---|---|---|
| 1 | `192.168.1.16` | Gateway-originated probes on camera-like ports, plus Google TCP traffic | High |
| 2 | `192.168.1.154` | Repeated SSDP/UPnP multicast on `1900/udp`; media receiver fingerprint | Low |
| 3 | `192.168.1.230` | UPnP responder, AirPlay-style service name, multicast advertising | Low |
| 4 | `192.168.1.183` | `8001/udp` discovery plus SSDP searches for TV/media ecosystems | Low |
| 5 | `192.168.1.188` | Google Home Mini multicast / Cast advertisements | Low |

### Observations

- `192.168.1.154` repeatedly multicasted SSDP advertisements to `239.255.255.250:1900`.
- `192.168.1.230` replied to SSDP probes and advertised an AirPlay-style service name.
- `192.168.1.188` advertised Google Cast / Google Home Mini services via mDNS.
- `192.168.1.183` emitted periodic multicast beacons and actively searched for Roku/DIAL/webOS/Sony/MediaRenderer endpoints, which is characteristic of a media device or smart TV control path.
- `192.168.1.16` had the most camera-like traffic pattern:
  - repeated TCP SYNs to `554`, `8554`, and `37777`
  - additional probes to common device/admin ports
  - a live Google TCP session on `5228`, which is more typical of Android/Google push connectivity than surveillance hardware

### Cloud / External Traffic

- No cloud video upload pattern was confirmed.
- No sustained high-bandwidth upload stream was confirmed.
- I did observe external Google traffic involving `192.168.1.16`, but not a video-stream signature.

## Infrastructure Review

### ARP / Neighbor Table

- The live neighbor table matched the expected known infrastructure for the fleet hosts.
- Additional active devices found during capture:
  - `192.168.1.183`
  - `192.168.1.188`

### Routing / DNS

- Default route: `192.168.1.1`
- LAN DNS: `192.168.1.1`
- Tailscale DNS: `100.100.100.100`
- Local DNS domain: `home.arpa`

### DHCP Comparison

- I did not access router DHCP leases directly in this audit.
- Cross-checking against the architecture map shows the expected fleet IPs were present.
- The extra multicast hosts (`192.168.1.183`, `192.168.1.188`) were not listed in the architecture map and are worth follow-up.

## Recommended Next Steps

1. Physically identify `192.168.1.16` and verify what device it is.
2. Check router/client labels for `192.168.1.183` and `192.168.1.188`.
3. If you want a deeper camera-only sweep, run a focused scan from the router side or from another host with `arp-scan` / DHCP lease access.
4. If `192.168.1.16` is a TV, cast device, or phone, document it so it stops being a false-positive camera candidate.
5. If `192.168.1.183` is still unlabeled after physical review, treat it as an unmanaged smart TV / media device until proven otherwise.

## Conclusion

No unauthorized camera was confirmed.

The audit does identify one ambiguous device (`192.168.1.16`) that warrants manual follow-up because it combines:

- unknown consumer-grade Wi-Fi vendor
- gateway probes on RTSP/camera-adjacent ports
- live Google traffic

The remaining notable devices are consistent with media, streaming, Google Cast, Home Assistant, and AV hardware rather than hidden cameras.
