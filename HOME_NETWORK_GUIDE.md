# Home Network: Accessing Any Machine By Name

You want to hit `http://girlfriends-mac:8765` from any device on your network
instead of messing with IP addresses like `192.168.1.42`. Here's how.

---

## The Problem

Every device on your home network gets an IP address (like `192.168.1.42`).
These can change whenever your router feels like it. Typing them is annoying
and they're impossible to remember.

## The Solution: Three options, from easiest to most complete.

---

## Option 1: .local (mDNS) -- Zero Setup on Macs

**This already works between Apple devices.** No setup needed.

Every Mac broadcasts its name on the local network using a protocol called mDNS
(Bonjour). You can reach any Mac by its hostname + `.local`.

### Find the Mac's local hostname:

On the Mac running Breathwork, open **System Settings** > **General** > **Sharing**.

Look for **Local hostname** at the bottom. It'll say something like:

```
Ranas-MacBook-Pro.local
```

### Use it:

From any device on the same WiFi, open a browser and go to:

```
http://Ranas-MacBook-Pro.local:8765
```

That's it. This works from:
- Other Macs (always works)
- iPhones/iPads (always works)
- Linux machines (usually works -- see note below)
- Windows (usually works if Bonjour/iTunes is installed)

### Rename it to something nice:

1. Open **System Settings** > **General** > **Sharing**
2. Click **Edit** next to the local hostname
3. Change it to something like `breathwork`
4. Now the address is: `http://breathwork.local:8765`

### Linux Note:

Most modern Linux distros support mDNS out of the box via `avahi`.
If `.local` addresses don't work on your Linux box, install it:

```bash
# Ubuntu/Debian
sudo apt install avahi-daemon libnss-mdns

# Fedora
sudo dnf install avahi nss-mdns

# Arch
sudo pacman -S avahi nss-mdns
```

Then restart: `sudo systemctl restart avahi-daemon`

After that, `.local` addresses work from Linux too.

---

## Option 2: Static IP + Router Hostname -- Reliable, Moderate Effort

If you want the IP to never change (even after router reboots), assign a
static (fixed) IP to the Mac running Breathwork.

### Step 1: Log into your router

1. Open a browser and go to `192.168.1.1` (or `192.168.0.1` -- check sticker
   on your router)
2. Log in (username/password is usually on the router sticker too. Common
   defaults: admin/admin, admin/password)

### Step 2: Find "DHCP Reservation" or "Static Lease"

Different routers call it different things:
- **DHCP Reservation** (most common)
- **Address Reservation**
- **Static Lease**
- **Fixed IP Assignment**

It'll be under LAN Settings, DHCP, or Network.

### Step 3: Reserve an IP for the Mac

1. Find the Mac in the list of connected devices
2. Assign it a fixed IP, e.g., `192.168.1.100`
3. Save

Now the Mac always gets `192.168.1.100`, and you can reliably use:

```
http://192.168.1.100:8765
```

### Bonus: Some routers let you assign local hostnames

Higher-end routers (Unifi, pfSense, OpenWrt, some Netgear/Asus) let you
assign DNS names to devices. If yours supports it, you can set
`breathwork.home` or similar, and all devices on the network can use it.

---

## Option 3: Pi-hole or Local DNS -- Most Powerful, Most Work

If you want total control over naming on your network, run a local DNS server.
The most popular option is **Pi-hole** (which also blocks ads).

### What you need:

- A Raspberry Pi (any model, ~$35), OR any always-on Linux machine
- An SD card + power supply for the Pi

### Setup:

1. Install Pi-hole:

```bash
curl -sSL https://install.pi-hole.net | bash
```

2. In the Pi-hole admin panel (`http://pi.hole/admin`), go to
   **Local DNS** > **DNS Records**

3. Add a record:

```
Domain:  breathwork.home
IP:      192.168.1.100     (the Mac's static IP from Option 2)
```

4. Point your router's DNS to the Pi-hole's IP address
   (Router settings > WAN/Internet > DNS > set to Pi-hole's IP)

Now every device on your network can use:

```
http://breathwork.home:8765
```

### Why Pi-hole is worth it (even beyond this project):

- Blocks ads on every device on your network (phones, smart TVs, everything)
- You get nice custom local domain names
- Pi-holes are fun weekend projects

---

## My Recommendation

**Start with Option 1 (.local).** It already works on Macs and iPhones with
zero effort. Rename the hostname to `breathwork` and use
`http://breathwork.local:8765` from everything.

If you find `.local` unreliable or want it cleaner, do Option 2 (static IP)
as a fallback.

Option 3 is for when you catch the networking bug and want to go further.

---

## Quick Reference

| Method | Address | Works from | Setup |
|--------|---------|------------|-------|
| .local (mDNS) | `http://breathwork.local:8765` | Mac, iPhone, Linux (with avahi) | Rename hostname only |
| Static IP | `http://192.168.1.100:8765` | Everything | Router config |
| Pi-hole DNS | `http://breathwork.home:8765` | Everything | Pi-hole + Router DNS |
| Localhost | `http://localhost:8765` | Same machine only | None |
