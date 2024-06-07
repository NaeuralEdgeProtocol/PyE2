import socket
from ipaddress import ip_address, AddressValueError

def resolve_domain_or_ip(url):
  """Resolves a domain name to its IP address or verifies an IP address.

  Parameters
  ----------
  url : str
      The domain name or IP address.

  Returns
  -------
  tuple: (bool, str, str)
      <success>, <ip>, <original_url>
      A tuple containing a boolean indicating if the resolution was successful,
      a string with the resolved or verified IP address, and the original URL.
  """
  try:
    # Check if the URL is an IP address
    ip_address(url)
    return True, url, url
  except:
    pass

  try:
    # Try to resolve the domain name to an IP address
    ip_of_url = socket.gethostbyname(url)
    return True, ip_of_url, url
  except:
    return False, None, url
  
  
  

if __name__ == '__main__':
  # Usage:
  url = "r9092118.ala.eu-central-1.emqxsl.com"
  success, ip, original_url = resolve_domain_or_ip(url)
  if not success:
    print(f"Cannot connect to {original_url} (IP: {ip})")
  else:
    print(f"Resolved {original_url} to IP: {ip}")
    