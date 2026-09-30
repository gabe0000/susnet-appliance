# SusNet component scope

The public handoff covers the current design and test contracts for these five
areas. It contains no copied live configuration.

| Area | Current handoff | First proof required |
|---|---|---|
| AllStar | ASL3/Trixie architecture, one public-node template, one private USRP bridge contract | AURSINC identity, wiring, PTT polarity, RX calibration |
| DVSwitch | Analog_Bridge and MMDVM_Bridge topology, synthetic service/config fixtures | Native ARM64 Trixie bridge and software-vocoder test |
| APRS | Synthetic APRS-IS messages, receive/message/announcement boundary | Parser, reconnect, queue, and explicit announcement tests |
| MeshCore | Synthetic companion messages and Heltec V3 USB identity | Approved US-profile firmware hash and serial recovery test |
| TTS | Synthetic announcement fixture and route policy | Offline engine choice, pronunciation, queue, ducking, and timeout test |

TTS may announce explicitly enabled APRS or appliance events. MeshCore messages
never feed TTS in v1. All announcements are off by default and have bounded
length, rate, destination, and interruption behavior.

Experiments, website material, operator favorites, personal identities, and
machine-specific configuration are excluded from the handoff.
