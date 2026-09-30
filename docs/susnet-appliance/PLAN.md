# SusNet Raspberry Pi appliance — v1 implementation plan

Planning baseline: 2026-09-29. Architecture and implementation sequence are decided below. No image has been built or hardware validated in this planning pass. Exact dependency versions, firmware parameters, and hardware calibration become release inputs only after the specified qualification gates pass; inspected upstream commits are evidence, not a claim of compatibility.

## 1. Product boundary

Build a clean Raspberry Pi 4B ARM64 appliance from the official ASL3 image-builder path, using Debian 13 Trixie and Asterisk 22. Ship versioned SusNet Debian packages and a browser wizard on top. Never clone the live SD card or wholesale-copy its source tree, configuration, service units, logs, backups, or user directories.

The first pilot is for known amateur-radio operators. Imager owns hostname, OS account/password, locale, Wi-Fi, and optional SSH. The wizard owns radio identities, service credentials, hardware qualification, and appliance features. Each operator supplies their own callsign, AllStar node/password, DMR ID/suffix, BrandMeister hotspot password, TGIF security password, APRS identity/settings, and optional 44Net configuration.

User-confirmed kit: the same AURSINC USB dongle used by SusNet, plus a Heltec V3 companion using the US default profile. Labeled USB placement is acceptable. Baseline Pi is the existing 4B 8 GB model; other Pi 4B memory sizes require separate qualification. Use a documented power supply, cooling enclosure, and 32 GB or larger high-endurance microSD; freeze exact tested parts in the kit manifest. The AURSINC product revision, integrated-radio or external-radio arrangement, wiring, and PTT polarity still require physical identification. Do not infer those from C-Media VID/PID alone.

| Capability | v1 decision |
|---|---|
| AllStar RF | Exactly one operator-owned public RF node using the standardized AURSINC kit |
| Internal bridge | Exactly one local private USRP node; no public registration, directory publication, or incoming public dialplan route |
| DMR | Software vocoder, BrandMeister or TGIF, one active network at a time, numeric talkgroup entry, network-specific favorites |
| Other digital modes | D-Star, YSF, P25, NXDN assets installed/staged; disabled in configuration and backend capability checks until separately qualified |
| APRS | APRS-IS Internet receive, messaging, dashboard, and explicitly enabled announcements; no RF decode, modem, RF iGate, or packet gating |
| MeshCore | Heltec V3 USB serial companion; browser messaging; optional explicitly confirmed supported firmware flash |
| 44Net | Optional portal-generated WireGuard upload/paste; skip/resume during verification or tunnel approval |
| Remote management | Optional Tailscale; authenticated private management only |
| Exclusions | No GMRS code, nodes, directory feeds, controls, branding, or defaults; no MeshCore-to-TTS path; no guest-audio lanes or personalized favorites |

Keep this work in `docs/susnet-appliance/` during planning. Implementation belongs in a new standalone `susnet-appliance` project/repository, not CommsLab configuration or web01. No changes to allstar01, web01, or live SusNet are part of this plan.

## 2. Verified upstream structure and consequences

The official [ASL3 appliance documentation](https://allstarlink.github.io/install/pi-appliance/) identifies Trixie, Asterisk 22, Allmon3, Cockpit, and the ASL tools. The [Pi 4B limitations](https://allstarlink.github.io/basics/incompatibles/) support our decision to use only one USB audio interface; the serial Heltec is a separate device class.

Inspected official [image-builder commit](https://github.com/AllStarLink/asl3-pi-image/tree/85316e04773cb2c93de3deb92a88e5546e84db35):

| File or directory | Observed role |
|---|---|
| `build-image` | Clones CustomPiOS, generates `raspios_lite_arm64`, applies a patch, runs image assembly, compresses, then uploads to ASL infrastructure |
| `config` | `base(network,pkgupgrade,asl3)` module graph, ARM64 Raspberry Pi OS base, package dist-upgrade |
| `modules/asl3/start_chroot_script` | Installs ASL repository/packages, first-boot units, log tmpfs mounts, and serial settings |
| `modules/asl3/filesystem/` | First-boot certificate, manager credential, package-update, completion/reboot logic |
| `repo/repo_create_imager_json` | Image sizes, hashes, supported boards, and customization metadata |
| `.github/workflows/` | Upstream-specific ARM64 AWS build and publishing infrastructure |

Do not execute the upstream publisher. Add a thin maintained downstream module and patch set, keeping ASL provenance and license notices. Replace mutable downloads and first-boot upgrades with locked artifacts. Retain required Pi initialization; replace example-node/Allmon seeding with unconfigured SusNet state. Preserve Imager account creation and storage expansion.

Other inspected sources:

| Upstream | Commit inspected | Qualification meaning |
|---|---|---|
| [CustomPiOS fork used by ASL](https://github.com/jxmx/CustomPiOS) | `f6cf86161aba94e818818c60ed27593512a7239e` | Builder candidate only |
| [ASL appliance package](https://github.com/AllStarLink/asl3-pi-appliance) | `844be1095a8ad43f96045ff304c573c1e572eca6` | Provides firewalld, Cockpit, Avahi integration |
| [Analog_Bridge](https://github.com/DVSwitch/Analog_Bridge) | `dbc4c58f56a70b2da43861efd2393fa415e38c53` | Bookworm filesystem mirror; ARM64 executable exists |
| [MMDVM_Bridge](https://github.com/DVSwitch/MMDVM_Bridge) | `285e51e98dca637eab296a8fe00879e39381f678` | Bookworm filesystem mirror; ARM64 executable exists |
| [MeshCore](https://github.com/meshcore-dev/MeshCore) | `e94125987ed87497e706a0b54d1e80c709343980` | Includes `Heltec_v3_companion_radio_usb` target |
| [Raspberry Pi Imager](https://github.com/raspberrypi/rpi-imager) | `3186d3920d8f060422c08104ac06772ba4d5922e` | Documents image customization and local manifest requirements |

ARM64 bridge executables do not prove working Trixie dependencies or a working software AMBE encoder. The first engineering gate must validate Analog_Bridge, MMDVM_Bridge, and the selected software vocoder together on real Pi 4B hardware. Prefer native ARM64 throughout; any ARM32 emulator component requires an explicit pinned compatibility package and separate test result, never wholesale addition of Bookworm OS libraries. If the software-only path cannot pass on Trixie, report a blocked DMR release gate; do not silently downgrade Debian or add a USB vocoder.

## 3. Build and distribution contract

Use a dedicated disposable Linux ARM64 build runner with root/mount support. macOS is suitable for editing and unit tests, not the native image build. This runner is independent of the CommsLab VM. Assembly must run without operator credentials or deployment keys.

Repository layout:

```text
image/                 ASL/CustomPiOS adapter, downstream patches, SusNet module
packaging/             Debian package definitions and systemd units
src/                   UI, API, privileged broker, service adapters
schemas/ templates/    Versioned canonical models and deterministic renderers
hardware/              Kit BOM, labeled-port photos, firmware and calibration profiles
locks/                 Base image, packages, sources, firmware, toolchain hashes
tests/                 Unit, integration, image, fault-injection, hardware procedures
docs/                  Operator guide, recovery guide, maintainer guide, release evidence
```

The lock manifest records base image URL/hash, OS identity, ASL/CustomPiOS commits, patch hashes, architecture, complete `.deb` dependency closure, apt signing-key fingerprints and verified metadata, Python wheels and hashes, any JS build dependencies, firmware hashes, build-tool image digest, license inventory, and release timestamp. Mirror permitted dependencies into an immutable release input store. For binaries unavailable as source, retain the exact binary hash and origin; do not claim source-reproducible builds of those binaries. Missing hashes, missing dependency versions, or unverified origins fail the build.

Build sequence: resolve and review inputs once → lock → build packages → assemble from the pinned official-derived base → apply SusNet module → validate offline filesystem → sanitize image → produce compressed artifact and metadata → independently rebuild → qualify on hardware → sign and distribute the pilot bundle. Rebuilds use cached locked inputs without contacting moving package channels. No `curl | sh`, live `pip install`, tracking branches, or automatic package upgrades on customer first boot.

Generate machine identity, host SSH keys, web TLS keys, session secrets, and AMI credentials only at first boot. Remove build identities, histories, connection profiles, credentials, example enabled nodes, caches containing sensitive input, and seeded host keys from the final image. Normalize build timestamps, file order, filesystem creation metadata, and compression settings. Require identical package/config payload hashes on two clean builds. Compare full image hashes too; any residual filesystem nondeterminism must be enumerated and explained in a reproduction report. Do not label the image bit-for-bit reproducible until the full hashes match.

Distribute `susnet-pi4-arm64-<version>.img.xz`, signed SHA-256 manifest, Imager manifest, SBOM, corresponding source/license bundle where required, release notes, and acceptance report. Pilot distribution is a versioned downloadable bundle to known operators; no public catalog listing or hosting deployment is assumed by this plan.

**Imager is an integration contract, not just a file format.** Current [Imager customization documentation](https://github.com/raspberrypi/rpi-imager/blob/main/doc/os_customisation_formats.md) says a local image opened with “Use custom” does not by itself carry customization metadata. Ship a local `.rpi-imager-manifest` alongside the image and test the Content Repository import flow. A hosted manifest is optional later. Require a tested Imager 2.x release and publish its exact version in the pilot guide.

The ASL generator currently emits `init_format=systemd`, while modern Pi OS Trixie bases may use `cloudinit-rpi`. Choose the first pinned Trixie base compatible with the ASL module; derive and lock its actual initialization mechanism and emit the matching Imager metadata. The qualification rule is fixed: all Imager fields must survive first boot and reboot, otherwise that base/manifest pair cannot ship. Never copy upstream metadata blindly or let the builder auto-select the newest downloaded image.

## 4. Package and service ownership

Use Debian packages and systemd, not a container stack for radio/USB services. One canonical configuration owner prevents the wizard, ASL menus, and helper scripts from rewriting one another's files.

| Package | Services and responsibility | Privilege |
|---|---|---|
| `susnet-appliance` | Dependencies, release marker, first boot, safe defaults, health aggregation | Root only for initialization |
| `susnet-web` | Locally bundled frontend; FastAPI API behind the existing Apache TLS server | Dedicated unprivileged user; no device or configuration-write access |
| `susnet-configd` | Typed privileged RPC, PAM authentication, configuration transactions, firewall/tunnel control, backup/restore, bounded hardware-flash operation | Root; Unix socket only; fixed operations, no arbitrary shell |
| `susnet-radio` | ASL template adapter, local status/control adapter, internal-node lifecycle, optional APRS announcement queue | Asterisk user plus narrow broker operations |
| `susnet-digital` | Pinned bridge/vocoder integration, serialized DMR state machine, network-specific profiles/favorites | Separate digital-service user; no USB access |
| `susnet-aprs` | Single APRS-IS connection, parser, messaging state, sanitized events | Separate APRS user |
| `susnet-meshcore` | Companion protocol client, messages/contacts, reconnect and USB identity | Separate user; access only to selected serial device |
| `susnet-digital-staged` | Installed inactive non-DMR mode/gateway assets and capability manifest | All mode services disabled/masked |

Use upstream ASL packages without forking Asterisk. Start with the kit's verified SimpleUSB configuration; if physical inspection establishes it needs USBRadio DSP, record that as a kit-profile correction before release. No second USB audio lane is added for DVSwitch.

Keep Apache as the sole browser entry point to avoid a second competing web server. Disable stock unauthenticated landing/Allmon routes. Allmon3 and Cockpit can remain installed as upstream dependencies but are disabled and unexposed by default; console/SSH recovery uses the Imager account. Every browser API and event stream requires appliance authentication. Do not proxy generic AMI or Asterisk commands into the browser.

Default internal port registry: AMI TCP 5038 on loopback; Asterisk USRP receive UDP 32001, Analog_Bridge receive UDP 34001; Analog_Bridge TLV receive UDP 31100, MMDVM_Bridge TLV receive UDP 31103; software vocoder UDP 2470 only if the qualified vocoder uses that interface. The USRP configuration pairs Asterisk transmit to 34001 with Analog_Bridge transmit to 32001. Allocate the internal node deterministically from ASL's private range after checking collision with the public node; do not reuse a live SusNet identifier. All these endpoints are local-only. Where upstream binaries bind wildcard addresses despite a loopback peer, firewall non-loopback access and assert it in tests.

Service dependencies fail closed: incomplete identity/configuration means no radio/network startup; missing or ambiguous USB means no RF activation. Browser downtime must not terminate an already valid voice session. A configuration failure must not prevent local management from starting.

## 5. Browser setup and security

After Imager initialization, serve `https://<hostname>.local/` using Avahi and a unique first-boot certificate. Private-LAN HTTP only redirects to HTTPS and accepts no credentials or changes. Provide router/DHCP-address fallback when mDNS is unavailable. Generate certificates with appropriate hostname SANs, not only a CN.

For the pilot, use an explicitly documented local certificate trust step. A self-signed certificate encrypts traffic but does not establish device identity on its own. Show its fingerprint at the physical console and through authenticated SSH so operators can verify it. A verified locally trusted CA certificate may be installed later. Do not imply that merely accepting the warning provides protection against an active attacker on the setup LAN.

Authenticate using the OS user/password created by Imager through a dedicated PAM service. Never read or copy the password hash into SusNet, and never store the submitted OS password. Only authorized interactive local administrator accounts can manage the appliance. Handle a missing/locked Imager account with a recovery screen; never create a fallback password or unauthenticated “first person wins” claim flow. SSH may remain off while password-based browser login works.

The privileged broker owns authentication grants and checks session identity/action authorization itself. The frontend cannot assert that an arbitrary request is an administrator. Use opaque server-side sessions, Secure/HttpOnly/SameSite cookies, CSRF tokens, strict Origin/Host checks including WebSockets, login throttling, 30-minute idle and 12-hour maximum sessions, reauthentication for export/restore/firmware/update, and session revocation on password/account changes. No credentials in URLs or browser local storage; secret fields return only “configured,” never their stored value.

Config RPC uses Unix peer credentials, length-limited structured messages, schema validation, operation IDs, revision preconditions, timeouts, and allowlisted actions. The broker accepts no paths, shell fragments, service names, arbitrary URLs, Asterisk CLI strings, or firmware commands from the browser. It constructs fixed argument arrays and enforces permissions independently of UI controls. Hostname/destination inputs use strict grammars and endpoint rules rather than shell interpolation.

Runtime hardening: distinct service users, restrictive umask, no-new-privileges, filesystem protections, bounded writable directories, restricted devices, private temporary directories, and no debug/core dumps containing secrets. Root broker code should be small and independently tested. Use local frontend assets; no analytics, external scripts, or CDN dependency.

Wizard steps, each saved and resumable:

1. Sign in, show appliance/version, verify clock, storage, network and USB inventory.
2. Enter operator callsign and AllStar node credentials; validate syntax separately from online registration.
3. Select the supported kit, confirm detected devices/port map, enter required radio settings, and perform receive calibration. Transmit tests require an explicit action and timeout.
4. Enter DMR ID and explicit suffix, configure BM and TGIF separately, test each, and create optional favorites. Neither credentials nor favorite destinations are seeded from SusNet.
5. Configure APRS-IS identity, endpoint/filter and messaging credentials. Receive-only is valid; announcements start off and require a chosen scope and test.
6. Detect MeshCore companion, confirm US profile and device settings. Offer firmware flashing only as an explicit separate operation; skip is always available.
7. Optional 44Net: “not started / awaiting callsign verification / awaiting tunnel / ready to import / validating / active / error.” Link to the portal, accept only its tunnel configuration, and allow completion of other steps while pending.
8. Optional Tailscale device login via the operator's own account, without retaining a reusable enrollment key or enabling public sharing.
9. Show a redacted summary, disabled/pending features, validation results, and Apply. Distinguish “saved,” “running,” “registered,” “end-to-end tested,” and “not tested.”

## 6. Canonical configuration, secrets, and transaction protocol

Use a strict versioned JSON model, not editable shell environment files. It contains operator identity, public node, hardware profile/binding, DMR profiles and selected destination, APRS options, MeshCore profile, network options, and secret references. Secrets are supplied as explicit set/retain/delete operations; a blank field never ambiguously clears an existing password. Reject unknown fields, duplicate identifiers, invalid encodings, line breaks/control characters, oversized values and unsupported capabilities.

Persist canonical models, secret records, and generated generations under root-owned directories with mode 0700 and files 0600. No secret-bearing durable configuration is world- or group-readable. Use per-service systemd credentials or root-created private runtime config directories to give each unprivileged daemon only its required configuration, readable by that service alone. This is the necessary runtime exception to root-only storage: Asterisk must be able to read its own password without running as root. The web service receives no stored secrets. Root-only permissions do not encrypt a physically stolen SD card; do not describe them as encryption.

Keep the service's canonical configuration roots separate from package defaults. Launch Asterisk with an explicit managed configuration directory; provide equivalent fixed paths for the bridges. Root helpers expose sanitized diagnostics and calibration rather than making secret-bearing files readable to menu tools. Manual config edits are detected by hashes and shown as drift; block automatic apply until they are reconciled, rather than silently overwriting them.

Transaction algorithm:

1. Authenticate/authorize; acquire one appliance mutation lock; verify requested base revision and idempotency key. Draft save is separate from apply.
2. Validate canonical schema and cross-field invariants: one public RF node, one internal USRP node, unique ports, supported hardware, owned identifiers present, one active DMR network, no excluded modes/routes, approved management interfaces.
3. Render all affected files into a new root-only generation on the same filesystem. Parse the generated files back; verify path/section uniqueness, referenced secrets, include closure, destination allowlists, and port ownership. Never perform string substitution into live files.
4. Run available native checks in isolation: Apache config test, firewalld config validation, systemd unit validation, WireGuard parser/netns validation, and daemon-specific config checks where supported. Do not invent an Asterisk “check everything without side effects” flag: launch the pinned stack in an isolated network namespace without physical devices or outbound access to validate startup and expected modules/nodes. Perform such integration checks in CI and repeat lightweight deterministic checks on device.
5. Present redacted changes and interruption scope. For network changes arm a 120-second rollback timer independent of the web process; it requires successful private-browser reconnection and server-side health validation to commit.
6. Quiesce only affected services: inhibit transmit, disconnect bridge links as required, stop readers whose config spans files. Persist and fsync a transaction journal with old/new generation references.
7. Fsync new files/directories; atomically replace a single `current` generation pointer. Individual renames alone are not a multi-file transaction. Materialize runtime credentials and apply external system settings in journaled order. Install restrictive firewall state before bringing up tunnels or listeners.
8. Start/restart in dependency order: vocoder → bridges → permitted local links; ASL and hardware activation follow their readiness gates. Query actual state, registrations, devices, sockets and rules; process-alive is insufficient.
9. On success write/fsync the commit record and retain the previous generation. On failure stop affected transmit paths, restore the old generation and journaled firewall/routes, regenerate runtime credentials, restart and verify old services. If rollback itself fails, enter recovery with RF/digital transmission inhibited and private management alive.
10. At boot, recover unfinished journals before any radio/tunnel service starts. Power loss after pointer change but before commit restores the previous generation. Keep three committed generations plus any current transaction, bounded by disk limits. Do not automatically retry live transmissions or replay APRS/MeshCore sends.

Checks distinguish local invalid configuration (rollback), unavailable external networks (degraded, no false success), and failed online authentication (feature blocked). Save pending configurations without falsely declaring them active. A network outage must not reset the operator's identity or erase credentials.

Audit logs contain action type, operator account, revision, time, result and redacted diagnostics. Exclude request bodies, environment dumps, secrets and raw daemon config echoes. Bridge stdout/stderr must be audited with synthetic canary secrets before release; disable unsafe upstream logging and expose sanitized status instead. Redact before storage, not just in the browser. Message content stays in bounded private message storage, not general service logs.

## 7. Radio, DMR, APRS and MeshCore behavior

### RF and link behavior

Persistent hardware identity uses serial plus VID/PID when available, otherwise physical USB topology plus the frozen kit profile. No hard-coded ALSA card index or `/dev/ttyUSB0`. Label AURSINC and Heltec ports with a kit photograph. Unexpected extra audio devices, multiple matching serial adapters, moved devices, or a different hardware revision require an explicit rebind/calibration check. CP2102 detection alone does not authorize flashing or prove that the board is a Heltec.

Set initial RF enable=false until setup and calibration succeed. Test carrier/squelch, PTT polarity, level/deviation and unkey behavior on the actual kit. Use the radio's hardware transmit timeout where supported; software cannot guarantee unkey after every host/USB failure. Freeze measured tuning values and tolerances with the kit profile. Default maximum continuous transmit is 180 seconds, or a lower kit-supported limit. A test transmission stops on button release, session loss, or a 10-second server timer, whichever happens first. No boot-time test transmission.

Default operating topology permits RF↔AllStar or RF↔DMR, with no unintended external AllStar↔DMR conference. Switching to DMR disconnects external AllStar links and verifies they are gone; reverse switching detaches the private bridge. Enforce this in node/dialplan and backend policy, including inbound calls, not only browser controls. Cross-network conferencing is outside v1.

### DMR

Store two separate credential profiles; select an endpoint from a versioned network catalog. BM uses the [operator's hotspot security password](https://help.brandmeister.network/hotspots/connecting-hotspots/pi-star-mmdvm/), not the website password. TGIF uses the operator's secure connection password; its [FAQ](https://tgif.network/faq.php) describes ESSIDs and network-specific behavior. Do not ship legacy shared passwords.

DMR ID is a validated operator-supplied base ID; suffix is an explicit two-digit field including leading zeros. Preserve base subscriber identity separately from the combined endpoint ID. Validate against the chosen protocol profile; never truncate or guess a supplied ID. Talkgroup input accepts protocol-valid numeric group IDs even when absent from a directory, with an explicit error for reserved control values. Favorites are keyed by `(network, group ID, call type)`; switching networks cannot reinterpret a favorite as belonging to the other network. Direct/private-call features are not required for v1.

State machine: `disconnected → preparing → connecting → ready → switching → ready/error`. Serialize switch/tune/disconnect requests with revision checks. Require fresh status and a gap in transmit/receive; wait up to 30 seconds before reporting busy. Detach RF/private-node audio, inhibit transmissions, stop the old bridge connection, confirm closure, generate the selected profile/TG, start the new connection, confirm network authentication and local vocoder readiness, apply any qualified network-specific TG selection operation, then reconnect audio. Never run simultaneous BM and TGIF sessions. On failure remain safely disconnected and offer a retry; never silently transmit on the previous network.

Separate “requested TG,” “locally configured TG,” and any remotely observed state. Some network selection needs traffic/signaling; qualify BM and TGIF independently and do not report network acknowledgment when the protocol supplies none. Test incoming static-group traffic and local filtering; an arbitrary requested TG must not let unrelated static groups leak into RF. Reboot starts with no external link until operator resume; saved favorites/settings remain.

D-Star, YSF, P25 and NXDN are visibly “installed, not configured/validated.” Stage the required bridge/gateway assets through a pinned capability manifest, including any codec dependencies; their normal upstream components include ircDDBGateway, YSFGateway, P25Gateway and NXDNGateway where required by the selected topology. Resolve their exact distribution packages and redistribution permissions during dependency qualification. No fake IDs, default reflector connections, active listeners, or frontend-only restrictions. Missing required staged assets block declaring the requested v1 bundle complete.

### APRS-IS

Extract behavior from selected clean source functions only after review; build new templates and synthetic fixtures. Document the observed SusNet receive/message/announcement behavior in a parity checklist before replacing it. No live log export is needed.

One upstream connection, bounded server-side filter, exponential reconnect with jitter, packet length/format validation, escaped browser display, message IDs, acknowledgment/rejection tracking, deduplication and bounded retries. Explicitly distinguish receive-only login from verified send capability per the [APRS-IS connection specification](https://www.aprs-is.net/Connecting.aspx). Never equate “written to socket” with delivered. No automatic retransmit of queued messages after reboot without an expiry check.

Announcements are an optional, separately controlled APRS-only service: chosen event types, length/rate limits, duplicate suppression, quiet hours, bounded queue, and local RF destination only. Default off. It does not accept MeshCore event types, cannot inject commands, and must not leak announcements to AllStar or DMR links. Use a local speech engine with fixed arguments and sanitized text. Permit send/announce tests only through explicit operator actions.

### MeshCore

Probe the selected CP2102 serial device using the companion protocol; read firmware/board/version/settings before offering operations. Default to the user's US profile; lock its actual frequency, bandwidth, spreading factor, coding rate, power and firmware version after comparison with the working SusNet companion and official release. “US default” is a profile name, not enough information to invent those values. Do not reconfigure a working companion merely because it was attached.

Optional flash flow: show detected board, installed/target version, pinned artifact/hash, expected settings impact and recovery instructions → explicit reauthentication and flash confirmation → exclusively lock serial device → back up exportable settings → stop companion service → verify target identity and artifact → run fixed flash command → verify result and companion handshake → restore supported settings and report anything requiring re-entry. No arbitrary firmware URL/upload, auto-flash on boot, or guessed offsets. If identity is uncertain, stop and require physical identification. Keep a documented bootloader/manual recovery procedure; do not promise automatic rollback of failed ESP32 firmware.

MeshCore messages and contacts remain in the authenticated browser. Its service has no permission or RPC operation for TTS, Asterisk, RF PTT, or APRS announcements.

## 8. Network and 44Net policy

Retain firewalld as the single appliance firewall policy owner. Use explicit private-management, public-IAX and default-drop zones; do not maintain an independent competing nftables ruleset. Assert effective IPv4 and IPv6 rules after reload, network changes, and Tailscale startup. Disable forwarding, masquerading, UPnP and public management forwarding.

| Ingress | Allowed services |
|---|---|
| Approved local management subnet on Ethernet/Wi-Fi | HTTPS; HTTP redirect; mDNS discovery; SSH only if enabled in Imager; necessary DHCP/IPv6 control traffic |
| Approved Tailscale peers | Authenticated HTTPS, optional SSH; restricted by tailnet policy and host policy |
| 44Net interface | Exactly configured AllStar IAX UDP port, default 4569; essential protocol control/established return traffic only |
| Other/unclassified ingress | No application management; necessary network control traffic only |
| Loopback | Private API/AMI/USRP/TLV/vocoder endpoints |

AllStar IAX availability on the ordinary uplink is a separate explicit connection choice for an operator with suitable NAT/forwarding. No automatic router changes. Management rules match ingress interface and approved local source ranges, never just “address looks private”; include IPv6 so global addresses do not bypass the restriction. A new/untrusted network profile starts restricted. Network namespace integration tests must verify that Tailscale-created rules cannot bypass 44Net management restrictions.

The [ASL 44Net guide](https://allstarlink.github.io/adv-topics/44net-connect/) describes full-tunnel routing and an ASL IAX service definition that covers a range. SusNet uses an exact-port rule instead. For v1 retain the portal's supported full-tunnel routing model; do not implement ad hoc split routing. Show that enabling it also changes the IPv4 route for DMR and APRS, then test those services again.

Treat imported WireGuard text as untrusted data. Limit upload to 16 KiB; parse a strict single-interface/single-peer profile; validate key encodings, assigned address, endpoint, port, allowed IPs, MTU and keepalive bounds. Reject duplicate/unknown directives, executable `PreUp/PostUp/PreDown/PostDown` hooks, `SaveConfig`, arbitrary routing-table overrides and unresolved key placeholders. Support only the qualified portal profile and explain incompatible imports. A private-key field is permitted if the portal file contains a placeholder, but portal account/password/API key fields never exist. Import a normalized representation; never execute uploaded text as a script. Keep DNS settings within the supported networking adapter and account for local `.local` resolution separately.

Apply sequence: validate and save → install and verify exact-port firewall zone → arm local rollback timer → start tunnel → verify handshake, assigned-address egress, private-browser return path, DNS and AllStar perceived registration address → check actual inbound IAX with a cooperative external test node → mark tested. Handshake alone is insufficient. External test availability is reported honestly. Tunnel startup waits for firewall readiness on every boot.

Once 44Net is selected as the AllStar path, tunnel failure inhibits AllStar network operation instead of silently advertising a different uplink address. Management remains on LAN; operator may explicitly choose a tested non-44Net path. Unexpected management exposure tears down the tunnel. Do not permit public ports for HTTPS, HTTP, SSH, Cockpit, Allmon, AMI, USRP or MeshCore.

Tailscale enrollment uses an interactive device-auth flow. Do not enable Funnel, exit-node service, subnet routing, or a reusable embedded auth key. Tailnet membership alone does not replace appliance login. Preserve local access if Tailscale expires; exclude its machine identity from portable backups.

## 9. Updates, recovery, export and restore

v1 uses signed, immutable release bundles and controlled configuration migrations. No unattended OS/kernel/ASL/DVSwitch upgrades and no unreviewed apt channel switching. Notify locally when a reviewed release is available. Package security updates are assembled and qualified as a new release; the maintainer guide includes a regular security review and expedited release procedure for relevant vulnerabilities.

For pilot system updates, use the simplest reliable recovery model: encrypted config export → flash a new spare SD with the signed image → complete Imager OS setup → import/validate → qualify devices and enable services. Keep the old SD offline as rollback. Do not run both cards with the same node identities at once. Do not claim atomic full-OS rollback from an ordinary apt upgrade on a single root filesystem. A/B OS updates are deferred. Small configuration changes use the transaction mechanism above; any later in-place application updater needs its own tested package/schema rollback contract.

Default export is a redacted configuration/support bundle, clearly labeled non-restorable for credentials. Full recovery export requires reauthentication and operator-supplied encryption passphrase; use a maintained authenticated-encryption tool/library such as age passphrase mode, not homegrown cryptography. Stream the encrypted result without plaintext files in shared temporary storage. Include schema/release IDs, canonical settings, secrets, calibration binding, and compatible MeshCore settings; optionally include message history. Exclude OS password/shadow data, SSH host keys, TLS private keys, session state, Tailscale identity, logs and build caches.

Restore: bound archive size and expansion; reject traversal, absolute paths, symlinks, hardlinks and unknown payloads; authenticate/decrypt; validate manifest and schema; migrate a copy; show redacted changes; apply through the normal transaction. A restore never copies arbitrary files to `/etc` or runs scripts. Rebind hardware, re-enroll Tailscale, regenerate device TLS/SSH identity, and validate 44Net/network ownership. Imported identities remain inactive until the operator confirms the previous appliance is off. Wrong passphrase, future schema, missing secret, mismatched hardware or failed migration changes nothing.

Recovery entry points: private browser diagnosis when application services fail; authenticated local console/SSH `susnetctl` operations for status, rollback, export and reset; known-good spare SD for filesystem/boot failure. Root reset removes operator configuration and credentials and inhibits all transmit paths; it does not claim forensic erasure of flash storage. Keep recovery documentation printable/offline. Bound journals, message stores and caches; storage exhaustion must reject new transactions before touching the active generation.

## 10. Qualification and pilot acceptance

All criteria below are proposed release gates, not tests already performed. Store results against image hash, package lock, Pi revision, dongle/board revision, USB placement and firmware hash. Synthetic credentials and reserved fixtures are used in CI; operator-owned credentials appear only on the pilot devices and never in test reports.

| Gate | Required evidence/pass condition |
|---|---|
| Locked build | Two clean builds produce matching package/config payloads; full-image comparison and any metadata differences recorded; no unpinned fetches or baked secrets |
| Imager/boot | Tested Imager 2.x on Windows and macOS; hostname, password, locale, Wi-Fi and both SSH choices survive boot/reboot; unique machine/SSH/TLS identities on two cards; setup reachable within 5 minutes on the documented kit with working DHCP |
| Base/ASL | ARM64 Trixie identity, correct kernel/modules, successful Asterisk/app_rpt startup, one public and one private node only, no sample public identity |
| Software DMR | Real Pi 4B bidirectional encode/decode through the full USRP/vocoder/bridge chain, no missing libraries or unapproved ABI substitution; live BM and TGIF authenticated audio tests |
| Hardware RF | Correct kit/port binding; RX/COS/PTT and modulation measured against frozen kit tolerances; startup/reboot/USB removal/fault never causes unintended transmit; 10-second test and 180-second operational timeout checked |
| AllStar reachability | Inbound/outbound calls from a cooperative node outside local LAN/tailnet; registration and perceived IP match selected path; private node inaccessible externally |
| DMR switching | At least 50 alternating BM/TGIF/TG changes, duplicate/concurrent requests, busy channel, wrong password, master outage, static groups and reboot; no simultaneous sessions, wrong-network audio, stale success or unexpected crosslink |
| APRS | Receive-only/verified logins, controlled message send/ACK/reject/expiry, reconnection/deduplication, malformed packet/XSS cases, bounded announcement queue and quiet hours; no RF packet decode/gating |
| MeshCore | Serial discovery, reboot/unplug/replug, ambiguity and wrong device, messages/contacts, supported flash success and interrupted-flash recovery procedure; every message-to-TTS/control attempt rejected |
| Management security | Anonymous/CSRF/Host/Origin/session-expiry tests; broker rejects forged authorization, command/path injection and oversized uploads; staged modes rejected by direct API as well as UI |
| Secrets | Canary secrets absent from journal, daemon logs, support exports, process args, web responses and image; master secrets 0600/root and directories 0700; each service cannot read another's credentials |
| 44Net | Pending/skip/resume, valid import, missing key, malicious hooks, bad endpoint, route/MTU/DNS failure, handshake without reachability, tunnel loss/reboot and browser rollback; external IPv4/IPv6 probes show only intended IAX application port |
| Tailscale coexistence | Before/after enrollment and restart, LAN management works, approved peers work, unapproved peers fail, and no 44Net route reaches management despite injected firewall rules |
| Transactions/recovery | Interrupt at each transaction checkpoint; full disk, daemon-start failure, power loss before/after pointer switch, failed rollback, old-schema restore and wrong passphrase; old valid config or safe recovery state always survives |
| Endurance | 48-hour combined workload on the exact kit, with controlled RF duty cycle, no OOM, repeated crashes, unexplained audio drops, undervoltage or sustained thermal throttling; memory/storage remain bounded |
| Scope | Build and route inventory contains no GMRS feature/feed/default, guest lane, MeshCore-to-TTS capability, personal IDs or personalized favorites; other digital modes remain inactive |

Hardware acceptance must include actual radio measurement and listening checks; a virtual machine or a network login is not enough. Set audio gain/deviation limits from the identified AURSINC/radio kit's specifications and measured baseline, then freeze them before any pilot image is marked accepted.

Pilot rollout: maintainer bench unit → one known operator using only the guide → small invited cohort. Advance only after the preceding stage's blocking defects are resolved. No public beta expansion in v1. Record issues and redacted support bundles with operator consent; no automatic telemetry uploads or remote control enrollment.

## 11. Documentation deliverables

Produce these alongside implementation:

- **Kit card:** exact BOM/revisions, power/cooling/SD, AURSINC details, Heltec US profile, labeled USB photograph, cable/pinout where applicable, antenna/load and recovery notes.
- **Quick start:** verify bundle/hash, import Imager manifest, fill OS settings, boot/wait, find `.local`/DHCP address, certificate trust, sign in, and finish wizard.
- **Credential checklist:** precise distinction between portal logins and service secrets; account approval steps, placeholders, no personal examples; 44Net skip/resume instructions.
- **Operator guide:** AllStar versus DMR behavior, TG entry/favorites, disconnect/busy/error states, APRS messaging and announcements, MeshCore browser-only messaging, disabled modes and status meanings.
- **Private access guide:** LAN/Tailscale scope, no public dashboard ports, firewall checks, 44Net full-tunnel effects and exact inbound IAX test.
- **Recovery guide:** redacted versus encrypted export, spare-card upgrade, restore and hardware rebind, password/hostname/mDNS problems, offline rollback, failed firmware flash, revoke/replace lost credentials.
- **Maintainer guide:** lock/build/sign/rebuild, package ownership, template/schema migration, dependencies and redistribution licenses, feature extraction rules, security updates, qualification scripts and release evidence.
- **Pilot report:** image/version/hash, tested kit/Imager versions, passes/failures and limitations, known issues, rollback version and support contact chosen for the pilot.

## 12. Implementation order and unresolved evidence

1. **Qualification spike:** record exact kit; identify the clean behavioral functions needed from live SusNet without copying secrets; lock a candidate ASL base/Imager pair; prove Trixie software DMR; resolve redistribution of every packaged bridge/vocoder/firmware component. Deliver compatibility/BOM report. Failure blocks pilot release, not a silent change in product scope.
2. **Build foundation:** standalone repository, lock manifest and input mirror, native runner, package skeletons, ASL overlay, sanitized image and Imager manifest. Deliver a bootable unconfigured engineering image with RF inhibited.
3. **Secure setup core:** PAM sessions, privilege-separated broker, schema/renderers, generation journal, firewall, health model, redacted diagnostics. Demonstrate malicious-input rejection and power-loss recovery before enabling radio operations.
4. **Radio and DMR:** kit qualification, public/private node config, vocoder chain, network profiles, safe switching, arbitrary TGs and empty-by-default favorites; staged non-DMR assets. Deliver measured bench acceptance.
5. **APRS and MeshCore:** parity checklist, isolated service adapters, protocol fixtures, announcement restrictions, serial lifecycle and separately confirmed flash path. Deliver feature and exclusion tests.
6. **Connectivity and recovery:** 44Net import/routing/reachability, Tailscale coexistence, encrypted export/restore, spare-card upgrade, complete fault/security tests.
7. **Pilot release:** two clean rebuilds, signed evidence, 48-hour soak, external reachability test, guide-only operator install, then invited distribution.

The remaining unknowns are factual qualification inputs: exact AURSINC/radio revision and calibration; numeric Heltec US profile and pinned firmware; compatible Trixie vocoder/dependency closure and licensing; the tested Imager/base initialization pair; and full APRS behavioral parity details. None is represented as already validated. Their required evidence, fallback behavior and release-blocking consequences are defined above, so implementation does not need to invent product decisions as it proceeds.
