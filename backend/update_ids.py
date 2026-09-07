import re

with open("app/utils/seed_reels.py", "r") as f:
    content = f.read()

ids = ['1aym_5bE7Z8', 'keR7KUyQ2qQ', 'sMYyz3WeL18', 'oeCIcV_QhHU', 'EATsj7__fVw', 'OzmCRNRk9ME', 'i5otDylcbY8', 'uDhhd4tY7KE', 'HIAB8zQoYDQ', 'IUQvq2oRM1w', '3CBZI7QXIVQ', '4IgetiIp8Pk', 'OlpMLSpNjfI', 'M2mNc9I7IAE', 'wvnXL_ycTXQ', 'TVQWGGsSQoI', '6wIjS64lrHM', '8a41lbQ2JCU', 'O27nLt1BRa8', 'Fkc7XBP8EiA', 'DcSSt27eGPE', 'uqAIsUowyCI', 'qZ-rT0A7MgM', 'VQ2CXvwuIPA', 'AHopU8qMfNM', 'm5cYzzHjjKA', 'J6bSPGorLsA', 'gCr8DBywINw', 'c6WcA_UGHcQ', '5CJFSY5HwYk', '6Gl0y3IpyhY', 'carsYXPsaUM', 'f4ucK6AUONg', 'qRRr00lgI2g', 'j6hv7Jcm5XQ', 'lVfNStAU178', 'TD-c7yRkEWI', 'eK0sZELRsrY', 'DqllbSMphXQ', 'EQLhVOJedMw', 'ehcVE5tIGS8', 'JD6AChPiDss', 'gZA5yW6Y-VI', 'ni_HSCBqDlM', '0so5OhA6k7k', 'eqxk2rVPbdA', 'UXSsqiLCqkE', 'zPxQjuFoUBc', 'UV5MmScWe0A', 'wUIoYL6IKT4', 'kQdasMB4bwc', 'S_KPTWmP0HQ', 'mqQDgm2qYQo', 'wNao2A9I9yY', '4Fo_Uybhtlc', 'qgwHxIXuyvQ', 'Q46S5BfashM', '80gjqMmqM4A', 'U49c3ebnC6E', 'xs9tsX8riBk']

new_content = ""
id_idx = 0
for line in content.splitlines():
    if '"https://youtube.com/shorts/' in line:
        line = re.sub(r'"https://youtube.com/shorts/[^"]+"', f'"https://youtube.com/shorts/{ids[id_idx]}"', line)
        id_idx += 1
    new_content += line + "\n"

with open("app/utils/seed_reels.py", "w") as f:
    f.write(new_content)
