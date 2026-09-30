# Accounts and credentials: what you need before setup

SusNet does not come with shared radio accounts. Each operator uses their own
accounts and identifiers. You can finish the basic appliance setup first and
return to optional services later.

Never send these values to a developer or include them in a support bundle.
Enter them only in the SusNet setup wizard on your own appliance.

## Quick checklist

| Feature | What you need | Required? | Where to get it |
|---|---|---:|---|
| Appliance sign-in | The username and password you create in Raspberry Pi Imager | Yes | [Raspberry Pi Imager documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html#installing-the-operating-system) |
| AllStar | AllStarLink account, public node number, and that node's password | For public AllStar | [AllStarLink Portal guide](https://allstarlink.github.io/basics/portal/) |
| DMR identity | Your 7-digit DMR Radio ID and a chosen hotspot suffix | For DMR | [RadioID registration](https://radioid.net/register) |
| BrandMeister | BrandMeister account and Hotspot Security password | For BrandMeister | [Account registration](https://help.brandmeister.network/dashboard/register-for-an-account/) and [Hotspot Security](https://help.brandmeister.network/dashboard/hotspot-security/) |
| TGIF | TGIF account and the network's secure hotspot password | For TGIF | [TGIF account and security help](https://tgif.network/help.php) |
| APRS-IS | Your amateur callsign with an optional SSID; sending also needs an APRS-IS passcode issued through the supported software workflow | For APRS | [Official APRS-IS connection rules](https://www.aprs-is.net/Connecting.aspx) |
| MeshCore | No online account for the local Heltec companion | Optional | [MeshCore documentation](https://meshcore.co.uk/) |
| 44Net | A 44Net Connect account and an approved tunnel configuration | Optional | [44Net Connect user guide](https://connect.44net.cloud/help/) |
| Tailscale | Your own Tailscale account/tailnet | Optional | [Tailscale quickstart](https://tailscale.com/docs/how-to/quickstart) |
| TTS | No external account; the appliance uses a local engine | Optional | Configure it in the SusNet wizard after installation |

## AllStarLink

1. Open the [official AllStarLink Portal guide](https://allstarlink.github.io/basics/portal/).
2. Create an account and complete email and amateur-license verification.
3. In the portal, add a server and request your first node number.
4. Open **Node Settings** and copy the assigned node number and its node
   password into the SusNet wizard.

The website login password and the node password are different values. SusNet
needs the node password for registration; it does not need your portal login
password. The private bridge inside SusNet does not need a second public node
number.

## DMR Radio ID

1. Register at [RadioID](https://radioid.net/register) and complete its amateur
   license verification.
2. Wait for your 7-digit DMR Radio ID to be issued.
3. Enter that ID in SusNet and choose the hotspot suffix offered by the wizard.

Use only an ID assigned to you. A suffix distinguishes multiple hotspots; it
does not create a new Radio ID.

## BrandMeister

1. Obtain your Radio ID first.
2. Follow the [BrandMeister account registration guide](https://help.brandmeister.network/dashboard/register-for-an-account/).
3. Sign in to BrandMeister SelfCare and follow the
   [Hotspot Security guide](https://help.brandmeister.network/dashboard/hotspot-security/).
4. Create a Hotspot Security password for the Radio ID used by SusNet.
5. Enter that Hotspot Security password in SusNet.

Do not enter your BrandMeister website password in the appliance. SusNet needs
the separate Hotspot Security password. If you forget it, replace it in
SelfCare and then update SusNet with the same new value.

## TGIF

Follow the current [TGIF account and security instructions](https://tgif.network/help.php),
verify the account, and create or copy the secure hotspot password described by
the network. Enter the hotspot password in the TGIF section of SusNet. Do not
reuse your TGIF website password unless TGIF's current instructions explicitly
say the generated value is the same one.

BrandMeister and TGIF settings are stored separately. SusNet activates only one
DMR network at a time.

## APRS-IS

Receive-only APRS-IS can use passcode `-1`, as documented by
[APRS-IS](https://www.aprs-is.net/Connecting.aspx). Sending messages or
announcements requires a valid passcode for your callsign. The official rules
say the supported software author supplies that passcode to licensed amateur
operators. Do not use a random passcode website or somebody else's callsign.

The initial SusNet setup can remain receive-only. A released sending feature
must provide its own compliant passcode-request workflow before it is enabled.
APRS announcements are off until you choose a destination and run an explicit
test.

## MeshCore and TTS

The supported Heltec V3 companion is local USB hardware and normally needs no
online account. SusNet verifies its device identity, approved firmware hash,
and US radio profile before enabling it. Firmware flashing is a separate,
physically authorized operation.

TTS runs locally and needs no cloud key. It is disabled by default. It can read
only approved APRS or appliance events with length and rate limits. MeshCore
messages are never routed to TTS in version 1.

## Optional remote networking

For 44Net, create an account and follow the
[44Net Connect guide](https://connect.44net.cloud/help/) to request the needed
resource and tunnel. Import only the tunnel configuration supplied by the
portal.

For Tailscale, follow the [official quickstart](https://tailscale.com/docs/how-to/quickstart)
to create your own tailnet. During SusNet setup, the appliance displays a login
link so you authenticate directly with Tailscale. SusNet does not ask for or
retain your identity-provider password or a reusable enrollment key.

## How SusNet stores secrets

The wizard shows whether a secret is configured but never displays it again.
Blank fields keep the existing value; removing a secret is a separate explicit
action. Secrets are excluded from diagnostics, backups intended for support,
qualification evidence, and logs. A factory reset removes all operator
identities and credentials from the appliance.
