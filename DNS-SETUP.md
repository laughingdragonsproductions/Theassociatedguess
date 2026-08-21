# DNS setup for theassociatedguess.com (GitHub Pages)

GitHub shows **NotServedByPagesError** because the domain is registered on Cloudflare but has **no records pointing at GitHub**.

## Cloudflare — add these records

Open [Cloudflare DNS](https://dash.cloudflare.com) → **theassociatedguess.com** → **DNS** → **Records**.

Delete any old `@` or `www` records that point elsewhere (parking page, wrong host, etc.).

### Apex (`theassociatedguess.com`)

**Option A — recommended on Cloudflare**

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | `@` | `laughingdragonsproductions.github.io` | **DNS only** (grey cloud) |

**Option B — A records (also valid)**

Add four **A** records, name `@`, proxy **DNS only**:

- `185.199.108.153`
- `185.199.109.153`
- `185.199.110.153`
- `185.199.111.153`

### WWW

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | `www` | `laughingdragonsproductions.github.io` | **DNS only** (grey cloud) |

**Important:** Target is `laughingdragonsproductions.github.io` — **not** `/Theassociatedguess`.

## After saving DNS

1. Wait **5–30 minutes** (sometimes up to a few hours).
2. GitHub → **Settings → Pages** → click **Check again** on the custom domain.
3. When the DNS check passes, enable **Enforce HTTPS**.

## Verify from your PC

```powershell
Resolve-DnsName theassociatedguess.com -Type A
Resolve-DnsName www.theassociatedguess.com -Type CNAME
```

You should see GitHub IPs (A) or a CNAME to `laughingdragonsproductions.github.io`.

## Until DNS works

The site is hosted on GitHub but redirects to your custom domain, so the URL will fail until DNS resolves. Local preview always works:

http://localhost:8081/
