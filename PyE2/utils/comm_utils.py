# -*- coding: utf-8 -*-
"""
Copyright (C) 2017-2021 Andrei Damian, andrei.damian@me.com,  All rights reserved.

This software and its associated documentation are the exclusive property of the creator. 
Unauthorized use, copying, or distribution of this software, or any portion thereof, 
is strictly prohibited.

Parts of this software are licensed and used in software developed by Knowledge Investment Group SRL.
Any software proprietary to Knowledge Investment Group SRL is covered by Romanian and  Foreign Patents, 
patents in process, and are protected by trade secret or copyright law.

Dissemination of this information or reproduction of this material is strictly forbidden unless prior 
written permission from the author.


"""

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
  url = "mqtt.staging2.hyperfy.tech"
  success, ip, original_url = resolve_domain_or_ip(url)
  if not success:
    print(f"Cannot connect to {original_url} (IP: {ip})")
  else:
    print(f"Resolved {original_url} to IP: {ip}")
    