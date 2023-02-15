from urllib.parse import urlsplit

# https://stackoverflow.com/a/43323540/9878135


def get_domain(url):
    u = urlsplit(url)
    return u.netloc


def get_top_domain(url):
    u"""
    >>> get_top_domain('http://www.google.com')
    'google.com'
    >>> get_top_domain('http://www.sina.com.cn')
    'sina.com.cn'
    >>> get_top_domain('http://bbc.co.uk')
    'bbc.co.uk'
    >>> get_top_domain('http://mail.cs.buaa.edu.cn')
    'buaa.edu.cn'
    """
    domain = get_domain(url)
    domain_parts = domain.split('.')
    if len(domain_parts) < 2:
        return domain
    top_domain_parts = 2
    # if a domain's last part is 2 letter long, it must be country name
    if len(domain_parts[-1]) == 2:
        if domain_parts[-1] in ['uk', 'jp']:
            if domain_parts[-2] in ['co', 'ac', 'me', 'gov', 'org', 'net']:
                top_domain_parts = 3
        else:
            if domain_parts[-2] in ['com', 'org', 'net', 'edu', 'gov']:
                top_domain_parts = 3
    return '.'.join(domain_parts[-top_domain_parts:])
