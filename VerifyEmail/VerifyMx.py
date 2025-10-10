import dns.resolver


def verifyMX(domain_lower, dns_timeout):
    try:
        mx_records = dns.resolver.resolve(domain_lower, "MX", lifetime=dns_timeout)
        mx_servers = sorted([r.exchange.to_text().rstrip(".") for r in mx_records])
        if not mx_servers:
            return "invalid", "no_mx_records", None
        return "ok", "mx_ok", mx_servers
    except dns.resolver.NXDOMAIN:
        return "invalid", "domain_not_found", None
    except dns.resolver.NoAnswer:
        return "invalid", "no_mx_records", None
    except dns.resolver.Timeout:
        return "risky", "dns_timeout", None
    except dns.resolver.NoNameservers:
        return "risky", "no_nameservers", None
    except Exception as e:
        return "risky", f"dns_error_{type(e).__name__}", None